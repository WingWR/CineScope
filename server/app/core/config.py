from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "CineScope Server"
    version: str = "0.1.0"
    recommender_base_url: str = "http://127.0.0.1:8010"
    cors_origins: list[str] = field(default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"])


def get_config() -> AppConfig:
    origins = os.getenv("CINESCOPE_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return AppConfig(
        app_name=os.getenv("CINESCOPE_APP_NAME", "CineScope Server"),
        version=os.getenv("CINESCOPE_VERSION", "0.1.0"),
        recommender_base_url=os.getenv("CINESCOPE_RECOMMENDER_BASE_URL", "http://127.0.0.1:8010"),
        cors_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
    )
