# CineScope 数据获取、清洗、融合与特征构造计划

## 1. 数据集选择

一期选择 GroupLens 官方 `ml-latest-small` 数据集。

选择理由：

- 数据量适合课程项目和本地开发，约 10 万条评分、约 9 千部电影、约 600 名用户，可以快速完成清洗、建模、接口联调和前端展示。
- 包含 `movies.csv`、`ratings.csv`、`tags.csv`、`links.csv`，字段覆盖电影、评分、用户标签和外部 ID 映射。
- `links.csv` 中包含 `tmdbId` 字段，可直接与 TMDb API 的电影详情接口对齐。
- 相比完整 MovieLens Latest，全量 TMDb 详情拉取请求量更可控；后续如需扩大规模，可以把脚本参数切换到更大的 MovieLens 版本。

MovieLens 官方入口：https://grouplens.org/datasets/movielens/

## 2. 数据源与字段

### MovieLens

- `movies.csv`：`movieId`、`title`、`genres`
- `ratings.csv`：`userId`、`movieId`、`rating`、`timestamp`
- `tags.csv`：`userId`、`movieId`、`tag`、`timestamp`
- `links.csv`：`movieId`、`imdbId`、`tmdbId`

本项目只使用 `tmdbId` 访问 TMDb，不再把 IMDb 作为外部元数据源。

### TMDb

按 `links.csv.tmdbId` 调用 TMDb 电影详情接口，标准化保存：

- TMDb 标题、原始标题、简介、上映日期、片长、语言、状态
- TMDb 平均评分、投票数、热度
- 海报路径、背景图路径、标准化完整图片 URL
- 类型、制片国家、原始响应缓存和失败记录

凭据只从环境变量或 `data/.env` 读取，不写入代码、文档、前端或输出日志。

## 3. 目录约定

- `data/raw/movielens/`：MovieLens 原始 zip 和解压后的 csv
- `data/raw/tmdb/`：TMDb 原始详情缓存 `movie_details.jsonl` 和失败记录
- `data/interim/`：MovieLens 规范化中间表
- `data/processed/`：算法、后端和前端可直接使用的数据资产
- `docs/`：数据说明和接口对接文档
- `scripts/`：可重复执行的数据处理脚本

## 4. 清洗规则

1. 统一字段命名为 snake_case。
2. 从 MovieLens `title` 中解析 `title_clean` 和 `movie_year`。
3. 将 `genres` 中的 `|` 分隔值转换为列表；`(no genres listed)` 视为空列表。
4. 将 `timestamp` 转换为 ISO 时间字段，保留原始 Unix 时间戳。
5. `tmdbId` 转换为可空整数，缺失时保留空值并记录可融合状态。
6. 标签字段去空格，生成小写归一化标签，用于搜索和内容特征。
7. 聚合每部电影的评分数、均分、中位数、标准差、最低分、最高分。
8. 聚合每部电影的高频标签，保留前 20 个标签作为解释和内容特征。
9. TMDb 响应不直接作为业务表结构使用，必须映射为稳定字段。
10. TMDb 图片 URL 由 `TMDB_IMAGE_BASE_URL`、图片尺寸和 `file_path` 组合生成。

## 5. 融合策略

主键链路：

`MovieLens movieId -> links.csv tmdbId -> TMDb movie/{tmdbId}`

融合输出以 MovieLens `movie_id` 为主键：

1. 先合并 `movies.csv` 与 `links.csv`，得到电影基础表。
2. 以 `movie_id` 聚合评分统计，合并到电影基础表。
3. 以 `movie_id` 聚合标签统计，合并到电影基础表。
4. 用 `tmdb_id` 匹配本地 TMDb 缓存，补充外部详情。
5. 对 TMDb 缺失或请求失败的电影保留 MovieLens 基础信息，保证主流程不断裂。

## 6. 特征构造

面向电影检索：

- `display_title`
- `display_year`
- `genres_json`
- `top_tags_json`
- `search_text`
- `poster_url`
- `overview`

面向推荐算法：

- 评分统计：`rating_count`、`rating_mean`、`rating_median`、`rating_std`
- 热门度特征：MovieLens 评分数、TMDb 热度、TMDb 投票数
- 内容特征：类型 one-hot、标签文本、简介文本、语言、年份
- 排序基线：MovieLens 加权评分 `weighted_rating`

面向前端分析：

- 数据集概览：电影数、用户数、评分数、标签数、可匹配 TMDb 数
- 类型分布
- 评分分布
- 热门电影与高分电影候选
- TMDb 补充覆盖率

## 7. 输出文件

- `data/processed/movies_enriched.csv`
- `data/processed/ratings_clean.csv`
- `data/processed/tags_clean.csv`
- `data/processed/movie_features.csv`
- `data/processed/genre_stats.csv`
- `data/processed/dataset_summary.json`

## 8. 执行策略

默认执行 MovieLens 下载、解压、清洗、融合 MovieLens 内部字段和特征构造。

TMDb 拉取必须显式开启：

- 小样本验证：`python scripts/prepare_movie_data.py --fetch-tmdb --tmdb-limit 20`
- 全量拉取：`python scripts/prepare_movie_data.py --fetch-tmdb --allow-full-tmdb`

全量拉取会产生约 9 千次 TMDb 请求，应在确认 token、网络和时间成本后执行。脚本会缓存成功结果，后续重复执行只补拉缺失记录。
