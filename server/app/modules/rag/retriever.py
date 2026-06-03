from __future__ import annotations

from server.app.core.errors import not_implemented


class RagRetriever:
    def search(self, query: str, top_k: int):
        not_implemented("rag.retriever", "search")
