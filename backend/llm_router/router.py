"""
llm_router/router.py
--------------------
Single factory for all LLM instances used in the app.
Centralises model names and API key wiring.
"""
from langchain_groq import ChatGroq
from core.config import settings


class LLMRouter:
    _text_llm: ChatGroq | None = None
    _vision_llm: ChatGroq | None = None

    def get_llm(self) -> ChatGroq:
        """Standard text LLM (used by all agents)."""
        if self._text_llm is None:
            self._text_llm = ChatGroq(
                model=settings.GROQ_TEXT_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=0.0,
                max_tokens=4096,
            )
        return self._text_llm

    def get_vision_llm(self) -> ChatGroq:
        """Vision LLM (used by image extractor)."""
        if self._vision_llm is None:
            self._vision_llm = ChatGroq(
                model=settings.GROQ_VISION_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=0.0,
                max_tokens=1024,
            )
        return self._vision_llm


# Singleton
router = LLMRouter()