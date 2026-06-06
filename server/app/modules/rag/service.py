from __future__ import annotations

from server.app.modules.rag.retriever import RagRetriever
from server.app.modules.rag.schemas import RagIndexRequest, RagIndexResponse, RagSearchRequest, RagSearchResponse, RagSource
from server.app.shared.cache import cached


class RagService:
    def __init__(self, retriever: RagRetriever | None = None) -> None:
        self.retriever = retriever or get_rag_retriever()

    def index_documents(self, request: RagIndexRequest) -> RagIndexResponse:
        documents = self.retriever.rebuild(source_names=request.sourceNames if request.rebuild or request.sourceNames else None)
        return RagIndexResponse(
            indexedCount=len(documents),
            sources=self.retriever.list_sources(),
        )

    def search(self, request: RagSearchRequest) -> RagSearchResponse:
        scored = self.retriever.search(query=request.query, top_k=request.topK)
        items = [
            self._to_search_result(item.document, item.score)
            for item in scored
        ]
        return RagSearchResponse(items=items)

    def list_sources(self) -> list[RagSource]:
        return self.retriever.list_sources()

    @staticmethod
    def _to_search_result(document, score: float):
        return {
            "source": RagSource(
                id=document.source_id,
                name=document.source_name,
                path=document.source_path,
                type=document.source_type,
            ),
            "title": document.title,
            "content": _excerpt(document.content),
            "score": score,
            "metadata": document.metadata,
        }


def get_rag_service() -> RagService:
    return RagService()


@cached
def get_rag_retriever() -> RagRetriever:
    return RagRetriever()


def _excerpt(content: str, max_chars: int = 320) -> str:
    text = content.strip().replace("\r\n", "\n")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."
