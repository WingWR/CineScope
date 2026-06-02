from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
RECOMMENDER_DIR = ROOT_DIR / "recommender"
FINAL_DATA_DIR = ROOT_DIR / "data" / "final"
ARTIFACT_DIR = RECOMMENDER_DIR / "artifacts"

MOVIES_FILE = FINAL_DATA_DIR / "movies.csv"
RATINGS_FILE = FINAL_DATA_DIR / "ratings.csv"

CONTENT_ARTIFACT_DIR = ARTIFACT_DIR / "content_based"
COLLABORATIVE_ARTIFACT_DIR = ARTIFACT_DIR / "collaborative"

DEFAULT_TOP_K = 10
DEFAULT_NEIGHBOR_K = 10
RECOMMENDER_SERVICE_NAME = "cinescope-recommender"

