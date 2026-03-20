"""
core/memory.py
--------------
Memory & Self-Learning layer.

Storage:   SQLite — zero deps, file-based, works on every free host
Embedding: Gemini embedding-004 (same model used in RAG, no extra deps)
Retrieval: Cosine similarity over stored embeddings for "find similar problems"

At runtime:
  - save_record()   → called by orchestrator after every solve
  - find_similar()  → called before solving to inject past solutions as context
  - update_feedback()→ called when user gives thumbs up/down or HITL corrects
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.config import settings


# ── DB setup ──────────────────────────────────────────────────────────────────

def _db_path() -> Path:
    p = Path(settings.MEMORY_DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id            TEXT PRIMARY KEY,
                raw_input     TEXT NOT NULL,
                problem_text  TEXT NOT NULL,
                topic         TEXT NOT NULL DEFAULT 'other',
                final_answer  TEXT NOT NULL DEFAULT '',
                full_record   TEXT NOT NULL,   -- JSON blob (MemoryRecord)
                embedding     BLOB,            -- float32 bytes (768-dim Gemini)
                user_feedback TEXT,            -- 'correct'|'incorrect'|'corrected'
                timestamp     TEXT NOT NULL
            )
        """)
        conn.commit()


_init_db()


# ── Embedding helper ──────────────────────────────────────────────────────────
_embedder: Optional[GoogleGenerativeAIEmbeddings] = None

def _get_embedder() -> GoogleGenerativeAIEmbeddings:
    global _embedder
    if _embedder is None:
        _embedder = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="RETRIEVAL_DOCUMENT",
            transport="rest",
        )
    return _embedder


def _embed(text: str) -> np.ndarray:
    """Return a 768-dim float32 numpy array for a problem text string.
    Guards against empty strings which cause 400 errors from Gemini.
    """
    if not text or not text.strip():
        return np.zeros(settings.EMBEDDING_DIMENSIONS, dtype=np.float32)
        
    vec = _get_embedder().embed_query(text)
    return np.array(vec, dtype=np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-9
    return float(np.dot(a, b) / denom)


# ── Public API ────────────────────────────────────────────────────────────────

def save_record(record) -> str:
    """
    Persist a MemoryRecord to SQLite.
    Accepts a MemoryRecord instance or a plain dict.
    Returns the record id.
    """
    from models.schemas import MemoryRecord

    if not isinstance(record, MemoryRecord):
        # Already a dict/JSON
        if hasattr(record, "model_dump"):
            record = record.model_dump()
        else:
             # Just assume it's a dict
             pass
        record = MemoryRecord(**record)

    rec_id = record.id or str(uuid.uuid4())
    problem_text = record.parsed_problem.problem_text
    final_answer = record.explanation.final_answer or record.solver_result.final_answer
    emb = _embed(problem_text)

    with _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO memory
              (id, raw_input, problem_text, topic, final_answer,
               full_record, embedding, user_feedback, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_id,
            record.raw_input,
            problem_text,
            record.parsed_problem.topic,
            final_answer,
            record.model_dump_json(),
            emb.tobytes(),
            record.user_feedback,
            record.timestamp or datetime.now(timezone.utc).isoformat(),
        ))
        conn.commit()

    return rec_id


def update_feedback(memory_id: str, feedback: str, comment: Optional[str] = None):
    """
    Store user feedback for a solved problem.
    Also updates the JSON blob so the full record stays consistent.
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT full_record FROM memory WHERE id = ?", (memory_id,)
        ).fetchone()

    if not row:
        return

    data = json.loads(row["full_record"])
    data["user_feedback"] = feedback
    if comment:
        data["user_comment"] = comment

    with _get_conn() as conn:
        conn.execute(
            "UPDATE memory SET user_feedback = ?, full_record = ? WHERE id = ?",
            (feedback, json.dumps(data), memory_id),
        )
        conn.commit()


def find_similar(
    problem_text: str,
    top_k: int = 3,
    min_similarity: float = 0.72,
) -> List[dict]:
    """
    Find up to top_k past problems semantically similar to problem_text.

    - Skips records explicitly marked 'incorrect' by the user.
    - Returns lightweight dicts with: id, problem_text, final_answer, similarity.
    """
    if not problem_text or not problem_text.strip():
        return []

    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, problem_text, final_answer, embedding, user_feedback "
            "FROM memory"
        ).fetchall()

    if not rows:
        return []

    query_emb = _embed(problem_text)
    results = []

    for row in rows:
        if row["user_feedback"] == "incorrect":
            continue
        if not row["embedding"]:
            continue

        stored = np.frombuffer(row["embedding"], dtype=np.float32)
        sim = _cosine(query_emb, stored)

        if sim >= min_similarity:
            results.append({
                "id": row["id"],
                "problem_text": row["problem_text"],
                "final_answer": row["final_answer"],
                "similarity": round(sim, 3),
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def get_record(memory_id: str) -> Optional[dict]:
    """Return the full JSON record for a given memory_id, or None."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT full_record FROM memory WHERE id = ?", (memory_id,)
        ).fetchone()
    return json.loads(row["full_record"]) if row else None


def list_recent(limit: int = 20) -> List[dict]:
    """Return lightweight summaries of the most recent records."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, problem_text, topic, final_answer, user_feedback, timestamp "
            "FROM memory ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_record(memory_id: str) -> bool:
    """Delete a record by id. Returns True if a row was deleted."""
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM memory WHERE id = ?", (memory_id,))
        conn.commit()
    return cur.rowcount > 0


def find_cached_match(
    problem_text: str,
    raw_input: Optional[str] = None,
    threshold: float = 0.90,
) -> Optional[dict]:
    """
    Find a high-reliability match in memory.
    1. Check for exact match on raw_input (if provided).
    2. Check for high-similarity match on problem_text.
    """
    if not problem_text and not raw_input:
        return None

    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT raw_input, problem_text, embedding, user_feedback, full_record "
            "FROM memory"
        ).fetchall()

    if not rows:
        return None

    # Step 1: Exact match on normalized raw_input
    if raw_input:
        clean_raw = raw_input.strip().lower()
        for row in rows:
            if row["user_feedback"] == "incorrect":
                continue
            if row["raw_input"].strip().lower() == clean_raw:
                return json.loads(row["full_record"])

    # Step 2: Semantic match on problem_text
    if problem_text:
        query_emb = _embed(problem_text)
        for row in rows:
            if row["user_feedback"] == "incorrect":
                continue
            if not row["embedding"]:
                continue

            stored = np.frombuffer(row["embedding"], dtype=np.float32)
            sim = _cosine(query_emb, stored)

            if sim >= threshold:
                return json.loads(row["full_record"])

    return None