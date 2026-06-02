# CineScope Recommender Service

This directory is a standalone recommendation microservice. It is intentionally
separate from the future backend: the backend should call it through HTTP
instead of importing recommendation code directly.

## What It Provides

1. Content-based recommendation
   - `overview` text: `TfidfVectorizer` + cosine similarity.
   - movie content soup: `CountVectorizer` + cosine similarity.
   - The two similarity scores are merged into one ranking.

2. Collaborative recommendation
   - item-based KNN: every movie is represented by all users' ratings.
   - user-based KNN: every user is represented by ratings over all movies.
   - The two candidate sets are merged into one ranking when both `user_id`
     and `movie_name` are provided.

The current final movie table does not contain directors, actors, or external
keywords. The content soup currently uses title, genres, top tags, and original
language. If ETL later adds directors or cast fields, add them in
`algorithms/content_based/features.py`.

## Directory Layout

```text
recommender/
  app/                  # FastAPI HTTP layer
  core/                 # business orchestration and ranking utilities
  algorithms/           # algorithm implementations
  data/                 # loaders and preprocessing helpers
  artifacts/            # generated vectorizers, matrices, and KNN models
  scripts/              # offline build and demo entry points
```

## Build Artifacts

Run from the repository root:

```powershell
E:\CodeEnv\Anaconda\python.exe -m recommender.scripts.build_all
```

## Run The Service

```powershell
E:\CodeEnv\Anaconda\python.exe -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 8010
```

## Endpoints

```text
GET /health
GET /recommend/content?movie_name=Toy Story&top_k=10
GET /recommend/collaborative?user_id=1&movie_name=Toy Story&top_k=10
```

For a purely personalized collaborative list, omit `movie_name`:

```text
GET /recommend/collaborative?user_id=1&top_k=10
```

