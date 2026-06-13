# CineScope

CineScope 是一个面向电影数据分析、检索、可视化与推荐的课程项目。项目以 MovieLens、TMDb、IMDb 等电影相关数据为基础，完成数据清洗、统计分析、推荐模型构建，并通过前端、统一后端和独立推荐服务提供交互式电影搜索、数据可视化、混合推荐和轻量 Agent/RAG 问答能力。

项目运行时主要由三个服务组成：

- 前端应用 `client`：React + Vite，默认运行在 `http://127.0.0.1:5173`
- 统一后端 `server`：FastAPI，默认运行在 `http://127.0.0.1:8000`
- 推荐服务 `recommender`：FastAPI，默认运行在 `http://127.0.0.1:3000`

推荐页的主要调用链是：

```text
client:5173 -> server:8000 -> recommender:3000
```

## 目录结构

```text
CineScope/
  client/         前端应用，包含电影搜索、推荐页、数据可视化页面
  server/         统一后端 API，负责电影检索、统计、RAG、Agent、推荐代理
  recommender/    独立推荐服务，提供内容推荐和协同过滤推荐
  data/           清洗后的最终数据与统计数据
  etl/            数据抽取、清洗、转换流程
  training/       模型训练相关代码
  models/         预测模型与模型产物
  visualization/  可视化实验与图表相关代码
  docs/           项目文档与补充数据说明
```

## 模块介绍

### 1. client 前端模块

`client/` 是用户直接访问的前端应用，使用 React + Vite 构建。它不直接读取本地 CSV 或推荐模型，而是通过统一后端 `server` 获取数据。

主要页面包括：

- Search：电影搜索、筛选、分页、排序、详情展示
- Recommend：内容推荐、协同过滤推荐、Agent 推荐，以及推荐结果详情展示
- Atlas：数据集概览、类型分布、预算趋势、票房气泡图、相关性视图等数据可视化模块

关键配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_TIMEOUT_MS=8000
```

前端默认访问后端 `server:8000`，所以启动前端前应先确保后端服务可用。

### 2. server 统一后端模块

`server/` 是面向前端的统一 API 层，使用 FastAPI 构建。它负责承接前端请求，并对接本地数据、推荐服务、统计服务、RAG 和 Agent 模块。

主要职责：

- 从 `data/final/movies.csv` 读取电影数据，提供搜索、筛选、排序和详情接口
- 从统计文件和电影数据中生成数据概览、类型分布、预算趋势、票房预算关系和相关性矩阵
- 通过 HTTP 调用 `recommender` 服务，向前端提供统一的推荐接口
- 从项目数据说明和质量报告中构建轻量 RAG 检索
- 支持项目问答和自然语言推荐 Agent；生成回答需要配置 DeepSeek Key

推荐服务地址由环境变量配置：

```env
RECOMMENDER_BASE_URL=http://127.0.0.1:3000
```

### 3. recommender 推荐服务模块

`recommender/` 是独立的推荐微服务，使用 FastAPI 对外提供推荐接口。它和 `server` 分离，后端通过 HTTP 调用它，而不是直接导入推荐算法代码。

主要职责：

- 构建并加载推荐模型产物
- 提供基于内容的电影相似推荐
- 提供基于用户评分行为的协同过滤推荐
- 将推荐结果封装为统一结构，包括电影信息、分数、推荐来源和推荐理由

推荐微服务方法：

- Content-based 推荐：
  - `overview` 文本使用 `TfidfVectorizer` + cosine similarity
  - 电影内容特征使用 `CountVectorizer` + cosine similarity
  - 两类相似度结果合并排序

- Collaborative 推荐：
  - item-based KNN：基于电影-用户评分矩阵寻找相似电影
  - user-based KNN：基于用户-电影评分矩阵寻找相似用户偏好
  - 当同时提供 `user_id` 和 `movie_name` 时，会合并两类候选结果

注意：推荐服务必须运行在 `3000` 端口。如果直接使用 `uvicorn recommender.app.main:app` 而不指定端口，uvicorn 默认会使用 `8000`，容易和统一后端冲突。

### 4. data 数据模块

`data/final/` 保存项目运行依赖的清洗后数据和统计数据。

主要文件：

```text
data/final/movies.csv
data/final/ratings.csv
data/final/tags.csv
data/final/genre_stats.csv
data/final/dataset_summary.json
data/final/quality_report.json
```

其中：

- `movies.csv`：电影主表，包含标题、年份、类型、评分统计、标签、简介、预算、票房、语言、海报等字段
- `ratings.csv`：用户评分数据
- `tags.csv`：用户标签数据
- `genre_stats.csv`：类型分布统计
- `dataset_summary.json`：数据集整体规模摘要
- `quality_report.json`：数据清洗和 TMDb/IMDb 匹配质量报告

### 5. etl / training / models / visualization / docs

这些目录主要用于项目的离线处理、实验和文档补充：

- `etl/`：数据抽取、清洗、转换和合并流程
- `training/`：模型训练或实验代码
- `models/`：模型文件和模型产物
- `visualization/`：可视化实验和图表相关代码
- `docs/`：项目说明、数据说明和补充文档

## 环境与依赖

Python 依赖：

```text
server/requirements.txt
recommender/requirements.txt
```

安装后端依赖：

```python
pip install -r server\requirements.txt
```

安装推荐服务依赖：

```python
pip install -r recommender\requirements.txt
```

安装前端依赖：

```powershell
cd client
npm install
```

## 项目运行

建议按下面顺序启动三个服务：推荐服务、统一后端、前端。三个服务需要分别占用一个终端窗口，并保持窗口不关闭。

### 1. 启动推荐服务 recommender

在项目根目录 `CineScope/` 下执行：

```powershell
python -m uvicorn recommender.app.main:app --host 127.0.0.1 --port 3000
```

如果端口 `3000` 无法访问，前端推荐页通常会出现 `HTTP 502` 或类似的推荐服务连接失败错误。

### 2. 启动统一后端 server

另开一个终端窗口，在项目根目录 `CineScope/` 下执行：

```powershell
python -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

### 3. 启动前端 client

再开一个终端窗口：

```powershell
cd client
npm run dev
```

浏览器访问：

```text
http://127.0.0.1:5173
```

此时前端会访问 `server:8000`，后端再按需访问 `recommender:3000`。
