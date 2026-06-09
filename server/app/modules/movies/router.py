from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...modules.movies.schemas import Movie, MovieListResponse, MovieSort
from ...modules.movies.service import MovieService, get_movie_service


router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    search: str | None = Query(None),
    genre: str | None = Query(None),
    language: str | None = Query(None),
    minRating: float | None = Query(None, ge=0, le=5),
    sort: MovieSort | None = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(25, ge=1, le=60),
    service: MovieService = Depends(get_movie_service),
) -> MovieListResponse:
    return service.list_movies(
        search=search,
        genre=genre,
        language=language,
        min_rating=minRating,
        sort=sort,
        page=page,
        page_size=pageSize,
    )


@router.get("/{movieId}", response_model=Movie)
def get_movie(
    movieId: str,
    service: MovieService = Depends(get_movie_service),
) -> Movie:
    return service.get_movie(movieId)
