from __future__ import annotations

from server.app.modules.rag.retriever import RagRetriever


class RagIndexer:
    def __init__(self, retriever: RagRetriever | None = None) -> None:
        self.retriever = retriever or RagRetriever()

    def build_index(self, source_names: list[str] | None = None):
        return self.retriever.rebuild(source_names=source_names)
