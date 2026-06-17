from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI

if __package__ in {None, "", "app"}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3000)

