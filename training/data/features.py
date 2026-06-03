from __future__ import annotations

import numpy as np
import pandas as pd

from models.revenue_features import (
    RevenueFeatureSchema,
    filter_revenue_training_rows,
    fit_revenue_feature_schema,
    make_revenue_target,
    save_revenue_feature_schema,
    transform_revenue_features,
)


def build_feature_matrix(
    train_df: pd.DataFrame,
    valid_df: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray, RevenueFeatureSchema]:
    schema = fit_revenue_feature_schema(train_df)
    x_train = transform_revenue_features(train_df, schema)
    y_train = make_revenue_target(train_df)
    x_valid = transform_revenue_features(valid_df, schema)
    y_valid = make_revenue_target(valid_df)
    return x_train, y_train, x_valid, y_valid, schema


__all__ = [
    "RevenueFeatureSchema",
    "build_feature_matrix",
    "filter_revenue_training_rows",
    "save_revenue_feature_schema",
]
