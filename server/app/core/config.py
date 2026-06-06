from __future__ import annotations

import os
from dataclasses import dataclass, field

from server.app.core.paths import PROJECT_ROOT, SERVER_DIR

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


def _load_env_files() -> None:
    if load_dotenv is None:
        return
    for path in (PROJECT_ROOT / ".env", SERVER_DIR / ".env"):
        if path.exists():
            load_dotenv(path, override=False)


_load_env_files()


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "CineScope Server"
    version: str = "0.1.0"
    recommender_base_url: str = "http://127.0.0.1:8010"
    cors_origins: list[str] = field(default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"])
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_seconds: float = 30.0
    agent_use_llm: bool = True
    agent_max_context_chars: int = 5000
    agent_max_rag_results: int = 5


def get_config() -> AppConfig:
    origins = os.getenv("CINESCOPE_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return AppConfig(
        app_name=os.getenv("CINESCOPE_APP_NAME", "CineScope Server"),
        version=os.getenv("CINESCOPE_VERSION", "0.1.0"),
        recommender_base_url=os.getenv(
            "RECOMMENDER_BASE_URL",
            os.getenv("CINESCOPE_RECOMMENDER_BASE_URL", "http://127.0.0.1:8010"),
        ),
        cors_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat",
        deepseek_timeout_seconds=_get_float("DEEPSEEK_TIMEOUT_SECONDS", 30.0),
        agent_use_llm=_get_bool("AGENT_USE_LLM", True),
        agent_max_context_chars=_get_int("AGENT_MAX_CONTEXT_CHARS", 5000),
        agent_max_rag_results=_get_int("AGENT_MAX_RAG_RESULTS", 5),
    )


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default
