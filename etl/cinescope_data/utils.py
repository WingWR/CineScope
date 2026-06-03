from __future__ import annotations

import json
from typing import Any

import pandas as pd


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def missing_or_blank_count(frame: pd.DataFrame, column: str) -> int:
    values = frame[column]
    blank_count = values.astype("string").str.strip().eq("").fillna(False).sum()
    return int(values.isna().sum() + blank_count)

