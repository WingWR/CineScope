from __future__ import annotations

from typing import Any

from server.app.modules.movies.schemas import Movie


def movie_record_to_schema(record: dict[str, Any]) -> Movie:
    raise NotImplementedError("Movie record mapping is not implemented yet.")
