# CineScope

CineScope 是一个面向电影数据分析、检索、可视化与推荐的课程项目。项目以 MovieLens / TMDB / IMDb 等电影相关数据为基础，完成数据清洗、统计分析、推荐模型构建，并通过前后端应用提供交互式查询、推荐和可视化体验。

项目包含三个主要运行服务：

- 前端应用：React + Vite，默认运行在 `http://127.0.0.1:5173`
- 统一后端：FastAPI，默认运行在 `http://127.0.0.1:8000`
- 推荐服务：FastAPI，默认运行在 `http://127.0.0.1:3000`

## 项目模块

```text
CineScope/
  client/         前端应用，包含电影搜索、推荐页、可视化页面
  server/         统一后端 API，负责前端请求、电影检索、统计、RAG、Agent、推荐代理
  recommender/    独立推荐服务，提供内容推荐和协同过滤推荐
  data/           清洗后的最终数据与统计数据
  etl/            数据抽取、清洗、转换流程
  training/       模型训练相关代码
  models/         预测模型与模型产物
  visualization/  可视化实验与图表相关代码
  docs/           项目文档与补充数据说明
```

### client

前端页面使用 React 构建，主要页面包括：

- Search：电影搜索、筛选、分页、排序、详情展示
- Recommend：内容推荐、协同过滤推荐、Agent 推荐，以及推荐结果详情展示
- Atlas：数据集概览、类型分布、预算趋势、票房气泡图、相关性视图等可视化模块

### server

统一后端负责承接前端请求，并对接本地数据、推荐服务和 Agent/RAG 模块。主要接口包括：

- `GET /health`
- `GET /movies`
- `GET /movies/{movieId}`
- `POST /recommendations`
- `GET /stats/summary`
- `GET /stats/genres`
- `GET /stats/budget-trend`
- `GET /stats/revenue-budget`
- `GET /stats/correlations`
- `POST /rag/search`
- `POST /agent/chat`
- `POST /agent/recommend`

### recommender

推荐服务是独立的 FastAPI 服务，统一运行在 `3000` 端口。它提供：

- 内容推荐：基于电影简介、类型、标签、语言等特征计算相似电影
- 协同过滤推荐：基于用户评分矩阵和 KNN 模型生成推荐
- 推荐结果封装：返回电影、分数、推荐理由和来源

后端 `server` 会通过 HTTP 调用该服务，而不是直接导入推荐代码。

## 运行环境

推荐使用本机已有的 conda `data` 环境运行后端和推荐服务。

前端需要 Node.js 与 npm。

Python 依赖文件：

```text
server/requirements.txt
recommender/requirements.txt
```

前端依赖文件：

```text
client/package.json
```

## 配置说明

根目录提供 `.env.example`，推荐复制为 `.env` 后按需修改：

```env
RECOMMENDER_BASE_URL=http://127.0.0.1:3000

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT_SECONDS=30

AGENT_USE_LLM=true
AGENT_MAX_CONTEXT_CHARS=5000
AGENT_MAX_RAG_RESULTS=5

CINESCOPE_APP_NAME=CineScope Server
CINESCOPE_VERSION=0.1.0
CINESCOPE_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

前端使用 `client/.env`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_TIMEOUT_MS=8000
```

端口约定：

- `5173`：前端 Vite 服务
- `8000`：统一后端 server
- `3000`：独立推荐服务 recommender

注意：如果使用 `uvicorn recommender.app.main:app` 启动推荐服务，必须显式加上 `--port 3000`，否则 uvicorn 默认会使用 `8000`，与后端 server 冲突。

## 项目运行

以下命令均在项目根目录 `CineScope/` 下执行，除非特别说明。

### 1. 安装依赖

安装后端依赖：

```powershell
E:\CodeEnv\Anaconda\envs\data\python.exe -m pip install -r server\requirements.txt
```

安装推荐服务依赖：

```powershell
E:\CodeEnv\Anaconda\envs\data\python.exe -m pip install -r recommender\requirements.txt
```

安装前端依赖：

```powershell
cd client
npm install
```

### 2. 启动推荐服务

推荐服务必须先启动，并保持窗口不关闭：

```powershell
E:\CodeEnv\Anaconda\envs\data\python.exe -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 3000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:3000/health
```

如果看到 `artifacts_ready: true`，说明推荐模型产物可用。

### 3. 启动统一后端

另开一个终端窗口：

```powershell
E:\CodeEnv\Anaconda\envs\data\python.exe -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. 启动前端

另开一个终端窗口：

```powershell
cd client
npm run dev
```

浏览器访问：

```text
http://127.0.0.1:5173
```

## 推荐接口检查

推荐页依赖 `server -> recommender` 的调用链。可以用下面的请求检查链路：

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/recommendations `
  -ContentType "application/json" `
  -Body '{"mode":"content","prompt":"","seedMovieName":"Toy Story","userId":"1","topK":3}'
```

如果返回 `items` 列表，说明前端推荐页可以正常获取数据。

如果前端显示 `The API did not return usable data (HTTP 502)`，通常表示：

- `server:8000` 正常运行
- 但 `recommender:3000` 没有运行，或推荐服务启动到了错误端口

此时请先检查：

```powershell
Invoke-RestMethod http://127.0.0.1:3000/health
```

## 项目功能

### 电影搜索

- 按标题、类型、标签进行搜索
- 按语言、评分、类型过滤电影
- 支持按热度、评分、票房、年份排序
- 支持分页展示
- 点击电影后显示详情、评分、票房、预算、标签等信息

### 推荐系统

- Content 推荐：根据种子电影推荐相似电影
- Collaborative 推荐：结合用户评分行为生成推荐
- Agent 推荐：允许使用自然语言描述偏好，再生成推荐结果
- 推荐结果支持点击选中，并在右侧展示电影详情

### 数据可视化

- 数据集概览
- 类型分布
- 年度预算趋势
- 预算与票房气泡图
- 指标相关性视图
- 多视图 Atlas 切换

### RAG 与 Agent

- 可对项目数据说明、质量报告等文档进行轻量检索
- 支持项目问答
- 支持基于自然语言偏好的电影推荐
