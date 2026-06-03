# CineScope Server

`server/` 是 CineScope 的统一业务后端目录。当前只搭建模块化框架，不实现具体业务逻辑。

前端只连接这个业务后端；推荐服务、RAG、Agent、模型推理都由业务后端封装。

## 目录结构

```text
server/
  app/
    main.py

    core/
      config.py
      paths.py
      errors.py
      response.py

    shared/
      cache.py
      csv_loader.py
      json_loader.py
      text_utils.py

    modules/
      movies/
        router.py
        schemas.py
        service.py
        repository.py
        mappers.py

      recommendations/
        router.py
        schemas.py
        service.py
        recommender_client.py
        mappers.py

      stats/
        router.py
        schemas.py
        service.py
        repository.py

      revenue/
        router.py
        schemas.py
        service.py

      rag/
        router.py
        schemas.py
        service.py
        document_loader.py
        indexer.py
        retriever.py
        vector_store.py

      agent/
        router.py
        schemas.py
        service.py
        planner.py
        tools.py
        prompts.py

  requirements.txt
  README.md
```

## 模块职责

`movies`：电影搜索、筛选、排序、详情查询。后续读取 `data/final/movies.csv`，输出前端需要的 `Movie` 数据结构。

`recommendations`：统一推荐接口。后续适配已有 `recommender/` 微服务，并把推荐结果转换成前端的 `RecommendationItem`。

`stats`：前端 Atlas 可视化数据接口。后续读取 `dataset_summary.json`、`genre_stats.csv` 和 `movies.csv`，返回图表 JSON 序列。

`revenue`：票房预测模型封装。后续接入 `models/revenue_predictor.py`。

`rag`：知识库加载、索引构建和检索。后续可接入 ChromaDB、sentence-transformers，或先用轻量检索实现。

`agent`：自然语言 Agent 编排层。后续调用 RAG、电影搜索、推荐、票房预测等内部能力。

`core`：全局配置、路径、异常和统一响应。

`shared`：无业务含义的通用工具。

## 当前接口占位

当前 router 已经预留入口，但 service 均返回 `501 Not Implemented`：

```text
GET  /movies
GET  /movies/{movie_id}

POST /recommendations

GET  /stats/summary
GET  /stats/genres
GET  /stats/budget-trend
GET  /stats/revenue-budget
GET  /stats/correlations

POST /revenue/predict

POST /rag/index
POST /rag/search
GET  /rag/sources

POST /agent/chat
POST /agent/recommend
```

## 运行方式

安装依赖后可从项目根目录运行：

```powershell
E:\CodeEnv\Anaconda\python.exe -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

当前服务只用于确认模块边界和接口入口，业务实现会在后续步骤补齐。
