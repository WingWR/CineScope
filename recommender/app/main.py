from __future__ import annotations

from fastapi import FastAPI

from recommender.app.routes import router
from recommender.app.settings import RECOMMENDER_SERVICE_NAME


app = FastAPI(
    title="CineScope Recommender Service",
    description="Standalone content-based and collaborative recommendation service.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": RECOMMENDER_SERVICE_NAME, "status": "ok"}

