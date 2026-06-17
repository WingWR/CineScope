from __future__ import annotations

from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SERVER_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
FINAL_DATA_DIR = DATA_DIR / "final"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RECOMMENDER_DIR = PROJECT_ROOT / "recommender"

MOVIES_FILE = FINAL_DATA_DIR / "movies.csv"
RATINGS_FILE = FINAL_DATA_DIR / "ratings.csv"
TAGS_FILE = FINAL_DATA_DIR / "tags.csv"
GENRE_STATS_FILE = FINAL_DATA_DIR / "genre_stats.csv"
DATASET_SUMMARY_FILE = FINAL_DATA_DIR / "dataset_summary.json"
QUALITY_REPORT_FILE = FINAL_DATA_DIR / "quality_report.json"
