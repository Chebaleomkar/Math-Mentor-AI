"""
rag/embed_kb.py
---------------
One-time (or re-runnable) script that:
  1. Reads all .md files from rag/knowledge_base/
  2. Splits them into chunks
  3. Embeds each chunk with Gemini embedding-004 (768-dim)
  4. Persists into ChromaDB

Run once before starting the server:
    python -m rag.embed_kb

Safe to re-run — clears and rebuilds the collection each time.
"""
import sys
from pathlib import Path
import time

# Allow running as a script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from core.config import settings


# ── Config ────────────────────────────────────────────────────────────────────
CHUNK_SIZE = 500          # characters per chunk
CHUNK_OVERLAP = 250
BATCH_SIZE = 20           # Gemini embedding API batch limit
RATE_LIMIT_DELAY = 10     # 10 second delay between batches to respect rate limits


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_markdown_files(kb_dir: Path) -> List[dict]:
    """Return list of {text, source, title} dicts from all .md files."""
    docs = []
    for md_file in sorted(kb_dir.glob("**/*.md")):
        text = md_file.read_text(encoding="utf-8")
        # Use first H1 as title, fallback to filename
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_file.stem
        docs.append({
            "text": text,
            "source": md_file.name,
            "title": title,
        })
    return docs


def chunk_document(doc: dict) -> List[dict]:
    """Split a markdown doc into overlapping chunks, preserving header context."""

    # First split by markdown headers to keep section context
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ],
        strip_headers=False,
    )

    # Then further split large sections by character count
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    header_chunks = header_splitter.split_text(doc["text"])
    chunks = []

    for hchunk in header_chunks:
        sub_chunks = char_splitter.split_text(hchunk.page_content)
        for i, chunk_text in enumerate(sub_chunks):
            # Build header breadcrumb from metadata
            breadcrumb = " > ".join(
                v for k, v in hchunk.metadata.items() if v
            )
            chunks.append({
                "text": chunk_text,
                "source": doc["source"],
                "title": doc["title"],
                "section": breadcrumb,
            })

    return chunks


def build_knowledge_base():
    kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
    if not kb_dir.exists():
        print(f"[embed_kb] Knowledge base directory not found: {kb_dir}")
        return

    md_files = list(kb_dir.glob("**/*.md"))
    if not md_files:
        print(f"[embed_kb] No .md files found in {kb_dir}")
        return

    print(f"[embed_kb] Found {len(md_files)} markdown file(s)")

    # ── Load & chunk ──────────────────────────────────────────────────────────
    all_chunks = []
    for doc in load_markdown_files(kb_dir):
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc['source']} → {len(chunks)} chunks")

    print(f"[embed_kb] Total chunks: {len(all_chunks)}")

    # ── Embed with Gemini ─────────────────────────────────────────────────────
    embedder = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        task_type="RETRIEVAL_DOCUMENT",
    )

    texts = [c["text"] for c in all_chunks]
    print(f"[embed_kb] Embedding {len(texts)} chunks (batch_size={BATCH_SIZE})...")

    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        batch_embeddings = embedder.embed_documents(batch)
        all_embeddings.extend(batch_embeddings)
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")
        time.sleep(RATE_LIMIT_DELAY)

    # ── Persist to ChromaDB ───────────────────────────────────────────────────
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    # Drop and recreate collection for clean rebuild
    try:
        client.delete_collection(settings.CHROMA_COLLECTION)
        print(f"[embed_kb] Dropped existing collection '{settings.CHROMA_COLLECTION}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # ChromaDB requires string IDs
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    metadatas = [
        {
            "source": c["source"],
            "title": c["title"],
            "section": c.get("section", ""),
        }
        for c in all_chunks
    ]

    # Upsert in batches (ChromaDB has a soft limit of ~5000 per call)
    for i in range(0, len(all_chunks), 500):
        collection.upsert(
            ids=ids[i : i + 500],
            embeddings=all_embeddings[i : i + 500],
            documents=texts[i : i + 500],
            metadatas=metadatas[i : i + 500],
        )

    print(f"[embed_kb] ✓ Persisted {len(all_chunks)} chunks to ChromaDB at {persist_dir}")
    print(f"[embed_kb] Collection: '{settings.CHROMA_COLLECTION}'")


if __name__ == "__main__":
    build_knowledge_base()