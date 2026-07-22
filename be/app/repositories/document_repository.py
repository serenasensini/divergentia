"""
Document Repository - in-memory document registry.

The service is designed for single-shot, local usage: a user uploads a document,
applies a few operations, previews and downloads the result. Nothing is meant to
be persisted for future sessions, so the registry is kept entirely in memory and
is discarded when the process exits.

Records live only for the lifetime of the process, so run the app with a single
worker (see the Dockerfile) to keep the registry coherent for the one user.
"""
import logging
import threading
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class DocumentRepository:
    """In-memory repository for document metadata (ephemeral)."""

    def __init__(self) -> None:
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        logger.info("In-memory document repository initialized")

    def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Store a document record (must contain an ``id``)."""
        with self._lock:
            self._documents[document['id']] = document
        logger.debug(f"Document created in repository: {document['id']}")
        return document

    def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Return a document by id, or None if it does not exist."""
        with self._lock:
            document = self._documents.get(document_id)
        return dict(document) if document is not None else None

    def update(self, document_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Merge ``updates`` into the stored document. Returns None if unknown."""
        with self._lock:
            document = self._documents.get(document_id)
            if document is None:
                return None
            document.update(updates)
            logger.debug(f"Document updated: {document_id}")
            return dict(document)

    def delete(self, document_id: str) -> bool:
        """Delete a document record. Returns True if a record was removed."""
        with self._lock:
            existed = self._documents.pop(document_id, None) is not None
        if existed:
            logger.debug(f"Document deleted: {document_id}")
        return existed

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all stored documents."""
        with self._lock:
            return [dict(document) for document in self._documents.values()]

    def count(self) -> int:
        """Return the total number of stored documents."""
        with self._lock:
            return len(self._documents)


# Singleton instance
_repository_instance: Optional[DocumentRepository] = None


def get_repository() -> DocumentRepository:
    """Get or create the shared repository instance."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = DocumentRepository()
    return _repository_instance
