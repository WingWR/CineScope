# CineScope 前端接口文档

本文档描述 `client` 前端当前封装和依赖的后端接口契约。

前端只连接一个统一业务后端。推荐算法、Agent、向量检索、模型服务或其他内部服务应由该业务后端封装，不能作为前端直接依赖暴露出来。

## 环境配置

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 是 | 统一业务后端地址，例如 `http://127.0.0.1:8000`。前端会自动去掉末尾 `/`。 |
| `VITE_API_TIMEOUT_MS` | 否 | 请求超时时间，单位毫秒。未设置时默认 `8000`。 |

## 通用规则

- 所有请求字段和响应字段使用 `camelCase`。
- 请求和响应均使用 JSON。
- 前端请求会带 `Content-Type: application/json`。
- 列表资源返回 `{ "items": [] }`，图表序列接口直接返回数组 `[]`。
- 后端异常或不可用时返回标准 HTTP 错误；前端会展示连接提示。
- 前端不渲染 mock 数据，只展示后端真实返回内容或连接提示。
- `204 No Content` 会被前端当作 `undefined` 处理。

## 接口总览

| 页面/模块 | 方法 | 路径 | 前端封装 | 响应形态 | 当前使用情况 |
| --- | --- | --- | --- | --- | --- |
| 电影搜索 | `GET` | `/movies` | `movieSearchApi.listMovies` | `{ items: Movie[]; total?: number }` | 已使用 |
| 电影详情 | `GET` | `/movies/{movieId}` | `movieSearchApi.getMovie` | `Movie` | 已封装，当前页面未直接调用 |
| 推荐 | `POST` | `/recommendations` | `recommendationApi.recommend` | `{ items: RecommendationItem[] }` | 已使用 |
| 数据可视化 | `GET` | `/stats/summary` | `atlasApi.getSummary` | `AtlasSummary` | 已使用 |
| 数据可视化 | `GET` | `/stats/genres` | `atlasApi.getGenreDistribution` | `GenreDistributionItem[]` | 已使用 |
| 数据可视化 | `GET` | `/stats/budget-trend` | `atlasApi.getBudgetTrend` | `BudgetTrendPoint[]` | 已使用 |
| 数据可视化 | `GET` | `/stats/revenue-budget` | `atlasApi.getRevenueBudgetPoints` | `RevenueBudgetPoint[]` | 已使用 |
| 数据可视化 | `GET` | `/stats/correlations` | `atlasApi.getCorrelationCells` | `CorrelationCell[]` | 已使用 |

## 数据类型

### Movie

```ts
type Movie = {
  id: number | string;
  title: string;
  year?: number;
  genres?: string[];
  ratingMean?: number;
  ratingCount?: number;
  tagCount?: number;
  tags?: string[];
  overview?: string;
  runtimeMinutes?: number;
  tmdbPopularity?: number;
  budget?: number;
  revenue?: number;
  language?: string;
  posterUrl?: string;
  backdropUrl?: string;
};
```

### RecommendationRequest

```ts
type RecommendationRequest = {
  mode: "content" | "collaborative" | "agent-ready";
  prompt: string;
  seedMovieName: string;
  userId: string;
  topK: number;
};
```

### RecommendationItem

```ts
type RecommendationItem = {
  movie: Movie;
  score: number;
  reason: string;
  source: "content" | "collaborative" | "hybrid" | "agent-ready" | string;
};
```

### 接口响应类型

```ts
type MovieListResponse = {
  items: Movie[];
  total?: number;
};

type RecommendationResponse = {
  items: RecommendationItem[];
};

type AtlasSummary = {
  dataset?: string;
  movieCount?: number;
  userCount?: number;
  ratingCount?: number;
  tagCount?: number;
  genreCount?: number;
  ratingMean?: number;
};

type GenreDistributionItem = {
  genre: string;
  count: number;
};

type BudgetTrendPoint = {
  year: number;
  budget: number;
};

type RevenueBudgetPoint = {
  title: string;
  budget: number;
  revenue: number;
  popularity?: number;
};

type CorrelationCell = {
  x: string;
  y: string;
  value: number;
};
```

### 数组字段速查

| 字段/接口 | 数组类型 | 说明 |
| --- | --- | --- |
| `Movie.genres` | `string[]` | 电影类型列表。 |
| `Movie.tags` | `string[]` | 标签列表。 |
| `GET /movies` 的 `items` | `Movie[]` | 电影搜索结果列表。 |
| `POST /recommendations` 的 `items` | `RecommendationItem[]` | 推荐结果列表。 |
| `GET /stats/genres` | `GenreDistributionItem[]` | 类型分布图表序列。 |
| `GET /stats/budget-trend` | `BudgetTrendPoint[]` | 年份预算趋势图表序列。 |
| `GET /stats/revenue-budget` | `RevenueBudgetPoint[]` | 收入与预算散点图序列。 |
| `GET /stats/correlations` | `CorrelationCell[]` | 相关性热力矩阵数据。 |

## 电影接口

### `GET /movies`

用于电影搜索页，根据搜索词、类型、语言、最低评分和排序方式获取电影列表。

#### Query 参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `search` | `string` | 否 | 搜索关键词。 |
| `genre` | `string` | 否 | 类型过滤，例如 `Drama`。 |
| `language` | `string` | 否 | 语言过滤，例如 `en` / `zh`。 |
| `minRating` | `number` | 否 | 最低评分。 |
| `sort` | `"popularity" \| "rating" \| "revenue" \| "year"` | 否 | 排序方式。 |

#### 响应

响应类型：`MovieListResponse`，其中 `items` 是 `Movie[]`。

```json
{
  "items": [
    {
      "id": 1,
      "title": "电影标题",
      "year": 1995,
      "genres": ["Drama"],
      "ratingMean": 4.1,
      "ratingCount": 100,
      "tagCount": 12,
      "tags": ["tag"],
      "overview": "剧情简介",
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

`total` 可选。前端当前只使用 `items`。

### `GET /movies/{movieId}`

用于按电影 ID 获取单部电影详情。该接口已在前端 API 层封装，但当前页面详情面板直接使用 `/movies` 列表项中的数据，尚未单独请求此接口。

#### Path 参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `movieId` | `number \| string` | 是 | 电影 ID。前端会进行 URL encode。 |

#### 响应

响应类型：`Movie`。

```json
{
  "id": 1,
  "title": "电影标题",
  "year": 1995,
  "genres": ["Drama"],
  "ratingMean": 4.1,
  "ratingCount": 100,
  "tagCount": 12,
  "tags": ["tag"],
  "overview": "剧情简介",
  "runtimeMinutes": 120,
  "tmdbPopularity": 10.5,
  "budget": 1000000,
  "revenue": 5000000,
  "language": "en",
  "posterUrl": "https://...",
  "backdropUrl": "https://..."
}
```

## 推荐接口

### `POST /recommendations`

用于推荐页提交推荐请求。三种模式共用同一个请求结构；只有 `agent-ready` 模式会使用自然语言 `prompt`。

#### 请求体

```json
{
  "mode": "agent-ready",
  "prompt": "我想看一部节奏紧凑、评分较高的科幻电影",
  "seedMovieName": "Inception",
  "userId": "1",
  "topK": 6
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | `"content" \| "collaborative" \| "agent-ready"` | 是 | 推荐模式。 |
| `prompt` | `string` | 是 | Agent 模式的自然语言描述；非 Agent 模式可传空字符串。 |
| `seedMovieName` | `string` | 是 | 种子电影名；可为空字符串。 |
| `userId` | `string` | 是 | 默认用户 ID。前端内部自动传递，页面不提供输入框。 |
| `topK` | `number` | 是 | 返回推荐数量。 |

#### 响应

响应类型：`RecommendationResponse`，其中 `items` 是 `RecommendationItem[]`。

```json
{
  "items": [
    {
      "movie": {
        "id": 1,
        "title": "电影标题",
        "year": 1995,
        "genres": ["Drama"],
        "ratingMean": 4.1,
        "posterUrl": "https://..."
      },
      "score": 0.91,
      "reason": "推荐原因说明",
      "source": "agent-ready"
    }
  ]
}
```

## 数据可视化接口

### `GET /stats/summary`

用于 Atlas 页面顶部统计卡片。

#### 响应

响应类型：`AtlasSummary`。

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

所有字段均可选。前端当前展示 `movieCount`、`ratingCount`、`genreCount`。

### `GET /stats/genres`

用于 Atlas 类型分布柱状图。

#### 响应

响应类型：`GenreDistributionItem[]`。

```json
[
  {
    "genre": "Drama",
    "count": 4355
  }
]
```

### `GET /stats/budget-trend`

用于 Atlas 年份预算趋势折线图。

#### 响应

响应类型：`BudgetTrendPoint[]`。

```json
[
  {
    "year": 2000,
    "budget": 49
  }
]
```

### `GET /stats/revenue-budget`

用于 Atlas 预算与收入散点图。

#### 响应

响应类型：`RevenueBudgetPoint[]`。

```json
[
  {
    "title": "电影标题",
    "budget": 100,
    "revenue": 500,
    "popularity": 20
  }
]
```

`popularity` 可选；未提供时前端会使用默认气泡大小计算值。

### `GET /stats/correlations`

用于 Atlas 相关性热力矩阵。

#### 响应

响应类型：`CorrelationCell[]`。

```json
[
  {
    "x": "Budget",
    "y": "Revenue",
    "value": 0.72
  }
]
```

`value` 建议范围为 `0` 到 `1`。前端会用该值计算热力颜色强度。

## 前端错误处理

- 未配置 `VITE_API_BASE_URL`：前端显示后端未配置提示。
- HTTP 非 2xx：前端显示接口不可用提示，并包含 HTTP 状态码。
- 请求超时：前端显示接口未返回可用数据提示。
- 返回空数组或空 `items`：前端显示空状态，不会使用本地假数据填充。
