# CineScope Client API Contract

The frontend reads only `VITE_API_BASE_URL`.

The client talks to one unified business backend. Recommendation algorithms, agents, vector search, or other internal services should be wrapped by that backend and should not appear as frontend dependencies.

## Movies

### `GET /movies`

Query:

- `search?: string`
- `genre?: string`
- `language?: string`
- `minRating?: number`
- `sort?: "popularity" | "rating" | "revenue" | "year"`

Response can be either:

```json
[
  {
    "id": 1,
    "title": "Movie title",
    "year": 1995,
    "genres": ["Drama"],
    "ratingMean": 4.1,
    "ratingCount": 100,
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
]
```

or:

```json
{ "items": [] }
```

Snake-case fields such as `movie_id`, `title_clean`, `movie_year`, `rating_mean`, `genres_json`, `poster_url`, and `backdrop_url` are also accepted.

### `GET /movies/:movieId`

Response: one movie object using the same shape as above.

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

Response can be either:

```json
[
  {
    "movie": { "id": 1, "title": "Movie title" },
    "score": 0.91,
    "reason": "Why this was recommended",
    "source": "agent-ready"
  }
]
```

or:

```json
{ "items": [] }
```

For maintainability, prefer camelCase response fields in the backend. The frontend mapper still tolerates a few snake-case aliases on movie and stats response objects during backend iteration.

## Stats / Atlas

### `GET /stats/summary`

Response:

```json
{
  "movieCount": 9727,
  "userCount": 610,
  "ratingCount": 100811,
  "tagCount": 3678,
  "genreCount": 19,
  "ratingMean": 3.5
}
```

Snake-case variants are accepted.

### `GET /stats/genres`

```json
[
  { "genre": "Drama", "count": 4355 }
]
```

`movie_count` is also accepted.

### `GET /stats/budget-trend`

```json
[
  { "year": 2000, "budget": 49 }
]
```

`movie_year` and `average_budget` are also accepted.

### `GET /stats/revenue-budget`

```json
[
  { "title": "Movie title", "budget": 100, "revenue": 500, "popularity": 20 }
]
```

`tmdb_popularity` is also accepted.

### `GET /stats/correlations`

```json
[
  { "x": "Budget", "y": "Revenue", "value": 0.72 }
]
```
