"""
core/config.py
--------------
Single source of truth for all environment variables.
Uses pydantic-settings so values are validated at startup.

Required .env keys:
    GROQ_API_KEY=...
    GOOGLE_API_KEY=...
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Project root = two levels up from this file (backend/core/config.py → backend/)
_ROOT = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    # ── API Keys ──────────────────────────────────────────────────────────────
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str

    # ── Groq models ───────────────────────────────────────────────────────────
    GROQ_TEXT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_WHISPER_MODEL: str = "whisper-large-v3-turbo"

    # ── Gemini embedding ──────────────────────────────────────────────────────
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 768

    # ── RAG / ChromaDB ────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = str(_ROOT / "data" / "chroma_db")
    CHROMA_COLLECTION: str = "math_knowledge"
    KNOWLEDGE_BASE_DIR: str = str(_ROOT / "rag" / "knowledge_base")
    RAG_TOP_K: int = 4

    # ── Memory (SQLite) ───────────────────────────────────────────────────────
    MEMORY_DB_PATH: str = str(_ROOT / "data" / "memory.db")

    # ── HITL thresholds ───────────────────────────────────────────────────────
    VERIFIER_HITL_THRESHOLD: float = 0.75

    model_config = SettingsConfigDict(
        env_file=str(_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton — import this everywhere
settings = Settings()