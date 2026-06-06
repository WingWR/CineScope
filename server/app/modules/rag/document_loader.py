from __future__ import annotations

from typing import Any

import pandas as pd

from server.app.core.paths import DATASET_SUMMARY_FILE, DOCS_DATA_DIR, GENRE_STATS_FILE, MOVIES_FILE, QUALITY_REPORT_FILE
from server.app.modules.rag.models import RagDocument
from server.app.shared.csv_loader import load_csv
from server.app.shared.json_loader import load_json
from server.app.shared.text_utils import normalize_text, parse_json_list


POPULARITY_PROFILE_LIMIT = 3000
RANKING_LIMIT = 50
GENRE_RANKING_LIMIT = 20


class RagDocumentLoader:
    def load_documents(self, source_names: list[str] | None = None) -> list[RagDocument]:
        documents = [
            *self._load_dataset_summary(),
            *self._load_quality_report(),
            *self._load_genre_distribution(),
            *self._load_movie_profiles(),
            *self._load_movie_rankings(),
            *self._load_markdown_docs(),
        ]
        if not source_names:
            return documents

        allowed = {name.strip().lower() for name in source_names if name and name.strip()}
        if not allowed:
            return documents

        return [
            document
            for document in documents
            if document.source_id.lower() in allowed
            or document.source_name.lower() in allowed
            or document.id.lower() in allowed
        ]

    def _load_dataset_summary(self) -> list[RagDocument]:
        if not DATASET_SUMMARY_FILE.exists():
            return []

        payload = load_json(DATASET_SUMMARY_FILE)
        lines = [
            f"Dataset: {payload.get('dataset', 'unknown')}",
            "Summary:",
            f"Movie count: {payload.get('movie_count', 'unknown')}",
            f"User count: {payload.get('user_count', 'unknown')}",
            f"Rating count: {payload.get('rating_count', 'unknown')}",
            f"Tag count: {payload.get('tag_count', 'unknown')}",
            f"Genre count: {payload.get('genre_count', 'unknown')}",
            f"Average rating: {_format_decimal(payload.get('rating_mean'))}",
            f"Rating range: {_format_decimal(payload.get('rating_min'))} to {_format_decimal(payload.get('rating_max'))}",
            f"Movies matched to TMDb IDs: {payload.get('movie_with_tmdb_id_count', 'unknown')}",
            f"Movies with TMDb details: {payload.get('movie_with_tmdb_detail_count', 'unknown')}",
        ]
        return [
            RagDocument(
                id="dataset_summary",
                source_id="dataset_summary",
                source_name="dataset_summary",
                source_path=str(DATASET_SUMMARY_FILE),
                source_type="json",
                title="Dataset Summary",
                content="\n".join(lines),
                metadata={
                    "dataset": payload.get("dataset", ""),
                    "scope": payload.get("scope", ""),
                },
            )
        ]

    def _load_quality_report(self) -> list[RagDocument]:
        if not QUALITY_REPORT_FILE.exists():
            return []

        payload = load_json(QUALITY_REPORT_FILE)
        important_keys = [
            ("scope", "Quality report scope"),
            ("source_movie_count", "Source movie count"),
            ("final_movie_count", "Final movie count"),
            ("dropped_movie_without_tmdb_id_count", "Dropped movies without TMDb ID"),
            ("dropped_movie_without_tmdb_detail_count", "Dropped movies without TMDb detail"),
            ("dropped_rating_without_tmdb_id_movie_count", "Dropped ratings after movie removal"),
            ("dropped_tag_without_tmdb_id_movie_count", "Dropped tags after movie removal"),
            ("overview_missing_count", "Movies missing overview"),
            ("runtime_minutes_missing_count", "Movies missing runtime"),
            ("poster_url_missing_count", "Movies missing poster"),
            ("backdrop_url_missing_count", "Movies missing backdrop"),
            ("budget_nonzero_count", "Movies with budget"),
            ("revenue_nonzero_count", "Movies with revenue"),
            ("budget_revenue_both_nonzero_count", "Movies with both budget and revenue"),
        ]
        lines = ["Data quality and cleaning summary:"]
        for key, label in important_keys:
            value = payload.get(key)
            if value is None or value == "":
                continue
            lines.append(f"{label}: {value}")

        duplicate_records = payload.get("tmdb_id_duplicate_records")
        if isinstance(duplicate_records, list) and duplicate_records:
            sample_titles = [
                normalize_text(item.get("title"))
                for item in duplicate_records[:3]
                if isinstance(item, dict)
            ]
            sample_titles = [title for title in sample_titles if title]
            if sample_titles:
                lines.append(f"Duplicate TMDb sample titles: {', '.join(sample_titles)}")

        return [
            RagDocument(
                id="quality_report",
                source_id="quality_report",
                source_name="quality_report",
                source_path=str(QUALITY_REPORT_FILE),
                source_type="json",
                title="Quality Report",
                content="\n".join(lines),
                metadata={
                    "scope": payload.get("scope", ""),
                    "submission_scope": payload.get("submission_scope", ""),
                },
            )
        ]

    def _load_genre_distribution(self) -> list[RagDocument]:
        if not GENRE_STATS_FILE.exists():
            return []

        frame = load_csv(GENRE_STATS_FILE)
        if frame.empty:
            return []

        frame["movie_count"] = pd.to_numeric(frame["movie_count"], errors="coerce").fillna(0).astype(int)
        frame = frame.sort_values("movie_count", ascending=False)

        lines = ["Movie genre distribution:"]
        for record in frame.itertuples(index=False):
            genre = normalize_text(record.genre)
            if not genre:
                continue
            lines.append(f"{genre}: {int(record.movie_count)} movies")

        return [
            RagDocument(
                id="genre_distribution",
                source_id="genre_stats",
                source_name="genre_stats",
                source_path=str(GENRE_STATS_FILE),
                source_type="csv",
                title="Genre Distribution",
                content="\n".join(lines),
                metadata={"genres": frame["genre"].dropna().astype(str).tolist()},
            )
        ]

    def _load_movie_profiles(self) -> list[RagDocument]:
        frame = self._load_movies_frame()
        if frame.empty:
            return []

        popular_ids = set(
            frame.sort_values("tmdb_popularity", ascending=False, na_position="last")
            .head(POPULARITY_PROFILE_LIMIT)["movie_id"]
            .dropna()
            .astype(int)
            .tolist()
        )
        selected = frame[(frame["rating_count"] >= 10) | (frame["movie_id"].astype(int).isin(popular_ids))]

        documents: list[RagDocument] = []
        for record in selected.itertuples(index=False):
            movie_id = int(record.movie_id)
            title = normalize_text(record.title_clean) or f"Movie {movie_id}"
            genres = parse_json_list(record.genres_json)
            tags = parse_json_list(record.top_tags_json)

            lines = [
                f"Title: {title}",
                f"Year: {_format_int(record.movie_year)}",
                f"Genres: {', '.join(genres) if genres else 'unknown'}",
                f"Average rating: {_format_decimal(record.rating_mean)}",
                f"Rating count: {_format_int(record.rating_count)}",
                f"Tag count: {_format_int(record.tag_count)}",
                f"Top tags: {', '.join(tags[:10]) if tags else 'none'}",
                f"Overview: {normalize_text(record.overview) or 'none'}",
                f"Runtime: {_format_int(record.runtime_minutes)} minutes",
                f"TMDb popularity: {_format_decimal(record.tmdb_popularity)}",
                f"Budget: {_format_money(record.budget)}",
                f"Revenue: {_format_money(record.revenue)}",
                f"Original language: {normalize_text(record.original_language) or 'unknown'}",
            ]
            documents.append(
                RagDocument(
                    id=f"movie_profile:{movie_id}",
                    source_id="movies",
                    source_name="movies",
                    source_path=str(MOVIES_FILE),
                    source_type="csv",
                    title=title,
                    content="\n".join(lines),
                    metadata={
                        "movie_id": movie_id,
                        "title": title,
                        "genres": genres,
                        "tags": tags[:10],
                        "language": normalize_text(record.original_language),
                        "year": _format_int(record.movie_year),
                    },
                )
            )
        return documents

    def _load_movie_rankings(self) -> list[RagDocument]:
        frame = self._load_movies_frame()
        if frame.empty:
            return []

        documents = [
            self._build_ranking_document(
                document_id="movie_ranking:top_rated",
                title="Top Rated Movies",
                frame=frame[(frame["rating_mean"].notna()) & (frame["rating_count"] >= 20)].sort_values(
                    ["rating_mean", "rating_count"],
                    ascending=[False, False],
                ).head(RANKING_LIMIT),
            ),
            self._build_ranking_document(
                document_id="movie_ranking:most_popular",
                title="Most Popular Movies",
                frame=frame[frame["tmdb_popularity"].notna()].sort_values("tmdb_popularity", ascending=False).head(RANKING_LIMIT),
            ),
            self._build_ranking_document(
                document_id="movie_ranking:highest_revenue",
                title="Highest Revenue Movies",
                frame=frame[frame["revenue"].notna() & (frame["revenue"] > 0)].sort_values("revenue", ascending=False).head(RANKING_LIMIT),
            ),
            self._build_ranking_document(
                document_id="movie_ranking:most_rated",
                title="Most Rated Movies",
                frame=frame[frame["rating_count"].notna()].sort_values("rating_count", ascending=False).head(RANKING_LIMIT),
            ),
        ]

        genre_series = (
            frame.assign(genres=frame["genres_json"].apply(parse_json_list))
            .explode("genres")
            .dropna(subset=["genres"])
            .groupby("genres")
            .size()
            .sort_values(ascending=False)
        )
        for genre in genre_series.head(8).index.tolist():
            genre_frame = frame[frame["genres_json"].apply(lambda value: genre in parse_json_list(value))]
            genre_frame = genre_frame[(genre_frame["rating_mean"].notna()) & (genre_frame["rating_count"] >= 10)]
            documents.append(
                self._build_ranking_document(
                    document_id=f"movie_ranking:genre:{genre.lower()}",
                    title=f"Top {genre} Movies",
                    frame=genre_frame.sort_values(["rating_mean", "rating_count"], ascending=[False, False]).head(GENRE_RANKING_LIMIT),
                    genre=genre,
                )
            )

        return [document for document in documents if document is not None]

    def _load_markdown_docs(self) -> list[RagDocument]:
        if not DOCS_DATA_DIR.exists():
            return []

        documents: list[RagDocument] = []
        for path in sorted(DOCS_DATA_DIR.glob("*.md")):
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue

            documents.append(
                RagDocument(
                    id=f"project_doc:{path.stem}",
                    source_id=f"project_doc:{path.stem}",
                    source_name=path.stem,
                    source_path=str(path),
                    source_type="markdown",
                    title=path.stem,
                    content=content.strip(),
                    metadata={"title": path.stem, "path": str(path)},
                )
            )
        return documents

    def _build_ranking_document(
        self,
        document_id: str,
        title: str,
        frame: pd.DataFrame,
        genre: str | None = None,
    ) -> RagDocument | None:
        if frame.empty:
            return None

        lines = [f"{title}:"]
        metadata_titles: list[str] = []
        for index, record in enumerate(frame.itertuples(index=False), start=1):
            movie_title = normalize_text(record.title_clean)
            if not movie_title:
                continue

            metadata_titles.append(movie_title)
            lines.append(
                f"{index}. {movie_title} "
                f"(year={_format_int(record.movie_year)}, rating={_format_decimal(record.rating_mean)}, "
                f"rating_count={_format_int(record.rating_count)}, popularity={_format_decimal(record.tmdb_popularity)})"
            )

        if len(lines) == 1:
            return None

        return RagDocument(
            id=document_id,
            source_id="movies",
            source_name="movies",
            source_path=str(MOVIES_FILE),
            source_type="csv",
            title=title,
            content="\n".join(lines),
            metadata={"titles": metadata_titles, "genre": genre or ""},
        )

    def _load_movies_frame(self) -> pd.DataFrame:
        if not MOVIES_FILE.exists():
            return pd.DataFrame()

        frame = load_csv(MOVIES_FILE)
        if frame.empty:
            return frame

        for column in [
            "movie_id",
            "movie_year",
            "rating_count",
            "rating_mean",
            "tag_count",
            "runtime_minutes",
            "tmdb_popularity",
            "budget",
            "revenue",
        ]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame


def _format_decimal(value: Any) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    return f"{float(value):.2f}"


def _format_int(value: Any) -> str:
    if value is None or pd.isna(value):
        return "unknown"
    return str(int(float(value)))


def _format_money(value: Any) -> str:
    if value is None or pd.isna(value) or float(value) <= 0:
        return "unknown"
    return str(int(float(value)))
