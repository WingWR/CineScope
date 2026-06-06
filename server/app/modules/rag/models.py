from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RagDocument:
    id: str
    source_id: str
    source_name: str
    source_path: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ScoredRagDocument:
    document: RagDocument
    score: float
