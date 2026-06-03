from __future__ import annotations

from server.app.core.errors import not_implemented


class MovieRepository:
    def list_records(self):
        not_implemented("movies.repository", "list_records")

    def get_record_by_id(self, movie_id: int | str):
        not_implemented("movies.repository", "get_record_by_id")
