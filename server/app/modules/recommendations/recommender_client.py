from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit

import httpx
from fastapi import HTTPException

from ...core.config import get_config
from ...shared.text_utils import normalize_text


DEFAULT_NEIGHBOR_K = 10
REQUEST_TIMEOUT_SECONDS = 8.0
LOCAL_RECOMMENDER_PORTS = (3000,)


@dataclass(frozen=True)
class _RequestFailure:
    status_code: int
    detail: str


class RecommenderClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = _normalize_base_url(base_url or get_config().recommender_base_url)
        self._allow_local_fallback = base_url is None

    def recommend_content(self, movie_name: str, top_k: int) -> list[dict[str, Any]]:
        movie_name = normalize_text(movie_name)
        if not movie_name:
            raise HTTPException(status_code=400, detail="seedMovieName is required for content mode.")
        payload = self._get(
            "/recommend/content",
            params={
                "movie_name": movie_name,
                "top_k": top_k,
            },
        )
        return self._extract_items(payload)

    def recommend_collaborative(
        self,
        user_id: int,
        movie_name: str | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        if user_id < 1:
            raise HTTPException(status_code=400, detail="userId must be a positive integer.")

        params: dict[str, Any] = {
            "user_id": user_id,
            "top_k": top_k,
            "neighbor_k": DEFAULT_NEIGHBOR_K,
        }
        movie_name = normalize_text(movie_name)
        if movie_name:
            params["movie_name"] = movie_name

        payload = self._get("/recommend/collaborative", params=params)
        return self._extract_items(payload)

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        failures: list[_RequestFailure] = []
        candidate_urls = self._candidate_base_urls()

        for index, base_url in enumerate(candidate_urls):
            is_last_candidate = index == len(candidate_urls) - 1
            try:
                with httpx.Client(
                    base_url=base_url,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    trust_env=False,
                ) as client:
                    response = client.get(path, params=params)
            except httpx.TimeoutException:
                failure = _RequestFailure(
                    status_code=503,
                    detail=_format_transport_failure(
                        message="timed out",
                        base_url=base_url,
                        path=path,
                        params=params,
                    ),
                )
                failures.append(failure)
                if is_last_candidate:
                    raise HTTPException(status_code=failure.status_code, detail=failure.detail) from None
                continue
            except httpx.RequestError as exc:
                failure = _RequestFailure(
                    status_code=503,
                    detail=_format_transport_failure(
                        message=str(exc),
                        base_url=base_url,
                        path=path,
                        params=params,
                    ),
                )
                failures.append(failure)
                if is_last_candidate:
                    raise HTTPException(status_code=failure.status_code, detail=failure.detail) from exc
                continue

            if response.is_success:
                try:
                    payload = response.json()
                except ValueError:
                    failure = _RequestFailure(
                        status_code=502,
                        detail=_format_response_failure(
                            base_url=base_url,
                            path=path,
                            params=params,
                            response=response,
                            extra="invalid JSON",
                        ),
                    )
                    failures.append(failure)
                    if is_last_candidate:
                        raise HTTPException(status_code=failure.status_code, detail=failure.detail) from None
                    continue

                if not isinstance(payload, dict):
                    failure = _RequestFailure(
                        status_code=502,
                        detail=_format_response_failure(
                            base_url=base_url,
                            path=path,
                            params=params,
                            response=response,
                            extra="invalid payload type",
                        ),
                    )
                    failures.append(failure)
                    if is_last_candidate:
                        raise HTTPException(status_code=failure.status_code, detail=failure.detail) from None
                    continue
                return payload

            detail = _format_response_failure(
                base_url=base_url,
                path=path,
                params=params,
                response=response,
            )
            should_retry = self._allow_local_fallback and not is_last_candidate and _should_try_next_candidate(response)
            if should_retry:
                failures.append(_RequestFailure(status_code=_map_error_status(response.status_code), detail=detail))
                continue

            raise HTTPException(
                status_code=_map_error_status(response.status_code),
                detail=detail,
            )

        last_failure = failures[-1] if failures else _RequestFailure(503, "Recommender service is unavailable.")
        raise HTTPException(status_code=last_failure.status_code, detail=last_failure.detail)

    def _candidate_base_urls(self) -> list[str]:
        candidates = [self.base_url]
        if not self._allow_local_fallback:
            return candidates

        parsed = urlsplit(self.base_url)
        hostname = (parsed.hostname or "").lower()
        port = parsed.port
        if hostname not in {"127.0.0.1", "localhost"} or port not in LOCAL_RECOMMENDER_PORTS:
            return candidates

        for candidate_port in LOCAL_RECOMMENDER_PORTS:
            if candidate_port == port:
                continue
            candidate_url = _replace_port(parsed, candidate_port)
            if candidate_url not in candidates:
                candidates.append(candidate_url)
        return candidates

    @staticmethod
    def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise HTTPException(status_code=502, detail="Recommender service returned malformed items.")
        return [item for item in items if isinstance(item, dict)]


def _normalize_base_url(value: str) -> str:
    text = normalize_text(value).rstrip("/")
    return text or "http://127.0.0.1:3000"


def _replace_port(parsed: SplitResult, port: int) -> str:
    hostname = parsed.hostname or "127.0.0.1"
    netloc = hostname if port in {80, 443} else f"{hostname}:{port}"
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth += f":{parsed.password}"
        netloc = f"{auth}@{netloc}"
    return urlunsplit((parsed.scheme or "http", netloc, parsed.path, parsed.query, parsed.fragment)).rstrip("/")


def _should_try_next_candidate(response: httpx.Response) -> bool:
    if response.status_code >= 500 or response.status_code == 405:
        return True
    if response.status_code != 404:
        return False
    detail = normalize_text(_extract_error_message(response)).lower()
    return detail in {"", "not found"}


def _map_error_status(status_code: int) -> int:
    if status_code in {400, 404, 503}:
        return status_code
    return 502


def _format_transport_failure(
    *,
    message: str,
    base_url: str,
    path: str,
    params: dict[str, Any],
) -> str:
    return (
        f"Recommender request failed: GET {base_url}{path} "
        f"params={params} error={normalize_text(message)[:500]}"
    )


def _format_response_failure(
    *,
    base_url: str,
    path: str,
    params: dict[str, Any],
    response: httpx.Response,
    extra: str | None = None,
) -> str:
    detail = _extract_error_message(response)
    preview = normalize_text(response.text).replace("\r", " ").replace("\n", " ")[:500]
    suffix = f" extra={extra};" if extra else ""
    return (
        f"Recommender request failed: GET {base_url}{path} params={params} "
        f"status={response.status_code};{suffix} detail={detail}; body={preview}"
    )


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message
    return f"HTTP {response.status_code}"
