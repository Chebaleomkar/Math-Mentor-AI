"""
rag/vector_store.py
-------------------
Thin wrapper around ChromaDB that provides a single persistent client
and collection reference, shared across the whole application.

Never instantiate chromadb.PersistentClient more than once —
doing so on the same path causes lock conflicts.
"""
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings


class VectorStore:
    _client: Optional[chromadb.PersistentClient] = None
    _collection: Optional[chromadb.Collection] = None

    @classmethod
    def _init(cls):
        if cls._client is not None:
            return

        persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        persist_dir.mkdir(parents=True, exist_ok=True)

        cls._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    @classmethod
    def get_collection(cls) -> chromadb.Collection:
        cls._init()

        if cls._collection is None:
            # get_or_create so the server starts even if embed_kb hasn't been run
            cls._collection = cls._client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        return cls._collection

    @classmethod
    def is_populated(cls) -> bool:
        """Returns True if the collection has at least one document."""
        try:
            return cls.get_collection().count() > 0
        except Exception:
            return False


# Module-level convenience
def get_collection() -> chromadb.Collection:
    return VectorStore.get_collection()