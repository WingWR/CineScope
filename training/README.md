# 票房预测训练模块

本目录负责离线训练，产物输出到根目录 `models/artifacts/revenue_prediction/`。

## 目录职责

- `data/`：训练数据准备、切分和特征矩阵包装。
- `algorithms/`：XGBoost、LightGBM、加权融合逻辑。
- `evaluation/`：统一回归评估指标。
- `train_xgboost.py`：只训练 XGBoost。
- `train_lightgbm.py`：只训练 LightGBM。
- `train_ensemble.py`：同时训练 XGBoost + LightGBM，并在验证集上搜索最优加权比例。

## 运行方式

```powershell
python -m pip install -r training/requirements.txt
python -m training.train_ensemble
```

单独训练某个模型：

```powershell
python -m training.train_xgboost
python -m training.train_lightgbm
```

## 训练目标与特征

- 预测目标：`log1p(revenue)`，输出预测时会用 `expm1` 还原为美元票房。
- 核心特征：年份、片长、TMDb 热度、预算、评分统计、标签数、原始语言、电影类型。
- 数据过滤：只使用 `revenue > 0` 的电影训练。

## 主要产物

- `feature_schema.json`：训练时拟合出的特征列、类别取值和缺失值填充值。
- `xgboost_revenue.json`：XGBoost 模型。
- `lightgbm_revenue.txt`：LightGBM 模型。
- `ensemble_config.json`：验证集上选择出的 XGBoost/LightGBM 加权比例。
- `metrics.json`：单模型和融合模型的验证集指标。
