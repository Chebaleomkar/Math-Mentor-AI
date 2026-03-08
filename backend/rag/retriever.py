"""
rag/retriever.py
----------------
Retrieves the top-k most relevant knowledge base chunks for a given query.

Uses:
  - Gemini embedding-004 (768-dim) to embed the query
  - ChromaDB cosine similarity to find nearest chunks
  - Returns clean RetrievedChunk objects with source metadata
"""
from typing import List, Optional
from dataclasses import dataclass

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.config import settings
from rag.vector_store import get_collection


@dataclass
class RetrievedChunk:
    text: str
    source: str
    title: str
    section: str
    score: float          # cosine similarity distance (lower = more similar in ChromaDB)


class Retriever:
    _embedder: Optional[GoogleGenerativeAIEmbeddings] = None

    def _get_embedder(self) -> GoogleGenerativeAIEmbeddings:
        if self._embedder is None:
            self._embedder = GoogleGenerativeAIEmbeddings(
                model=settings.GEMINI_EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                task_type="RETRIEVAL_QUERY",   # different task type for queries vs docs
            )
        return self._embedder

    def retrieve(
        self,
        query: str,
        top_k: int = settings.RAG_TOP_K,
    ) -> List[RetrievedChunk]:
        """
        Embed `query` and return the top_k most similar chunks from ChromaDB.
        Returns empty list if the collection is empty (knowledge base not built yet).
        """
        collection = get_collection()

        if collection.count() == 0:
            return []

        # Embed the query
        embedder = self._get_embedder()
        query_embedding = embedder.embed_query(query)

        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            chunks.append(RetrievedChunk(
                text=doc,
                source=meta.get("source", ""),
                title=meta.get("title", ""),
                section=meta.get("section", ""),
                score=round(dist, 4),
            ))

        return chunks


# ── Module-level convenience function ────────────────────────────────────────
_retriever: Optional[Retriever] = None

def retrieve(query: str, top_k: int = settings.RAG_TOP_K) -> List[RetrievedChunk]:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever.retrieve(query, top_k)