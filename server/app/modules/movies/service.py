from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.movies.repository import MovieRepository
from server.app.modules.movies.schemas import Movie, MovieListResponse, MovieSort


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
        not_implemented("movies.service", "list_movies")

    def get_movie(self, movie_id: int | str) -> Movie:
        not_implemented("movies.service", "get_movie")


def get_movie_service() -> MovieService:
    return MovieService()
