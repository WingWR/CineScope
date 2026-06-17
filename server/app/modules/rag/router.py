from __future__ import annotations

from fastapi import APIRouter, Depends

from ...modules.rag.schemas import RagIndexRequest, RagIndexResponse, RagSearchRequest, RagSearchResponse, RagSource
from ...modules.rag.service import RagService, get_rag_service


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/search", response_model=RagSearchResponse)
def search(
    request: RagSearchRequest,
    service: RagService = Depends(get_rag_service),
) -> RagSearchResponse:
    return service.search(request)


@router.post("/index", response_model=RagIndexResponse)
def index_documents(
    request: RagIndexRequest,
    service: RagService = Depends(get_rag_service),
) -> RagIndexResponse:
    return service.index_documents(request)


@router.get("/sources", response_model=list[RagSource])
def list_sources(service: RagService = Depends(get_rag_service)) -> list[RagSource]:
    return service.list_sources()
