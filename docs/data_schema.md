# CineScope 数据字段说明

## 数据来源

- MovieLens `ml-latest-small`：评分、电影标题、类型、用户标签、外部 ID 映射。
- TMDb API：电影详情、简介、片长、语言、评分、投票数、热度、海报和背景图。

MovieLens 的 `links.csv.tmdbId` 是本项目对接 TMDb 的核心外键。

## 输出文件

### `data/processed/movies_enriched.csv`

面向后端电影检索、电影详情页、前端展示和推荐解释。

核心字段：

- `movie_id`：MovieLens 电影主键。
- `title`：MovieLens 原始标题。
- `title_clean`：去除年份后的标题。
- `movie_year`：从 MovieLens 标题解析出的年份。
- `genres`：MovieLens 原始类型字符串。
- `genres_json`：标准化类型数组 JSON。
- `genres_text`：用于检索和内容特征的类型文本。
- `imdb_id`、`imdb_tt_id`：MovieLens 自带 IMDb 映射，仅保留为交叉引用，不作为外部元数据源。
- `tmdb_id`：TMDb 电影 ID。
- `rating_count`：MovieLens 评分数。
- `rating_mean`：MovieLens 平均评分。
- `rating_median`：MovieLens 评分中位数。
- `rating_std`：MovieLens 评分标准差。
- `tag_count`：MovieLens 标签数。
- `top_tags_json`：高频标签数组 JSON，最多 20 个。
- `tmdb_title`：TMDb 标题。
- `tmdb_original_title`：TMDb 原始标题。
- `overview`：TMDb 简介。
- `release_date`：TMDb 上映日期。
- `runtime_minutes`：TMDb 片长。
- `tmdb_vote_average`：TMDb 平均评分；未拉取时回退为 MovieLens 平均评分。
- `tmdb_vote_count`：TMDb 投票数；未拉取时回退为 MovieLens 评分数。
- `tmdb_popularity`：TMDb 热度；未拉取时回退为 MovieLens 评分数。
- `poster_url`：标准化完整海报 URL。
- `backdrop_url`：标准化完整背景图 URL。
- `display_title`：前端展示标题，优先 TMDb 标题，缺失时使用 MovieLens 标题。
- `display_year`：前端展示年份，优先 TMDb 年份，缺失时使用 MovieLens 年份。
- `has_tmdb_id`：是否存在 TMDb ID。
- `has_tmdb_detail`：是否已拉取到 TMDb 详情。
- `search_text`：电影检索和内容召回用拼接文本。
- `weighted_rating`：基于 MovieLens 评分数和均分构造的加权评分。

### `data/processed/ratings_clean.csv`

面向协同过滤、用户画像和评分分布分析。

核心字段：

- `user_id`
- `movie_id`
- `rating`
- `timestamp`
- `rated_at`

### `data/processed/tags_clean.csv`

面向内容推荐、解释标签和搜索。

核心字段：

- `user_id`
- `movie_id`
- `tag`
- `tag_norm`
- `timestamp`
- `tagged_at`

### `data/processed/movie_features.csv`

面向推荐算法训练和候选召回。

核心字段：

- `movie_id`
- `display_title`
- `display_year`
- `genres_json`
- `top_tags_json`
- `rating_count`
- `rating_mean`
- `weighted_rating`
- `tmdb_vote_average`
- `tmdb_vote_count`
- `tmdb_popularity`
- `feature_text`
- `genre_*`：按 MovieLens 类型展开的 one-hot 特征。

### `data/processed/genre_stats.csv`

面向前端数据分析页。

核心字段：

- `genre`
- `movie_count`

### `data/processed/dataset_summary.json`

面向前端概览卡片、README 和答辩材料。

核心字段：

- `movie_count`
- `user_count`
- `rating_count`
- `tag_count`
- `movie_with_tmdb_id_count`
- `movie_with_tmdb_detail_count`
- `genre_count`
- `rating_mean`
- `rating_min`
- `rating_max`

## 缺失值策略

- 缺失 `tmdb_id`：保留 MovieLens 基础信息，`has_tmdb_id=false`。
- 未拉取 TMDb 详情：保留 MovieLens 基础信息，`has_tmdb_detail=false`。
- 缺失 TMDb 图片：`poster_url`、`backdrop_url` 为空，由前端展示占位图。
- 缺失标签：`top_tags_json=[]`，`tags_text` 为空。
- 缺失评分统计：评分数置 0，均分和加权分置 0。
