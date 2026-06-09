from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from ...modules.movies.repository import MovieRepository
from ...modules.movies.mappers import movie_record_to_schema
from ...modules.movies.schemas import Movie, MovieListResponse, MovieSort
from ...shared.text_utils import normalize_text


DEFAULT_MOVIE_LIMIT = 60


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
    ) -> MovieListResponse:
        records = self.repository.list_records()
        filtered = [
            record
            for record in records
            if self._matches_search(record, search)
            and self._matches_genre(record, genre)
            and self._matches_language(record, language)
            and self._matches_rating(record, min_rating)
        ]
        filtered = self._sort_records(filtered, sort or "popularity")
        return MovieListResponse(
            items=[movie_record_to_schema(record) for record in filtered[:DEFAULT_MOVIE_LIMIT]],
            total=len(filtered),
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
        wanted = normalize_text(language).lower()
        if not wanted:
            return True
        return str(record.get("_language_norm", "")) == wanted

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
