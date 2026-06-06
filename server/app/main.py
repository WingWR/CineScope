from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from server.app.core.config import get_config
from server.app.core.errors import ModuleNotImplementedError
from server.app.core.response import error_response
from server.app.modules.agent.router import router as agent_router
from server.app.modules.movies.router import router as movies_router
from server.app.modules.rag.router import router as rag_router
from server.app.modules.recommendations.router import router as recommendations_router
from server.app.modules.stats.router import router as stats_router


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
