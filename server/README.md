# CineScope Server

`server/` is the unified backend for the React client. It exposes the movie search,
recommendation, and visualization endpoints used by the frontend.

## Implemented Endpoints

```text
GET  /health
GET  /movies
GET  /movies/{movieId}
POST /recommendations
GET  /stats/summary
GET  /stats/genres
GET  /stats/budget-trend
GET  /stats/revenue-budget
GET  /stats/correlations
```

## What Each Module Does

- `movies`: loads `data/final/movies.csv`, supports search, filtering, sorting, and detail lookup.
- `stats`: serves summary cards, genre distribution, yearly budget trend, revenue-budget scatter points, and correlation cells.
- `recommendations`: proxies the standalone `recommender/` service for `content` and `collaborative` modes.
- `agent-ready`: uses lightweight prompt heuristics and falls back to local catalog ranking when needed, while still returning real movies from local data.

## Local Setup

Install dependencies:

```powershell
python -m pip install -r server/requirements.txt
python -m pip install -r recommender/requirements.txt
```

Start the recommender service first:

```powershell
python -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 8010
```

Then start the unified backend:

```powershell
python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

The frontend example config already points to `http://127.0.0.1:8000`.
Default CORS allows both `http://127.0.0.1:5173` and `http://localhost:5173`.

## Notes

- Recommendation artifacts must exist under `recommender/artifacts/`.
- Revenue prediction, standalone RAG indexing, and the richer internal agent layer remain extension points and are not exposed as public frontend endpoints yet.
