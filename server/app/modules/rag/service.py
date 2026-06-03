from __future__ import annotations

from server.app.core.errors import not_implemented
from server.app.modules.rag.schemas import RagIndexRequest, RagIndexResponse, RagSearchRequest, RagSearchResponse, RagSource


class RagService:
    def index_documents(self, request: RagIndexRequest) -> RagIndexResponse:
        not_implemented("rag.service", "index_documents")

    def search(self, request: RagSearchRequest) -> RagSearchResponse:
        not_implemented("rag.service", "search")

    def list_sources(self) -> list[RagSource]:
        not_implemented("rag.service", "list_sources")


def get_rag_service() -> RagService:
    return RagService()
