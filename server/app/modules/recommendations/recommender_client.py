from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException

from ...core.config import get_config
from ...shared.text_utils import normalize_text


REQUEST_TIMEOUT_SECONDS = 8.0


class RecommenderClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or get_config().recommender_base_url

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
        }
        movie_name = normalize_text(movie_name)
        if movie_name:
            params["movie_name"] = movie_name

        payload = self._get("/recommend/collaborative", params=params)
        return self._extract_items(payload)

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(base_url=self.base_url, timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = client.get(path, params=params)
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=503, detail="Recommender service timed out.") from exc
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail="Recommender service is unavailable.") from exc

        if response.status_code in {400, 404, 503}:
            raise HTTPException(
                status_code=response.status_code,
                detail=_extract_error_message(response),
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail="Recommender service returned an unexpected error.") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="Recommender service returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise HTTPException(status_code=502, detail="Recommender service returned an invalid payload.")
        return payload

    @staticmethod
    def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise HTTPException(status_code=502, detail="Recommender service returned malformed items.")
        return [item for item in items if isinstance(item, dict)]


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"Recommender service returned HTTP {response.status_code}."

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message
    return f"Recommender service returned HTTP {response.status_code}."
