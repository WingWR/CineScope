# CineScope Server

`server/` 是 CineScope 的统一业务后端目录。当前只搭建模块化框架，不实现具体业务逻辑。

前端只连接这个业务后端。`server` 对外只暴露前端契约中需要的接口；推荐服务、RAG、Agent、模型推理都作为后端内部模块被业务接口编排调用。

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
        schemas.py
        service.py

      rag/
        schemas.py
        service.py
        document_loader.py
        indexer.py
        retriever.py
        vector_store.py

      agent/
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

`recommendations`：统一推荐接口。后续适配已有 `recommender/` 微服务，并把推荐结果转换成前端的 `RecommendationItem`。`agent-ready` 模式也通过这个接口进入后端，不额外暴露 `/agent`。

`stats`：前端 Atlas 可视化数据接口。后续读取 `dataset_summary.json`、`genre_stats.csv` 和 `movies.csv`，返回图表 JSON 序列。

`revenue`：内部票房预测能力模块。后续接入 `models/revenue_predictor.py`，供推荐或 Agent 编排使用，不直接暴露给前端。

`rag`：内部知识库加载、索引构建和检索模块。后续可接入 ChromaDB、sentence-transformers，或先用轻量检索实现，不直接暴露给前端。

`agent`：内部自然语言 Agent 编排层。后续调用 RAG、电影搜索、推荐、票房预测等内部能力，并通过 `/recommendations` 的 `agent-ready` 模式对前端提供结果。

`core`：全局配置、路径、异常和统一响应。

`shared`：无业务含义的通用工具。

## 当前接口占位

当前只预留前端已依赖的公开接口入口，service 均返回 `501 Not Implemented`：

```text
GET  /movies
GET  /movies/{movieId}

POST /recommendations

GET  /stats/summary
GET  /stats/genres
GET  /stats/budget-trend
GET  /stats/revenue-budget
GET  /stats/correlations
```

## 运行方式

安装依赖后可从项目根目录运行：

```powershell
E:\CodeEnv\Anaconda\python.exe -m uvicorn server.app.main:app --host 127.0.0.1 --port 8000
```

当前服务只用于确认模块边界和接口入口，业务实现会在后续步骤补齐。
