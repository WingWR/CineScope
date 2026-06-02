from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from recommender.algorithms.content_based.features import build_content_soup, build_overview_text
from recommender.app.settings import CONTENT_ARTIFACT_DIR, MOVIES_FILE
from recommender.data.loaders import load_movies
from recommender.data.preprocess import normalize_title


def build_content_artifacts(
    movies_path: str | Path = MOVIES_FILE,
    output_dir: str | Path = CONTENT_ARTIFACT_DIR,
) -> dict[str, Any]:
    movies = load_movies(movies_path).reset_index(drop=True)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    overview_text = build_overview_text(movies)
    content_soup = build_content_soup(movies)

    overview_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        min_df=1,
        max_features=60000,
    )
    content_vectorizer = CountVectorizer(
        lowercase=True,
        token_pattern=r"(?u)\b\w+\b",
        min_df=1,
        max_features=50000,
    )

    overview_matrix = overview_vectorizer.fit_transform(overview_text)
    content_matrix = content_vectorizer.fit_transform(content_soup)

    joblib.dump(overview_vectorizer, output / "overview_tfidf.joblib")
    joblib.dump(content_vectorizer, output / "content_count.joblib")
    sparse.save_npz(output / "overview_matrix.npz", overview_matrix)
    sparse.save_npz(output / "content_matrix.npz", content_matrix)
    _write_json(output / "movie_index.json", _movie_index_payload(movies))

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "movie_count": int(len(movies)),
        "overview_feature_count": int(overview_matrix.shape[1]),
        "content_feature_count": int(content_matrix.shape[1]),
        "movies_path": str(Path(movies_path).resolve()),
    }
    _write_json(output / "metadata.json", metadata)
    return metadata


def _movie_index_payload(movies) -> dict[str, Any]:
    records = []
    for index, row in movies.iterrows():
        records.append(
            {
                "index": int(index),
                "movie_id": int(row["movie_id"]),
                "title": str(row.get("title_clean", "")),
                "normalized_title": normalize_title(row.get("title_clean", "")),
            }
        )
    return {"movies": records}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

