# CineScope

同济大学 计算机学院 软件工程 数据挖掘与数据分析 2026年春

## 项目当前状态

- 数据清洗流水线（ETL）已完成，位于 `etl/`
- 终版数据 6 个文件已产出，位于 `data/final/`
- 票房预测模型（XGBoost + LightGBM ensemble）已完成训练，产物位于 `models/artifacts/revenue_prediction/`
- 数据可视化已完成（6 张 SVG 图表），位于 `visualization/graph/`
- 推荐层已实现为独立微服务，位于 `recommender/`，包含内容推荐、协同过滤、离线 artifacts 构建、demo 和 HTTP 接口
- 前端框架已搭建（React + TypeScript + Vite），当前页面仍以骨架/占位为主，等待业务后端与推荐服务对接
- 业务后端聚合 API、Agent/RAG、推荐效果评估与自动化测试尚未完成

## 数据概览

| 文件 | 行数 | 说明 |
|------|------|------|
| `data/final/movies.csv` | 9727 | 电影主表（20 列提交字段，含 TMDb 详情 + 预算/票房） |
| `data/final/ratings.csv` | 100811 | 用户评分（610 用户，稀疏度 98.3%） |
| `data/final/tags.csv` | 3678 | 用户标签（已去除 tag 字段） |
| `data/final/genre_stats.csv` | 19 | 类型分布 |
| `data/final/dataset_summary.json` | — | 数据集概览 |
| `data/final/quality_report.json` | — | 数据质量报告（含提交元数据） |

主键：`movie_id`（MovieLens ID），通用外键：`tmdb_id`

> 注：`movie_features.csv` 已按要求从最终提交中移除。

## 完整目录结构

```
CineScope/
│
├── etl/                          # 数据清洗（已完成）
│   ├── prepare_movie_data.py     #   入口脚本
│   ├── requirements.txt          #   ETL 依赖
│   └── cinescope_data/           #   清洗流水线包
│       ├── cli.py                #   CLI 参数
│       ├── config.py             #   路径 & 环境变量
│       ├── movielens.py          #   MovieLens 下载/解析
│       ├── pipeline.py           #   流水线编排
│       ├── transform.py          #   融合 & 特征工程
│       ├── outputs.py            #   输出 & 质量报告
│       ├── tmdb_client.py        #   TMDb API
│       ├── submission.py         #   提交数据准备 & 预算/票房字段注入
│       ├── utils.py              #   工具函数
│       └── __init__.py
│
├── data/                         # 数据存储（ETL 产出）
│   ├── final/                    #   终版数据（Git 追踪）
│   ├── raw/                      #   原始数据（Git 忽略）
│   ├── interim/                  #   中间数据（Git 忽略）
│   └── processed/                #   加工数据（Git 忽略）
│
├── models/                       # 模型推理 + 训练产物
│   ├── __init__.py
│   ├── data_loader.py            #   统一数据加载入口（load_movies / load_ratings / load_tags）
│   ├── revenue_features.py       #   票房预测特征工程（特征 schema 拟合 & 转换）
│   ├── revenue_predictor.py      #   票房预测推理（XGBoost + LightGBM ensemble）
│   └── artifacts/                #   训练产物（Git 追踪）
│       └── revenue_prediction/
│           ├── feature_schema.json     #   特征列、类别取值、缺失值填充
│           ├── xgboost_revenue.json    #   XGBoost 模型
│           ├── lightgbm_revenue.txt    #   LightGBM 模型
│           ├── ensemble_config.json    #   加权融合权重
│           └── metrics.json            #   验证集评估指标
│
├── training/                     # 离线训练脚本（已完成）
│   ├── __init__.py
│   ├── cli.py                    #   命令行参数共享
│   ├── config.py                 #   路径、超参数常量
│   ├── pipeline.py               #   训练流水线编排（数据准备 → 训练 → 评估）
│   ├── train_revenue.py          #   便捷入口 → train_ensemble
│   ├── train_ensemble.py         #   同时训练 XGBoost + LightGBM，搜索最优加权
│   ├── train_xgboost.py          #   单独训练 XGBoost
│   ├── train_lightgbm.py         #   单独训练 LightGBM
│   ├── README.md                 #   训练模块说明
│   ├── requirements.txt          #   xgboost, lightgbm
│   ├── algorithms/               #   算法实现
│   │   ├── __init__.py
│   │   ├── xgboost_model.py      #     XGBoost 训练/预测
│   │   ├── lightgbm_model.py     #     LightGBM 训练/预测
│   │   └── ensemble.py           #     加权融合 & 最优权重搜索
│   ├── data/                     #   训练数据准备
│   │   ├── __init__.py
│   │   ├── loader.py             #     加载 & 列校验
│   │   ├── features.py           #     特征矩阵构建（委托 models/revenue_features.py）
│   │   └── split.py              #     训练/验证集划分
│   └── evaluation/               #   评估指标
│       ├── __init__.py
│       └── metrics.py            #     RMSE/MAE/MAPE/R²（log1p 空间 + 原始空间）
│
├── visualization/                # 数据可视化 & EDA（已完成）
│   ├── code/                     #   可视化生成脚本（纯 Python，输出 SVG）
│   │   ├── common_svg.py         #     共享工具（数据加载、颜色、比例尺、SVG 输出）
│   │   ├── budget_year_average_curve.py        #   预算/票房年均曲线
│   │   ├── language_revenue_tower.py           #   语言-票房塔状图
│   │   ├── revenue_budget_bubble.py            #   票房 vs 预算气泡图
│   │   ├── revenue_budget_popularity_correlation_heatmap.py  #   相关性热力图
│   │   ├── revenue_popularity_bubble.py        #   票房 vs 热度气泡图
│   │   └── revenue_year_bubble.py             #   票房 vs 年份气泡图
│   └── graph/                    #   输出的 SVG 图表（6 张）
│
├── recommender/                  # 推荐微服务（已实现，可运行；待补评估与测试）
│   ├── README.md                 #   推荐服务说明、构建命令、运行命令、接口列表
│   ├── requirements.txt          #   pandas / scipy / scikit-learn / FastAPI 等依赖
│   ├── app/                      #   FastAPI HTTP 层
│   │   ├── main.py               #     app 创建与路由挂载
│   │   ├── routes.py             #     /health、/recommend/content、/recommend/collaborative
│   │   ├── schemas.py            #     Pydantic 响应模型
│   │   └── settings.py           #     数据路径、artifact 路径、默认 top_k / neighbor_k
│   ├── core/                     #   业务编排与通用排序工具
│   │   ├── service.py            #     加载数据与推荐器，输出统一推荐响应
│   │   ├── ranking.py            #     分数归一化、加权融合、Top-K
│   │   └── exceptions.py         #     Movie/User/Artifact 异常
│   ├── data/                     #   推荐数据加载与预处理
│   │   ├── loaders.py            #     load_movies / load_ratings
│   │   └── preprocess.py         #     标题归一化、JSON 列解析、推荐结果转换
│   ├── algorithms/
│   │   ├── content_based/        #     TF-IDF + CountVectorizer 内容相似推荐
│   │   │   ├── builder.py        #       构建内容推荐 artifacts
│   │   │   ├── features.py       #       overview 文本与 content soup 构造
│   │   │   └── recommender.py    #       内容相似度召回与合并
│   │   └── collaborative/        #     item KNN + user KNN 协同过滤
│   │       ├── builder.py        #       构建评分矩阵与 KNN artifacts
│   │       ├── item_knn.py       #       基于电影-用户评分向量的相似电影召回
│   │       ├── user_knn.py       #       基于近邻用户的个性化打分
│   │       └── recommender.py    #       协同过滤编排、已看过滤、热门兜底
│   ├── artifacts/                #   已生成推荐 artifacts（vectorizer、矩阵、KNN 模型、索引）
│   │   ├── content_based/
│   │   └── collaborative/
│   └── scripts/                  #   build_all / build_content / build_collaborative / demo
│
├── frontend/                     # React 前端（框架已搭建，页面占位，等待 API）
│   ├── package.json              #   React 19 + TypeScript 6 + Vite 8 + React Router 7
│   ├── vite.config.ts
│   ├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
│   ├── eslint.config.js
│   ├── index.html
│   ├── public/
│   │   └── favicon.svg
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── App.css
│       ├── index.css
│       ├── routes.tsx            #   路由定义（6 个页面）
│       ├── api/                  #   API 客户端层（已就绪，等待后端）
│       │   ├── client.ts         #     fetch 封装、错误类型、VITE_API_BASE_URL 配置
│       │   ├── movies.ts         #     /api/movies 系列
│       │   ├── recommendations.ts #    /api/recommendations 系列
│       │   └── stats.ts          #     /api/stats 系列
│       ├── types/
│       │   └── api.ts            #     API 类型定义
│       ├── components/           #   可复用组件
│       │   ├── EmptyState.tsx
│       │   ├── PageHeader.tsx
│       │   └── StatusPanel.tsx
│       ├── layout/
│       │   └── AppShell.tsx      #   全局布局（侧边栏 + 顶栏 + 内容区）
│       └── pages/                #   页面（当前均为占位状态）
│           ├── DashboardPage.tsx       #   首页概览
│           ├── MoviesPage.tsx          #   电影列表（搜索/筛选/排序 UI）
│           ├── MovieDetailPage.tsx     #   电影详情
│           ├── GenresPage.tsx          #   类型分布
│           ├── RecommendationsPage.tsx #   推荐结果
│           ├── DataAboutPage.tsx       #   数据说明
│           └── NotFoundPage.tsx        #   404
│
├── docs/                         # 文档
│   └── data/
│       ├── 数据处理介绍.md
│       ├── 数据字段说明.md
│       └── 数据清洗计划.md
│
├── README.md
├── CLAUDE.md
├── LICENSE
└── .gitignore
```

## 模块依赖关系

```
frontend/ ──→ backend/ (未开始) ──→ models/ ──→ data/
                    │                   │
                    │              training/ (已完成，离线产出到 models/artifacts/)
                    │
                    └──→ recommender/ (已实现为独立微服务) ──→ data/final/

visualization/ ──→ data/final/ (只读数据，独立模块)
```

- `models/` 是核心推理层，目前提供票房预测能力
- `training/` 离线运行，产出模型文件到 `models/artifacts/revenue_prediction/`
- `recommender/` 是独立推荐层，目前已提供内容推荐、协同过滤和推荐 HTTP 接口，业务后端后续通过 HTTP 调用它
- `visualization/` 独立模块，只读 `data/final/`，输出 SVG 图表，不依赖其他任何模块
- `frontend/` 已搭建 React 框架，API 层通过 `VITE_API_BASE_URL` 连接后端（尚未对接）

## 架构核心原则

### 三层架构（规划）
```
前端 (React) → 后端 (FastAPI) → 模型推理 (models/) → 数据 (data/final/)
                             └→ 推荐微服务 (recommender/) → 数据/推荐 artifacts
```

### 训练与推理分离
- `training/` → 离线跑，产出模型文件到 `models/artifacts/`
- `models/` → 在线加载模型文件，做预测（推理代码 + 序列化产物放一起，但产物在 `artifacts/` 子目录）
- `visualization/` → 实验探索，通过 `common_svg.py` 复用绘图工具

### 训练产出分层
```
training/algorithms/  → 模型训练逻辑（无状态函数）
training/data/        → 特征准备（委托 models/revenue_features.py）
training/pipeline.py  → 编排：数据加载 → 特征构建 → 训练 → 评估 → 保存产物
models/artifacts/     → 序列化产物（Git 追踪，推理时直接加载）
models/revenue_predictor.py → 推理入口，加载产物并提供 predict_frame()
```

### 票房预测架构

- **目标变量**：`log1p(revenue)`（训练时），推理时通过 `expm1` 还原为美元
- **特征**（66 列）：14 个数值特征（年份、片长、TMDb 热度、预算、评分统计、标签数等）+ 语言 one-hot + 类型 one-hot
- **算法**：XGBoost + LightGBM 加权融合（默认权重 XGBoost 0.88, LightGBM 0.12，在验证集 RMSE(log) 上搜索最优权重）
- **验证集指标**：RMSE_log ≈ 1.27, R²_log ≈ 0.65
- **训练过滤**：仅使用 `revenue > 0` 的行（有效训练行 6235，训练集 4988，验证集 1247）

### 推荐层架构

- **服务形态**：`recommender/` 是独立推荐微服务，不直接塞进未来业务后端；后端应通过 HTTP 调用。
- **内容推荐**：`overview` 文本使用 `TfidfVectorizer`，电影内容汤使用 `CountVectorizer`，两路 cosine similarity 按权重合并。
- **内容特征**：当前使用 `title_clean`、`overview`、`genres_json`、`top_tags_json`、`original_language`；如果 ETL 后续补导演、演员、关键词，可在 `recommender/algorithms/content_based/features.py` 中加入。
- **协同过滤**：构建 movie-user 与 user-movie 稀疏评分矩阵；item KNN 提供相似电影，user KNN 提供个性化候选。
- **混合方式**：协同过滤接口在同时传入 `user_id` 与 `movie_name` 时合并 item KNN 与 user KNN；只传 `user_id` 时返回纯个性化推荐。
- **兜底策略**：当近邻候选不足时，按 `rating_count` 与 `rating_mean` 计算贝叶斯热门分数进行补足。
- **已生成 artifacts**：内容推荐覆盖 9727 部电影；协同过滤覆盖 9727 部电影、610 个用户、100811 条评分。
- **当前缺口**：尚未补推荐评估指标（Precision@K / Recall@K / NDCG@K / Coverage）、自动化测试、统一 hybrid 接口与更强的标题模糊匹配。

### 推荐服务运行命令

从仓库根目录运行：

```powershell
E:\CodeEnv\Anaconda\python.exe -m recommender.scripts.build_all
E:\CodeEnv\Anaconda\python.exe -m recommender.scripts.demo
E:\CodeEnv\Anaconda\python.exe -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 3000
```

### 推荐服务接口

```
GET /health
GET /recommend/content?movie_name=Toy Story&top_k=10
GET /recommend/collaborative?user_id=1&movie_name=Toy Story&top_k=10
GET /recommend/collaborative?user_id=1&top_k=10
```

## 当前分支

- 当前分支：`feature/recommend`
- 分支策略：`feature/*` → `develop` → `main`

## 已完成 vs 待实现

| 模块 | 状态 | 说明 |
|------|------|------|
| ETL 数据清洗 | ✅ 完成 | 含预算/票房字段注入（TMDb + IMDB 回退匹配） |
| 数据可视化 | ✅ 完成 | 6 张 SVG 图表，覆盖票房/预算/年份/语言/热度维度 |
| 票房预测模型 | ✅ 完成 | XGBoost + LightGBM ensemble，训练 & 推理代码就绪 |
| 推荐层 | ✅ 可运行 | 内容推荐、协同过滤、artifacts、demo、推荐 HTTP 接口已实现；待补评估/测试/统一 hybrid |
| 前端框架 | ⚠️ 骨架完成 | React + TS + Vite、路由、布局、API 层已搭建；业务页面仍为占位 |
| 业务后端 API | ❌ 未开始 | 统一电影/统计/票房预测/推荐的后端聚合 API 待搭建 |
| 推荐评估与测试 | ⚠️ 待完善 | 尚无 Precision@K、Recall@K、NDCG、Coverage 和自动化测试 |
| Agent + RAG | ❌ 未开始 | 对话推荐待实现 |

## 前端 API 接口（前端已定义，后端待实现）

```
GET  /api/movies?query=&genre=&yearFrom=&yearTo=&sortBy=&sortDirection=&page=&pageSize  # 电影列表（分页+搜索+过滤+排序）
GET  /api/movies/{movie_id}        # 电影详情
GET  /api/movies/top-rated         # 高分电影
GET  /api/movies/popular           # 热门电影
GET  /api/recommendations/{movie_id}  # 相似电影推荐（可选 movieId，不传则为热门）
GET  /api/stats/summary            # 数据集概览
GET  /api/stats/genres             # 类型分布
```

## 技术栈

- 数据处理：pandas, numpy
- ML/训练：xgboost, lightgbm
- 推荐/微服务：scipy, scikit-learn, joblib, FastAPI, uvicorn, pydantic
- 可视化：纯 Python 生成 SVG（无 notebook 依赖）
- 前端：React 19, TypeScript 6, Vite 8, React Router 7, Lucide React
- 待引入：chromadb, sentence-transformers, openai SDK（用于 Agent/RAG）

## 关键设计决策

1. 票房预测相关模块通过 `models/data_loader.py` 读数据，推荐服务通过 `recommender/data/loaders.py` 读终版 CSV
2. 特征工程逻辑在 `models/revenue_features.py` 中集中管理，training 和 inference 共用同一份代码
3. 训练产物（模型文件 + schema + config）放在 `models/artifacts/`，Git 追踪，保证推理可复现
4. 推荐层作为独立微服务维护，不与未来业务后端强耦合；业务后端通过 HTTP 调用推荐能力
5. 推荐 artifacts 放在 `recommender/artifacts/`，由 `recommender/scripts/build_all.py` 从 `data/final/` 离线生成
6. `visualization/` 独立于其他模块，只读 `data/final/`，不参与推理或训练
7. 前端在无业务后端情况下可独立开发运行（`npm run dev`），当前数据区域展示占位状态
8. `etl/cinescope_data/submission.py` 负责提交数据的最终裁剪（移除 `movie_features.csv`、去除 `tags.tag` 列、注入预算/票房字段）
9. Git 分支策略：`feature/recommend`（当前分支）→ `develop` → `main`
