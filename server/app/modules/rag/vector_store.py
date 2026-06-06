from __future__ import annotations

import re
from dataclasses import dataclass

from server.app.modules.rag.models import RagDocument, ScoredRagDocument
from server.app.shared.text_utils import normalize_text


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+", re.IGNORECASE)
CHINESE_PATTERN = re.compile(r"^[\u4e00-\u9fff]+$")


@dataclass(frozen=True)
class _IndexedRagDocument:
    document: RagDocument
    title_text: str
    content_text: str
    title_tokens: set[str]
    content_tokens: set[str]
    metadata_tokens: set[str]


class InMemoryRagStore:
    def __init__(self) -> None:
        self._documents: list[_IndexedRagDocument] = []

    def upsert(self, documents: list[RagDocument]) -> None:
        self._documents = [self._index_document(document) for document in documents]

    def query(self, query: str, top_k: int = 5) -> list[ScoredRagDocument]:
        query_text = normalize_text(query).lower()
        query_tokens = set(_tokenize(query_text))
        if not query_text and not query_tokens:
            return []

        scored: list[ScoredRagDocument] = []
        for indexed in self._documents:
            raw_score = self._score_document(indexed, query_text, query_tokens)
            if raw_score <= 0:
                continue
            scored.append(
                ScoredRagDocument(
                    document=indexed.document,
                    score=round(min(raw_score / 20.0, 1.0), 4),
                )
            )
        scored.sort(
            key=lambda item: (
                item.score,
                item.document.title,
            ),
            reverse=True,
        )
        return scored[:top_k]

    def _index_document(self, document: RagDocument) -> _IndexedRagDocument:
        metadata_text = " ".join(_flatten_metadata(document.metadata))
        return _IndexedRagDocument(
            document=document,
            title_text=normalize_text(document.title).lower(),
            content_text=normalize_text(document.content).lower(),
            title_tokens=set(_tokenize(document.title)),
            content_tokens=set(_tokenize(document.content)),
            metadata_tokens=set(_tokenize(metadata_text)),
        )

    def _score_document(
        self,
        indexed: _IndexedRagDocument,
        query_text: str,
        query_tokens: set[str],
    ) -> float:
        score = 0.0
        if query_text and query_text == indexed.title_text:
            score += 8.0
        if query_text and query_text in indexed.title_text:
            score += 6.0
        if query_text and query_text in indexed.content_text:
            score += 4.0

        if query_tokens:
            title_overlap = query_tokens.intersection(indexed.title_tokens)
            content_overlap = query_tokens.intersection(indexed.content_tokens)
            metadata_overlap = query_tokens.intersection(indexed.metadata_tokens)
            score += 4.0 * len(content_overlap) / len(query_tokens)
            score += 3.0 * len(title_overlap) / len(query_tokens)
            score += 2.5 * len(metadata_overlap) / len(query_tokens)
            if query_tokens.issubset(indexed.title_tokens):
                score += 2.0
            if query_tokens.issubset(indexed.metadata_tokens):
                score += 1.5
        score += _source_boost(indexed, query_text, query_tokens)
        return score


def _source_boost(
    indexed: _IndexedRagDocument,
    query_text: str,
    query_tokens: set[str],
) -> float:
    source_id = indexed.document.source_id
    boost = 0.0

    if _looks_like_stats_query(query_text, query_tokens):
        if source_id == "dataset_summary":
            boost += 4.0
        elif source_id == "quality_report":
            boost += 3.0
        elif source_id == "genre_stats":
            boost += 2.5
        elif source_id == "movies":
            boost -= 1.0

    if _looks_like_schema_query(query_text, query_tokens):
        if indexed.document.source_type == "markdown":
            boost += 2.5
        if "field" in indexed.title_tokens or "字段" in indexed.title_tokens:
            boost += 1.5

    if _looks_like_quality_query(query_text, query_tokens) and source_id == "quality_report":
        boost += 2.5
    return boost


def _flatten_metadata(metadata: dict[str, object]) -> list[str]:
    tokens: list[str] = []
    for value in metadata.values():
        if isinstance(value, list):
            tokens.extend(normalize_text(item) for item in value if normalize_text(item))
            continue
        tokens.append(normalize_text(value))
    return [token for token in tokens if token]


def _tokenize(text: str) -> list[str]:
    normalized = normalize_text(text).lower()
    tokens: list[str] = []
    for match in TOKEN_PATTERN.findall(normalized):
        if CHINESE_PATTERN.fullmatch(match):
            tokens.append(match)
            if len(match) > 1:
                tokens.extend(match[index : index + 2] for index in range(len(match) - 1))
            tokens.extend(char for char in match if char.strip())
        else:
            tokens.append(match)
    return [token for token in tokens if token]


def _looks_like_stats_query(query_text: str, query_tokens: set[str]) -> bool:
    keywords = {
        "dataset",
        "summary",
        "count",
        "counts",
        "rating",
        "ratings",
        "user",
        "users",
        "tag",
        "tags",
        "statistics",
        "stats",
        "数据集",
        "统计",
        "多少",
        "评分",
        "用户",
        "标签",
        "概览",
        "摘要",
    }
    return any(keyword in query_text for keyword in keywords) or bool(query_tokens.intersection(keywords))


def _looks_like_schema_query(query_text: str, query_tokens: set[str]) -> bool:
    keywords = {
        "field",
        "fields",
        "column",
        "columns",
        "schema",
        "格式",
        "字段",
        "列",
        "结构",
    }
    return any(keyword in query_text for keyword in keywords) or bool(query_tokens.intersection(keywords))


def _looks_like_quality_query(query_text: str, query_tokens: set[str]) -> bool:
    keywords = {
        "quality",
        "clean",
        "cleaning",
        "missing",
        "duplicate",
        "duplicates",
        "质量",
        "清洗",
        "缺失",
        "重复",
    }
    return any(keyword in query_text for keyword in keywords) or bool(query_tokens.intersection(keywords))
