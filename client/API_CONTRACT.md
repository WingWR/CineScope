# CineScope Client API Contract

The frontend reads only `VITE_API_BASE_URL`.

The client talks to one unified business backend. Recommendation algorithms, agents, vector search, or other internal services should be wrapped by that backend and must not appear as frontend dependencies.

The frontend does not maintain response mappers. Backend responses should use the camelCase contract below.

## Common Rules

- All request and response fields use camelCase.
- Empty list responses return `items: []` for paged/list resources, or `[]` for chart series.
- Failed or unavailable endpoints should return normal HTTP errors; the frontend will show a connection notice.
- No mock data is rendered by the client.

## Movies

### `GET /movies`

Query:

- `search?: string`
- `genre?: string`
- `language?: string`
- `minRating?: number`
- `sort?: "popularity" | "rating" | "revenue" | "year"`

Response:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Movie title",
      "year": 1995,
      "genres": ["Drama"],
      "ratingMean": 4.1,
      "ratingCount": 100,
      "tagCount": 12,
      "tags": ["tag"],
      "overview": "Synopsis",
      "runtimeMinutes": 120,
      "tmdbPopularity": 10.5,
      "budget": 1000000,
      "revenue": 5000000,
      "language": "en",
      "posterUrl": "https://...",
      "backdropUrl": "https://..."
    }
  ],
  "total": 1
}
```

### `GET /movies/:movieId`

Response:

```json
{
  "id": 1,
  "title": "Movie title",
  "year": 1995,
  "genres": ["Drama"],
  "ratingMean": 4.1,
  "ratingCount": 100,
  "tagCount": 12,
  "tags": ["tag"],
  "overview": "Synopsis",
  "runtimeMinutes": 120,
  "tmdbPopularity": 10.5,
  "budget": 1000000,
  "revenue": 5000000,
  "language": "en",
  "posterUrl": "https://...",
  "backdropUrl": "https://..."
}
```

## Recommendations

### `POST /recommendations`

Request:

```json
{
  "mode": "agent-ready",
  "prompt": "I want a clever sci-fi movie",
  "seedMovieName": "Inception",
  "userId": "42",
  "topK": 6
}
```

`mode` values:

- `"content"`
- `"collaborative"`
- `"agent-ready"`

Response:

```json
{
  "items": [
    {
      "movie": {
        "id": 1,
        "title": "Movie title",
        "year": 1995,
        "genres": ["Drama"],
        "ratingMean": 4.1,
        "posterUrl": "https://..."
      },
      "score": 0.91,
      "reason": "Why this was recommended",
      "source": "agent-ready"
    }
  ]
}
```

## Stats / Atlas

### `GET /stats/summary`

Response:

```json
{
  "dataset": "MovieLens",
  "movieCount": 9727,
  "userCount": 610,
  "ratingCount": 100811,
  "tagCount": 3678,
  "genreCount": 19,
  "ratingMean": 3.5
}
```

### `GET /stats/genres`

Response:

```json
[
  { "genre": "Drama", "count": 4355 }
]
```

### `GET /stats/budget-trend`

Response:

```json
[
  { "year": 2000, "budget": 49 }
]
```

### `GET /stats/revenue-budget`

Response:

```json
[
  { "title": "Movie title", "budget": 100, "revenue": 500, "popularity": 20 }
]
```

### `GET /stats/correlations`

Response:

```json
[
  { "x": "Budget", "y": "Revenue", "value": 0.72 }
]
```
