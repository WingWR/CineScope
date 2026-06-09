from __future__ import annotations

import pandas as pd

from ...modules.stats.repository import StatsRepository
from ...modules.stats.schemas import (
    AtlasSummary,
    BudgetTrendPoint,
    CorrelationCell,
    GenreDistributionItem,
    RevenueBudgetPoint,
)


SCATTER_POINT_LIMIT = 160
TREND_YEAR_START = 1970
TREND_YEAR_END = 2020
CORRELATION_FIELDS = {
    "Budget": "budget",
    "Revenue": "revenue",
    "Rating": "rating_mean",
    "Popularity": "tmdb_popularity",
}


class StatsService:
    def __init__(self, repository: StatsRepository | None = None) -> None:
        self.repository = repository or StatsRepository()

    def get_summary(self) -> AtlasSummary:
        payload = self.repository.load_summary()
        return AtlasSummary(
            dataset=payload.get("dataset"),
            movieCount=_as_int(payload.get("movie_count")),
            userCount=_as_int(payload.get("user_count")),
            ratingCount=_as_int(payload.get("rating_count")),
            tagCount=_as_int(payload.get("tag_count")),
            genreCount=_as_int(payload.get("genre_count")),
            ratingMean=_as_float(payload.get("rating_mean")),
        )

    def get_genres(self) -> list[GenreDistributionItem]:
        records = sorted(
            self.repository.load_genres(),
            key=lambda record: int(record.get("movie_count", 0)),
            reverse=True,
        )
        return [
            GenreDistributionItem(
                genre=str(record.get("genre", "")),
                count=int(record.get("movie_count", 0)),
            )
            for record in records
            if str(record.get("genre", "")).strip()
        ]

    def get_budget_trend(self) -> list[BudgetTrendPoint]:
        frame = self.repository.load_movies()
        filtered = frame[
            frame["movie_year"].notna()
            & frame["budget"].notna()
            & (frame["budget"] > 0)
            & (frame["movie_year"] >= TREND_YEAR_START)
            & (frame["movie_year"] <= TREND_YEAR_END)
        ].copy()
        if filtered.empty:
            return []

        filtered["year"] = filtered["movie_year"].astype(int)
        aggregated = (
            filtered.groupby("year", as_index=False)["budget"]
            .mean()
            .sort_values("year")
        )
        return [
            BudgetTrendPoint(
                year=int(record.year),
                budget=round(float(record.budget), 2),
            )
            for record in aggregated.itertuples(index=False)
        ]

    def get_revenue_budget(self) -> list[RevenueBudgetPoint]:
        frame = self.repository.load_movies()
        filtered = frame[
            frame["budget"].notna()
            & frame["revenue"].notna()
            & (frame["budget"] > 0)
            & (frame["revenue"] > 0)
        ].copy()
        if filtered.empty:
            return []

        filtered = filtered.sort_values(
            ["tmdb_popularity", "revenue", "budget"],
            ascending=[False, False, False],
            na_position="last",
        ).head(SCATTER_POINT_LIMIT)
        return [
            RevenueBudgetPoint(
                title=str(record.title_clean),
                budget=round(float(record.budget), 2),
                revenue=round(float(record.revenue), 2),
                popularity=_as_float(record.tmdb_popularity),
            )
            for record in filtered.itertuples(index=False)
            if str(record.title_clean).strip()
        ]

    def get_correlations(self) -> list[CorrelationCell]:
        frame = self.repository.load_movies()
        correlation_frame = frame[list(CORRELATION_FIELDS.values())].copy()
        correlation_frame = correlation_frame.dropna()
        correlation_frame = correlation_frame[
            (correlation_frame["budget"] > 0)
            & (correlation_frame["revenue"] > 0)
        ]
        if correlation_frame.empty:
            return []

        matrix = (
            correlation_frame.corr(method="pearson")
            .abs()
            .clip(lower=0, upper=1)
            .fillna(0)
        )

        labels = list(CORRELATION_FIELDS.keys())
        items: list[CorrelationCell] = []
        for row_index, row_label in enumerate(labels):
            for column_label in labels[row_index + 1 :]:
                row_key = CORRELATION_FIELDS[row_label]
                column_key = CORRELATION_FIELDS[column_label]
                items.append(
                    CorrelationCell(
                        x=column_label,
                        y=row_label,
                        value=round(float(matrix.loc[row_key, column_key]), 4),
                    )
                )
        return items


def _as_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _as_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(float(value))


def get_stats_service() -> StatsService:
    return StatsService()
