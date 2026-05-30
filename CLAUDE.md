# CineScope

同济大学 计算机学院 软件工程 数据挖掘与数据分析 2026年春

## 项目当前状态

- 数据清洗流水线（ETL）已完成，位于 `etl/`
- 终版数据 7 个文件已产出，位于 `data/final/`
- 推荐算法、Agent/RAG、API、前端均未开始

## 数据概览

| 文件 | 行数 | 说明 |
|------|------|------|
| `data/final/movies.csv` | 9727 | 电影主表（44列，含 TMDb 详情） |
| `data/final/ratings.csv` | 100811 | 用户评分（610用户，稀疏度 98.3%） |
| `data/final/tags.csv` | 3678 | 用户标签 |
| `data/final/movie_features.csv` | 9727 | ML 特征表（genre one-hot + 文本 + 评分统计） |
| `data/final/genre_stats.csv` | 19 | 类型分布 |
| `data/final/dataset_summary.json` | — | 数据集概览 |
| `data/final/quality_report.json` | — | 数据质量报告 |

主键：`movie_id`（MovieLens ID），通用外键：`tmdb_id`

## 完整目录结构

```
CineScope/
│
├── etl/                          # 数据清洗（已完成）
│   ├── prepare_movie_data.py     #   入口脚本
│   └── cinescope_data/           #   清洗流水线包
│       ├── cli.py                #   CLI 参数
│       ├── config.py             #   路径 & 环境变量
│       ├── movielens.py          #   MovieLens 下载/解析
│       ├── pipeline.py           #   流水线编排
│       ├── transform.py          #   融合 & 特征工程
│       ├── outputs.py            #   输出 & 质量报告
│       ├── tmdb_client.py        #   TMDb API
│       └── utils.py              #   工具函数
│
├── data/                         # 数据存储（ETL 产出）
│   ├── final/                    #   终版数据（Git 追踪）
│   ├── raw/                      #   原始数据（Git 忽略）
│   ├── interim/                  #   中间数据（Git 忽略）
│   └── processed/                #   加工数据（Git 忽略）
│
├── models/                       # 模型推理 + 训练产物
│   ├── data_loader.py            #   统一数据加载入口
│   ├── content_based.py          #   内容推荐推理（genre+TF-IDF 相似度）
│   ├── collaborative.py          #   协同过滤推理（SVD 矩阵分解）
│   ├── hybrid.py                 #   混合推荐编排 + 冷启动三级降级
│   ├── svd_model.pkl             #   训练好的 SVD 模型（Git 忽略）
│   ├── tfidf_vectorizer.pkl      #   TF-IDF 向量化器（Git 忽略）
│   ├── content_sim_matrix.npy    #   内容相似度矩阵（Git 忽略）
│   ├── user_embeddings.npy       #   用户隐向量（Git 忽略）
│   └── movie_embeddings.npy      #   电影隐向量（Git 忽略）
│
├── training/                     # 离线训练脚本
│   ├── train_cf.py               #   训练 SVD，网格搜索最佳 k
│   ├── train_content.py          #   计算 TF-IDF + 内容相似度矩阵
│   ├── evaluate.py               #   交叉验证、RMSE、Precision@K
│   └── generate_insights.py      #   ML 分析结果 → 自然语言洞察 → 入向量库
│
├── visualization/                # 数据可视化 & EDA
│   ├── 01_eda_overview.ipynb     #   数据全貌：分布、缺失、统计
│   ├── 02_eda_behavior.ipynb     #   用户行为分析
│   ├── 03_eda_content.ipynb      #   电影内容分析（类型、标签、文本）
│   └── viz_utils.py              #   画图工具函数（配色、字体、导出）
│
├── backend/                      # 后端服务
│   ├── api.py                    #   FastAPI 路由
│   ├── agent/                    #   Agent + RAG 对话推荐
│   │   ├── __init__.py
│   │   ├── prompts.py            #     System prompt 模板
│   │   ├── tools.py              #     Agent 工具（调 models/ 里的函数）
│   │   ├── retriever.py          #     向量检索
│   │   ├── rag.py                #     RAG 编排：检索 → 拼 prompt → 生成
│   │   └── agent.py              #     Agent 主循环
│   └── vector_store/             #   向量库持久化（Git 忽略）
│
├── frontend/                     # React 前端（后期）
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docs/                         # 文档
│   └── data/
│       ├── 数据处理介绍.md
│       ├── 数据字段说明.md
│       └── 数据清洗计划.md
│
├── requirements.txt
├── README.md
├── CLAUDE.md
├── LICENSE
└── .gitignore
```

## 模块依赖关系

```
frontend/ ──→ backend/ ──→ models/ ──→ data/
                 │             │
                 │        training/ (离线跑，产出到 models/)
                 │
            visualization/ ──→ data/ (只读数据，独立于其他模块)
```

- `models/` 是核心推理层，被 `backend/` 和 `training/` 共同依赖
- `training/` 离线运行，产出模型文件到 `models/` 目录
- `visualization/` 独立模块，只读 `data/final/`，不依赖其他任何模块
- `backend/agent/tools.py` 直接调用 `models/` 里的函数作为 Agent 工具

## 架构核心原则

### 三层架构
```
前端 (React) → 后端 (FastAPI) → 模型推理 (models/) → 数据 (data/final/)
```

### 训练与推理分离
- `training/` → 离线跑，产出模型文件到 `models/`
- `models/` → 在线加载模型文件，做预测（推理代码 + 序列化模型放一起）
- `visualization/` → 实验探索，跑通后有复用价值的逻辑抽到 `models/` 或 `viz_utils.py`

### 两种推荐路径互补
| 路径 | API 接口 | 场景 | 延迟 |
|------|----------|------|------|
| 传统 ML | `GET /api/recommend/{user_id}` | 页面自动推荐、"猜你喜欢" | 毫秒级 |
| Agent + RAG | `POST /api/chat` | 用户主动对话、自然语言交互 | 秒级 |

### ML + RAG 协作模式
```
离线：training/generate_insights.py → 洞察文本 → embedding → 向量库
在线：用户消息 → 向量检索命中洞察 → 拼入 prompt → LLM 生成精准回复
```
Agent 拿到的不是 LLM 凭空猜的用户偏好，而是 ML 真实分析出的结论。

### 冷启动三级降级（models/hybrid.py）
```
用户历史 ≥ 10 条 → 协同过滤 SVD
用户历史 1-9 条  → 内容推荐（genre 向量匹配）
用户历史 = 0 条  → 热门推荐（weighted_rating × log(rating_count)）
```

## 6 步实现计划

| 步骤 | 内容 | 涉及文件 | 依赖 |
|------|------|----------|------|
| 1 | 基础设施：requirements.txt + data_loader.py + EDA | `requirements.txt`, `models/data_loader.py`, `visualization/` | 无 |
| 2 | 内容推荐：genre+TF-IDF 相似度 | `models/content_based.py`, `training/train_content.py` | 步骤1 |
| 3 | 协同过滤：SVD 矩阵分解 | `models/collaborative.py`, `training/train_cf.py` | 步骤1 |
| 4 | 混合 + 冷启动 | `models/hybrid.py` | 步骤2+3 |
| 5 | Agent + RAG | `backend/agent/*` (5个文件), `training/generate_insights.py` | 步骤4 |
| 6 | API 层 | `backend/api.py` | 步骤4+5 |

步骤 2 和 3 可并行。

## API 接口清单

```
GET  /api/movies/{movie_id}        # 电影详情
GET  /api/movies/search?q=&genre=  # 搜索 + 过滤
GET  /api/recommend/{user_id}      # 无感推荐（纯 ML，毫秒级）
POST /api/chat                     # 对话推荐（Agent + RAG，秒级）
GET  /api/genres                   # 类型列表
```

## 技术栈

- 数据处理：pandas, numpy, scipy
- ML/推荐：scikit-learn, scikit-surprise
- 文本向量化：scikit-learn TfidfVectorizer, sentence-transformers
- 向量库：chromadb
- API：fastapi, uvicorn
- LLM：openai SDK（或兼容接口）
- 前端：React（后期）

## 关键设计决策

1. 所有模块通过 `models/data_loader.py` 读数据，不直接读 CSV
2. Agent 不产数据只消费数据，推荐逻辑全在 `models/` 里
3. ML 分析结果通过 `training/generate_insights.py` 转为文本洞察，embedding 后存入向量库供 RAG 检索
4. 前端两种推荐入口并存：自动推荐区（`/api/recommend`）+ 对话助手区（`/api/chat`）
5. `models/` 同时存放推理代码和序列化模型文件，两者紧密耦合放一起
6. `visualization/` 独立于其他模块，只读数据，不参与推理或训练
7. Git 分支策略：`feature/algorithm`（当前分支）→ `develop` → `main`
