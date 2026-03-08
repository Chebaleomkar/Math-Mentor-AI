"""
tests/conftest.py
-----------------
Shared pytest fixtures.
All tests run against a real FastAPI TestClient with mocked external APIs
so no actual Groq / Google credits are consumed during testing.
"""
from __future__ import annotations

import json
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mock_llm_response():
    """Factory for building fake ChatGroq responses."""
    def _make(content: str) -> MagicMock:
        m = MagicMock()
        m.content = content
        return m
    return _make


@pytest.fixture(scope="session")
def parser_json() -> str:
    return json.dumps({
        "problem_text": "Find the roots of x^2 - 5x + 6 = 0",
        "topic": "algebra",
        "variables": ["x"],
        "constraints": [],
        "needs_clarification": False,
        "clarification_reason": "",
    })


@pytest.fixture(scope="session")
def verifier_json() -> str:
    return json.dumps({
        "is_correct": True,
        "confidence": 0.95,
        "issues": [],
        "corrected_answer": "",
        "reasoning": "Verified by factoring: (x-2)(x-3)=0 gives x=2 and x=3.",
    })


@pytest.fixture(scope="session")
def app_client(parser_json, verifier_json) -> Generator[TestClient, None, None]:
    """
    TestClient with all external calls patched so tests are fully offline.
    Patches:
      - ChatGroq.invoke         → returns mock LLM content
      - GoogleGenerativeAIEmbeddings.embed_query   → returns 768-dim zero vector
      - GoogleGenerativeAIEmbeddings.embed_documents → returns list of zero vectors
      - chromadb collection.query → returns empty results
      - Groq audio transcription  → returns mock transcript
    """
    import numpy as np

    fake_embedding = [0.0] * 768

    with (
        patch("langchain_groq.ChatGroq.invoke") as mock_invoke,
        patch(
            "langchain_google_genai.GoogleGenerativeAIEmbeddings.embed_query",
            return_value=fake_embedding,
        ),
        patch(
            "langchain_google_genai.GoogleGenerativeAIEmbeddings.embed_documents",
            return_value=[fake_embedding],
        ),
        patch(
            "chromadb.Collection.query",
            return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]},
        ),
        patch(
            "chromadb.Collection.count",
            return_value=1,
        ),
    ):
        # Route different LLM calls to appropriate mock responses
        def _invoke_router(messages, **kwargs):
            m = MagicMock()
            # Detect which agent is calling based on message content
            content = str(messages)
            if "parser" in content.lower() or "extract structured" in content.lower():
                m.content = parser_json
            elif "verif" in content.lower() or "critic" in content.lower():
                m.content = verifier_json
            else:
                # Solver or explainer
                m.content = (
                    "Step 1: Factor the quadratic x^2 - 5x + 6 = (x-2)(x-3).\n"
                    "Step 2: Set each factor to zero.\n"
                    "FINAL ANSWER: x = 2 and x = 3"
                )
            return m

        mock_invoke.side_effect = _invoke_router

        from main import app
        with TestClient(app) as client:
            yield client