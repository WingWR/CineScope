from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "server.app"

from .core.config import get_config
from .core.errors import ModuleNotImplementedError
from .core.response import error_response
from .modules.agent.router import router as agent_router
from .modules.movies.router import router as movies_router
from .modules.rag.router import router as rag_router
from .modules.recommendations.router import router as recommendations_router
from .modules.stats.router import router as stats_router


def create_app() -> FastAPI:
    config = get_config()
    app = FastAPI(title=config.app_name, version=config.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(movies_router)
    app.include_router(recommendations_router)
    app.include_router(stats_router)
    app.include_router(rag_router)
    app.include_router(agent_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "service": config.app_name,
            "status": "ok",
            "version": config.version,
        }

    @app.exception_handler(ModuleNotImplementedError)
    async def handle_module_not_implemented(
        request: Request,
        exc: ModuleNotImplementedError,
    ):
        return error_response(
            status_code=501,
            code="MODULE_NOT_IMPLEMENTED",
            message=str(exc),
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
