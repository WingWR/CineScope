from __future__ import annotations

from server.app.core.errors import not_implemented


class RagDocumentLoader:
    def load_documents(self):
        not_implemented("rag.document_loader", "load_documents")
