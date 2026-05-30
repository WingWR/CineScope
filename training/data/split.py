from __future__ import annotations

import numpy as np
import pandas as pd


def train_valid_split(
    df: pd.DataFrame,
    valid_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not 0 < valid_size < 1:
        raise ValueError("valid_size must be between 0 and 1")
    if len(df) < 5:
        raise ValueError("not enough rows to create a train/validation split")

    rng = np.random.default_rng(random_state)
    indices = rng.permutation(len(df))
    valid_count = max(1, int(round(len(df) * valid_size)))
    valid_indices = indices[:valid_count]
    train_indices = indices[valid_count:]
    return (
        df.iloc[train_indices].reset_index(drop=True),
        df.iloc[valid_indices].reset_index(drop=True),
    )
