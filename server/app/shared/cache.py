from __future__ import annotations

from functools import lru_cache
from typing import Callable, TypeVar


T = TypeVar("T")


def cached(function: Callable[..., T]) -> Callable[..., T]:
    return lru_cache(maxsize=1)(function)
