# CineScope Server

`server/` is the unified FastAPI backend for the React client. It keeps the
frontend contract stable while composing local movie search, statistics,
recommendation, lightweight RAG, and an optional DeepSeek-backed agent layer.

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
POST /rag/search
POST /rag/index
GET  /rag/sources
POST /agent/chat
POST /agent/recommend
```

## What Each Module Does

- `movies`: loads `data/final/movies.csv`, supports search, filtering, sorting, and detail lookup.
- `stats`: serves summary cards, genre distribution, budget trend, revenue-budget scatter points, and correlation cells.
- `recommendations`: proxies the standalone `recommender/` service for `content` and `collaborative` modes, and enriches `agent-ready` responses with local RAG context.
- `rag`: builds a lightweight in-memory retriever from `data/final/` and `docs/data/`.
- `agent`: classifies project QA vs recommendation intent, optionally uses DeepSeek to organize answers, and always falls back to deterministic local behavior if LLM access is unavailable.

## RAG Data Sources

The local RAG layer only reads existing project files:

```text
data/final/dataset_summary.json
data/final/quality_report.json
data/final/genre_stats.csv
data/final/movies.csv
docs/data/*.md
```

It does not ingest `ratings.csv` or `tags.csv` row-by-row. Recommendation
results still come from the local recommender service or local catalog fallback.

## Environment Variables

Recommended variables for local development:

```env
RECOMMENDER_BASE_URL=http://127.0.0.1:8010
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT_SECONDS=30
AGENT_USE_LLM=true
AGENT_MAX_CONTEXT_CHARS=5000
AGENT_MAX_RAG_RESULTS=5
```

- The backend now auto-loads `D:\205zd\Desktop\CS\.env` first, and then `D:\205zd\Desktop\CS\server\.env` if it exists.
- A ready-to-edit template is available at `D:\205zd\Desktop\CS\.env.example`.
- If `DEEPSEEK_API_KEY` is empty, the agent automatically falls back to rule-based behavior.
- If `AGENT_USE_LLM=false`, the DeepSeek client is disabled even if a key exists.
- `CINESCOPE_RECOMMENDER_BASE_URL` is still supported for backward compatibility, but `RECOMMENDER_BASE_URL` is preferred.

## Local Setup

Install dependencies:

```powershell
py -m pip install -r server/requirements.txt
py -m pip install -r recommender/requirements.txt
```

Start the recommender service first:

```powershell
py -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 8010
```

Then start the unified backend:

```powershell
py -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

The frontend example config should point to:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Default CORS allows both `http://127.0.0.1:5173` and `http://localhost:5173`.

## Manual Smoke Checks

### RAG

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"Toy Story","topK":3}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"数据集 有多少评分","topK":3}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"科幻 高分","topK":3}'
```

### Agent Project QA

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/agent/chat -ContentType 'application/json' -Body '{"message":"你们的数据集有多少电影和评分？"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/agent/chat -ContentType 'application/json' -Body '{"message":"MovieLens 和 IMDb 在这个项目里分别提供了什么？"}'
```

### Agent Recommendation

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/agent/recommend -ContentType 'application/json' -Body '{"message":"推荐几部高分科幻片，不要恐怖片","topK":6}'
```

### Frontend-Compatible Recommendation API

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/recommendations -ContentType 'application/json' -Body '{"mode":"agent-ready","prompt":"推荐几部高分科幻片，不要恐怖片","seedMovieName":"","userId":"","topK":6}'
```

## Notes

- Recommendation artifacts must exist under `recommender/artifacts/`.
- The RAG layer is intentionally lightweight and in-memory; no FAISS, Chroma, LangChain, or external embedding service is required.
- DeepSeek is only used to rewrite answers and explanations. It never becomes the source of truth for movie IDs, titles, scores, or project statistics.
