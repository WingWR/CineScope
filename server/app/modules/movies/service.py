from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException

from ...modules.movies.repository import MovieRepository
from ...modules.movies.mappers import movie_record_to_schema
from ...modules.movies.schemas import Movie, MovieListResponse, MovieSort
from ...shared.text_utils import normalize_text


DEFAULT_MOVIE_PAGE_SIZE = 25
MAX_MOVIE_PAGE_SIZE = 60

LANGUAGE_ALIASES: dict[str, set[str]] = {
    "en": {"en", "eng", "english"},
    "fr": {"fr", "fra", "fre", "french", "francais", "français"},
    "ja": {"ja", "jpn", "jp", "japanese"},
    "it": {"it", "ita", "italian"},
    "ru": {"ru", "rus", "russian"},
    "de": {"de", "deu", "ger", "german", "deutsch"},
    "es": {"es", "spa", "spanish", "espanol", "español"},
    "zh": {"zh", "zho", "chi", "chinese", "mandarin", "putonghua", "中文", "汉语", "普通话"},
    "cn": {"cn", "cantonese", "yue", "粤语"},
    "ko": {"ko", "kor", "korean"},
    "da": {"da", "dan", "danish"},
    "sv": {"sv", "swe", "swedish"},
    "pt": {"pt", "por", "portuguese"},
    "fi": {"fi", "fin", "finnish"},
    "hi": {"hi", "hin", "hindi"},
    "nl": {"nl", "dut", "nld", "dutch"},
    "cs": {"cs", "ces", "cze", "czech"},
    "fa": {"fa", "fas", "per", "persian", "farsi"},
    "pl": {"pl", "pol", "polish"},
    "no": {"no", "nor", "norwegian"},
    "he": {"he", "heb", "hebrew"},
    "th": {"th", "tha", "thai"},
    "tr": {"tr", "tur", "turkish"},
}

LANGUAGE_LOOKUP: dict[str, set[str]] = {}
for code, aliases in LANGUAGE_ALIASES.items():
    LANGUAGE_LOOKUP.setdefault(code, set()).add(code)
    for alias in aliases:
        LANGUAGE_LOOKUP.setdefault(alias, set()).add(code)


class MovieService:
    def __init__(self, repository: MovieRepository | None = None) -> None:
        self.repository = repository or MovieRepository()

    def list_movies(
        self,
        search: str | None = None,
        genre: str | None = None,
        language: str | None = None,
        min_rating: float | None = None,
        sort: MovieSort | None = None,
        page: int = 1,
        page_size: int = DEFAULT_MOVIE_PAGE_SIZE,
    ) -> MovieListResponse:
        records = self.repository.list_records()
        requested_page = max(1, int(page or 1))
        requested_page_size = min(MAX_MOVIE_PAGE_SIZE, max(1, int(page_size or DEFAULT_MOVIE_PAGE_SIZE)))
        filtered = [
            record
            for record in records
            if self._matches_search(record, search)
            and self._matches_genre(record, genre)
            and self._matches_language(record, language)
            and self._matches_rating(record, min_rating)
        ]
        filtered = self._sort_records(filtered, sort or "popularity")
        total = len(filtered)
        max_page = max(1, (total + requested_page_size - 1) // requested_page_size)
        current_page = min(requested_page, max_page)
        start = (current_page - 1) * requested_page_size
        end = start + requested_page_size
        return MovieListResponse(
            items=[movie_record_to_schema(record) for record in filtered[start:end]],
            total=total,
            page=current_page,
            pageSize=requested_page_size,
        )

    def get_movie(self, movie_id: int | str) -> Movie:
        record = self.repository.get_record_by_id(movie_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Movie not found: {movie_id}")
        return movie_record_to_schema(record)

    @staticmethod
    def _matches_search(record: dict[str, Any], search: str | None) -> bool:
        query = normalize_text(search).lower()
        if not query:
            return True
        return query in str(record.get("_search_blob", ""))

    @staticmethod
    def _matches_genre(record: dict[str, Any], genre: str | None) -> bool:
        wanted = normalize_text(genre).lower()
        if not wanted:
            return True
        return any(normalize_text(item).lower() == wanted for item in record.get("genres", []))

    @staticmethod
    def _matches_language(record: dict[str, Any], language: str | None) -> bool:
        wanted_codes = _language_codes(language)
        if not wanted_codes:
            return True
        return str(record.get("_language_norm", "")).lower() in wanted_codes

    @staticmethod
    def _matches_rating(record: dict[str, Any], min_rating: float | None) -> bool:
        if min_rating is None:
            return True
        rating = record.get("rating_mean")
        return rating is not None and float(rating) >= min_rating

    def _sort_records(
        self,
        records: list[dict[str, Any]],
        sort: MovieSort,
    ) -> list[dict[str, Any]]:
        if sort == "rating":
            return sorted(
                records,
                key=lambda record: (
                    self._as_float(record.get("rating_mean")),
                    self._as_float(record.get("rating_count")),
                    self._as_float(record.get("tmdb_popularity")),
                ),
                reverse=True,
            )
        if sort == "revenue":
            return sorted(
                records,
                key=lambda record: (
                    self._as_float(record.get("revenue")),
                    self._as_float(record.get("tmdb_popularity")),
                ),
                reverse=True,
            )
        if sort == "year":
            return sorted(
                records,
                key=lambda record: (
                    self._as_float(record.get("movie_year")),
                    self._as_float(record.get("tmdb_popularity")),
                ),
                reverse=True,
            )
        return sorted(
            records,
            key=lambda record: (
                self._as_float(record.get("tmdb_popularity")),
                self._as_float(record.get("rating_mean")),
                self._as_float(record.get("rating_count")),
            ),
            reverse=True,
        )

    @staticmethod
    def _as_float(value: Any) -> float:
        if value is None:
            return float("-inf")
        try:
            value = float(value)
        except (TypeError, ValueError):
            return float("-inf")
        return value


def get_movie_service() -> MovieService:
    return MovieService()


def _language_codes(language: str | None) -> set[str]:
    normalized = normalize_text(language).lower()
    if not normalized:
        return set()

    tokens = {normalized}
    tokens.update(token for token in re.split(r"[\s,/|;:_-]+", normalized) if token)

    codes: set[str] = set()
    for token in tokens:
        matches = LANGUAGE_LOOKUP.get(token)
        if matches:
            codes.update(matches)
        elif len(token) <= 3:
            codes.add(token)
    return codes
