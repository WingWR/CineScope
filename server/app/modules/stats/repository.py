from __future__ import annotations

from server.app.core.errors import not_implemented


class StatsRepository:
    def load_summary(self):
        not_implemented("stats.repository", "load_summary")

    def load_genres(self):
        not_implemented("stats.repository", "load_genres")

    def load_movies(self):
        not_implemented("stats.repository", "load_movies")
