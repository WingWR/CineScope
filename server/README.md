# CineScope Server

`server/` 是统一的 FastAPI 后端，负责承接前端的电影检索、统计、推荐、轻量 RAG 和可选的 DeepSeek Agent。

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

## Modules

- `movies`：读取 `data/final/movies.csv`，提供搜索、筛选、排序和详情
- `stats`：提供摘要卡片、类型分布、预算趋势、预算/票房散点和相关性矩阵
- `recommendations`：对接 `recommender/` 的 `content` / `collaborative`，并增强 `agent-ready`
- `rag`：从 `data/final/` 与 `docs/data/` 构建轻量本地检索
- `agent`：区分“项目问答”和“电影推荐”，可选调用 DeepSeek，没有 Key 时自动降级

## RAG Data Sources

本地 RAG 只读取这些现有文件：

```text
data/final/dataset_summary.json
data/final/quality_report.json
data/final/genre_stats.csv
data/final/movies.csv
docs/data/*.md
```

不会逐行索引 `ratings.csv` 或 `tags.csv`。

## Environment Variables

推荐在项目根目录使用 `.env`：

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

- 后端会优先自动读取 `D:\205zd\Desktop\CS\.env`
- 模板文件在 `D:\205zd\Desktop\CS\.env.example`
- `DEEPSEEK_API_KEY` 留空时，自动走本地规则版 Agent
- `AGENT_USE_LLM=false` 时，即使有 Key 也不会调用 DeepSeek
- `RECOMMENDER_BASE_URL` 是推荐服务地址

## Local Setup

安装依赖：

```powershell
py -m pip install -r server/requirements.txt
py -m pip install -r recommender/requirements.txt
```

先启动推荐服务：

```powershell
py -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 8010
```

再启动统一后端：

```powershell
py -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

前端示例配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

默认 CORS 放行：

```text
http://127.0.0.1:5173
http://localhost:5173
```

## Manual Smoke Checks

### RAG

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"Toy Story","topK":3}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"dataset rating count","topK":3}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/rag/search -ContentType 'application/json' -Body '{"query":"high rated sci-fi","topK":3}'
```

### Agent Project QA

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/agent/chat -ContentType 'application/json' -Body '{"message":"这个数据集有多少电影和评分？"}'
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

- `recommender/artifacts/` 需要存在
- 当前 RAG 是轻量内存版，不依赖 FAISS、Chroma、LangChain 或外部 embedding 服务
- DeepSeek 只负责组织答案和解释，不负责决定电影 ID、电影标题、评分或统计结果
