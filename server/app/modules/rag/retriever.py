from __future__ import annotations

from ...modules.rag.document_loader import RagDocumentLoader
from ...modules.rag.models import RagDocument, ScoredRagDocument
from ...modules.rag.schemas import RagSource
from ...modules.rag.vector_store import InMemoryRagStore


class RagRetriever:
    def __init__(
        self,
        loader: RagDocumentLoader | None = None,
        store: InMemoryRagStore | None = None,
    ) -> None:
        self.loader = loader or RagDocumentLoader()
        self.store = store or InMemoryRagStore()
        self._documents: list[RagDocument] = []
        self._sources: list[RagSource] = []
        self._is_built = False

    def rebuild(self, source_names: list[str] | None = None) -> list[RagDocument]:
        self._documents = self.loader.load_documents(source_names=source_names)
        self.store.upsert(self._documents)
        self._sources = _build_sources(self._documents)
        self._is_built = True
        return list(self._documents)

    def get_documents(self) -> list[RagDocument]:
        self._ensure_built()
        return list(self._documents)

    def search(self, query: str, top_k: int) -> list[ScoredRagDocument]:
        self._ensure_built()
        return self.store.query(query=query, top_k=top_k)

    def list_sources(self) -> list[RagSource]:
        self._ensure_built()
        return list(self._sources)

    def _ensure_built(self) -> None:
        if not self._is_built:
            self.rebuild()


def _build_sources(documents: list[RagDocument]) -> list[RagSource]:
    seen: dict[str, RagSource] = {}
    for document in documents:
        seen.setdefault(
            document.source_id,
            RagSource(
                id=document.source_id,
                name=document.source_name,
                path=document.source_path,
                type=document.source_type,
            ),
        )
    return list(seen.values())
