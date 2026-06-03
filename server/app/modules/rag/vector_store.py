from __future__ import annotations

from server.app.core.errors import not_implemented


class VectorStore:
    def upsert(self, documents):
        not_implemented("rag.vector_store", "upsert")

    def query(self, query: str, top_k: int):
        not_implemented("rag.vector_store", "query")
