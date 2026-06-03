from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from server.app.modules.movies.schemas import Movie, MovieListResponse, MovieSort
from server.app.modules.movies.service import MovieService, get_movie_service


router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    search: str | None = Query(None),
    genre: str | None = Query(None),
    language: str | None = Query(None),
    minRating: float | None = Query(None, ge=0, le=5),
    sort: MovieSort | None = Query(None),
    service: MovieService = Depends(get_movie_service),
) -> MovieListResponse:
    return service.list_movies(
        search=search,
        genre=genre,
        language=language,
        min_rating=minRating,
        sort=sort,
    )


@router.get("/{movieId}", response_model=Movie)
def get_movie(
    movieId: str,
    service: MovieService = Depends(get_movie_service),
) -> Movie:
    return service.get_movie(movieId)
