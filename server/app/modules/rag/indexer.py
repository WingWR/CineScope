from __future__ import annotations

from server.app.core.errors import not_implemented


class RagIndexer:
    def build_index(self, source_names: list[str] | None = None):
        not_implemented("rag.indexer", "build_index")
