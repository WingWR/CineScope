# CineScope 最终数据说明

本目录提供清洗后可直接供后端、算法和前端使用的数据。终版数据统一放在 `data/final/` 下。

## 数据范围

- 数据源为 MovieLens `ml-latest-small` 与 TMDb 详情数据。
- MovieLens 原始电影数为 9742 部。
- 其中 8 部缺失 `tmdb_id`，7 部无法通过 TMDb movie、TMDb TV 或 IMDb external ID 兜底获取详情，均已从终版数据中剔除。
- 终版保留 9727 部电影，且每部电影都满足 `tmdb_id` 非空、`has_tmdb_detail=true`。
- 终版评分保留 100811 条，标签保留 3678 条。
- `movie_id` 是项目内主键；`tmdb_id` 是对接 TMDb 的外部 ID。

## 文件概览

| 文件 | 行数 | 用途 |
| --- | ---: | --- |
| `final/movies.csv` | 9727 | 电影主表，包含 MovieLens 基础信息、评分统计、标签聚合、TMDb 详情字段和搜索字段。 |
| `final/ratings.csv` | 100811 | 用户评分表，用于协同过滤、用户画像和评分分析。 |
| `final/tags.csv` | 3678 | 用户标签表，用于内容理解、解释型推荐和关键词展示。 |
| `final/movie_features.csv` | 9727 | 推荐特征表，包含评分特征、文本特征和类型 one-hot 特征。 |
| `final/genre_stats.csv` | 19 | MovieLens 类型分布统计。 |
| `final/dataset_summary.json` | 1 | 数据集整体概览。 |
| `final/quality_report.json` | 1 | 数据质量检查结果。 |

## 推荐使用方式

后端接口建议优先读取：

- `final/movies.csv`
- `final/ratings.csv`
- `final/tags.csv`
- `final/dataset_summary.json`
- `final/genre_stats.csv`

算法建模建议优先读取：

- `final/movie_features.csv`
- `final/ratings.csv`
- `final/tags.csv`

前端本地 Mock 或静态预览建议优先读取：

- `final/movies.csv`
- `final/dataset_summary.json`
- `final/genre_stats.csv`

常用展示字段：

| 场景 | 推荐字段 |
| --- | --- |
| 标题 | `display_title` |
| 年份 | `display_year` |
| 海报 | `poster_url` |
| 背景图 | `backdrop_url` |
| 简介 | `overview` |
| 类型 | `genres_json` 或 `tmdb_genres_json` |
| 评分 | `tmdb_vote_average` 或 `rating_mean` |
| 热度排序 | `weighted_rating`、`rating_count`、`tmdb_popularity` |
| 搜索 | `search_text` |

## `final/movies.csv`

电影主表。每行是一部 MovieLens 电影，且保证 `tmdb_id` 非空、`has_tmdb_detail=true`。

| 字段 | 说明 |
| --- | --- |
| `movie_id` | MovieLens 电影主键，也是项目内主键。 |
| `title` | MovieLens 原始标题。 |
| `title_clean` | 去除年份后的 MovieLens 标题。 |
| `movie_year` | 从 MovieLens 标题解析出的年份。 |
| `genres` | MovieLens 原始类型字符串，使用 `|` 分隔。 |
| `genres_json` | MovieLens 类型数组 JSON。 |
| `genres_text` | MovieLens 类型拼接文本，便于搜索和特征构造。 |
| `imdb_id` | MovieLens 自带 IMDb 数字 ID。 |
| `imdb_tt_id` | 标准 `tt` 格式 IMDb ID。 |
| `tmdb_id` | MovieLens `links.csv` 提供的 TMDb ID。 |
| `tmdb_resolved_id` | 实际拉取详情时使用的 TMDb ID。多数情况下等于 `tmdb_id`；通过 IMDb external ID 兜底时可能不同。 |
| `tmdb_resolved_from_imdb_id` | 如果通过 IMDb external ID 兜底匹配，则记录使用的 `imdb_tt_id`。 |
| `tmdb_media_type` | TMDb 详情来源类型，取值为 `movie` 或 `tv`。 |
| `rating_count` | MovieLens 评分数。 |
| `rating_mean` | MovieLens 平均评分。 |
| `rating_median` | MovieLens 评分中位数。 |
| `rating_std` | MovieLens 评分标准差。 |
| `rating_min` | MovieLens 最低评分。 |
| `rating_max` | MovieLens 最高评分。 |
| `tag_count` | 标签数量。 |
| `top_tags_json` | 高频标签数组 JSON，最多 20 个。 |
| `tags_text` | 高频标签拼接文本。 |
| `tmdb_title` | TMDb 标题。 |
| `tmdb_original_title` | TMDb 原始标题。 |
| `overview` | TMDb 简介。 |
| `release_date` | TMDb 上映日期。 |
| `tmdb_year` | 从 TMDb 上映日期解析出的年份。 |
| `runtime_minutes` | TMDb 片长，单位为分钟；TV 条目或少量 TMDb 记录可能为空。 |
| `tmdb_vote_average` | TMDb 平均评分。 |
| `tmdb_vote_count` | TMDb 投票数。 |
| `tmdb_popularity` | TMDb 热度。 |
| `original_language` | TMDb 原始语言。 |
| `tmdb_status` | TMDb 条目状态。 |
| `poster_url` | TMDb 海报完整 URL；少量 TMDb 记录可能无海报。 |
| `backdrop_url` | TMDb 背景图完整 URL；少量 TMDb 记录可能无背景图。 |
| `tmdb_genres_json` | TMDb 类型数组 JSON。 |
| `display_title` | 展示标题，优先使用 TMDb 标题。 |
| `display_year` | 展示年份，优先使用 TMDb 年份。 |
| `has_tmdb_id` | 是否存在 TMDb ID；终版数据中均为 `true`。 |
| `has_tmdb_detail` | 是否已融合 TMDb 详情；终版数据中均为 `true`。 |
| `search_text` | 搜索文本，拼接标题、类型、标签和简介。 |
| `weighted_rating` | 基于 MovieLens 评分数和均分计算的加权评分。 |

## `final/ratings.csv`

用户评分表。只保留终版电影集合中的评分记录。

| 字段 | 说明 |
| --- | --- |
| `user_id` | MovieLens 用户 ID。 |
| `movie_id` | MovieLens 电影 ID，可关联 `movies.csv.movie_id`。 |
| `rating` | 用户评分，范围 0.5 到 5.0。 |
| `timestamp` | MovieLens 原始 Unix 时间戳。 |
| `rated_at` | UTC ISO 格式评分时间。 |

## `final/tags.csv`

用户标签表。只保留终版电影集合中的标签记录。

| 字段 | 说明 |
| --- | --- |
| `user_id` | MovieLens 用户 ID。 |
| `movie_id` | MovieLens 电影 ID，可关联 `movies.csv.movie_id`。 |
| `tag` | 清洗后的原始标签，已去除首尾空白。 |
| `timestamp` | MovieLens 原始 Unix 时间戳。 |
| `tag_norm` | 小写归一化标签。 |
| `tagged_at` | UTC ISO 格式打标签时间。 |

## `final/movie_features.csv`

推荐特征表。每行对应一部终版电影。

| 字段 | 说明 |
| --- | --- |
| `movie_id` | MovieLens 电影 ID。 |
| `display_title` | 展示标题。 |
| `display_year` | 展示年份。 |
| `genres_json` | MovieLens 类型数组 JSON。 |
| `top_tags_json` | 高频标签数组 JSON。 |
| `rating_count` | MovieLens 评分数。 |
| `rating_mean` | MovieLens 平均评分。 |
| `weighted_rating` | 加权评分。 |
| `tmdb_vote_average` | TMDb 平均评分。 |
| `tmdb_vote_count` | TMDb 投票数。 |
| `tmdb_popularity` | TMDb 热度。 |
| `feature_text` | 内容推荐与搜索用文本。 |
| `genre_*` | MovieLens 类型 one-hot 特征。 |

## `final/genre_stats.csv`

类型分布表。

| 字段 | 说明 |
| --- | --- |
| `genre` | MovieLens 类型。 |
| `movie_count` | 对应类型电影数量。 |

## `final/dataset_summary.json`

数据集概览，适合用于前端概览卡片、报告和答辩材料。

```json
{
  "dataset": "ml-latest-small",
  "scope": "movies_with_tmdb_detail",
  "movie_count": 9727,
  "user_count": 610,
  "rating_count": 100811,
  "tag_count": 3678,
  "genre_count": 19,
  "rating_mean": 3.5015821686125523,
  "rating_min": 0.5,
  "rating_max": 5.0,
  "movie_with_tmdb_id_count": 9727,
  "movie_with_tmdb_detail_count": 9727
}
```

## 数据质量说明

- `movie_id` 在 `final/movies.csv` 和 `final/movie_features.csv` 中唯一。
- `tmdb_id` 非空。
- `has_tmdb_detail` 全部为 `true`。
- 已从终版数据剔除 8 部缺失 `tmdb_id` 的电影和 7 部缺失 TMDb 详情的电影。
- 因电影剔除，对应剔除了 25 条评分记录和 5 条标签记录。
- `tmdb_media_type=movie` 的记录有 9628 条。
- `tmdb_media_type=tv` 的记录有 99 条，主要来自 MovieLens 中实际为剧集、迷你剧或电视电影的条目。
- 通过 `imdb_tt_id` 兜底解析 TMDb 详情的记录有 35 条。
- `display_title`、`display_year`、`search_text`、`feature_text` 均无缺失。
- `overview` 缺失 35 条，原因是 TMDb 对这些条目未提供简介文本。
- `runtime_minutes` 缺失 41 条。
- `poster_url` 缺失 31 条。
- `backdrop_url` 缺失 122 条。
- 存在 1 组重复 `tmdb_id=4912`，对应 `movie_id=6003` 和 `movie_id=144606`。终版数据保留两行，因为项目内主键是 `movie_id`，且两个 MovieLens 条目的类型信息不同。
