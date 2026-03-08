"""
tests/test_agents.py
---------------------
Unit tests for all 4 agents.
External LLM calls are mocked — no Groq credits consumed.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from models.schemas import (
    ParsedProblem,
    SolverResult,
    VerifierResult,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_response(content: str) -> MagicMock:
    m = MagicMock()
    m.content = content
    return m


def _make_parsed(
    text="Find the roots of x^2 - 5x + 6 = 0",
    topic="algebra",
) -> ParsedProblem:
    return ParsedProblem(problem_text=text, topic=topic)


def _make_solver_result(answer="x = 2 and x = 3") -> SolverResult:
    return SolverResult(
        solution=f"Step 1: Factor.\nFINAL ANSWER: {answer}",
        final_answer=answer,
    )


def _make_verifier_result(correct=True, confidence=0.95) -> VerifierResult:
    return VerifierResult(
        is_correct=correct,
        confidence=confidence,
        issues=[],
        needs_hitl=confidence < 0.75,
    )


# ── Parser Agent ──────────────────────────────────────────────────────────────

class TestParserAgent:
    _VALID_JSON = json.dumps({
        "problem_text": "Find the roots of x^2 - 5x + 6 = 0",
        "topic": "algebra",
        "variables": ["x"],
        "constraints": [],
        "needs_clarification": False,
        "clarification_reason": "",
    })

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_parses_clean_text(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(self._VALID_JSON)
        mock_get_llm.return_value = mock_llm

        from agents.parser_agent import ParserAgent
        agent = ParserAgent()
        result = agent.run("Find the roots of x^2 - 5x + 6 = 0")

        assert result.topic == "algebra"
        assert result.needs_clarification is False
        assert "x" in result.variables

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_handles_json_in_markdown_fences(self, mock_get_llm):
        """Groq sometimes wraps JSON in ```json ... ``` — parser must strip it."""
        fenced = f"```json\n{self._VALID_JSON}\n```"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(fenced)
        mock_get_llm.return_value = mock_llm

        from agents.parser_agent import ParserAgent
        agent = ParserAgent()
        result = agent.run("Any question")
        assert result.topic == "algebra"

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_needs_clarification_flag(self, mock_get_llm):
        unclear_json = json.dumps({
            "problem_text": "Find x",
            "topic": "other",
            "variables": ["x"],
            "constraints": [],
            "needs_clarification": True,
            "clarification_reason": "No equation given",
        })
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(unclear_json)
        mock_get_llm.return_value = mock_llm

        from agents.parser_agent import ParserAgent
        agent = ParserAgent()
        result = agent.run("Find x")
        assert result.needs_clarification is True
        assert result.clarification_reason != ""


# ── Verifier Agent ────────────────────────────────────────────────────────────

class TestVerifierAgent:
    _CORRECT_JSON = json.dumps({
        "is_correct": True,
        "confidence": 0.97,
        "issues": [],
        "corrected_answer": "",
        "reasoning": "Verified by factoring.",
    })

    _WRONG_JSON = json.dumps({
        "is_correct": False,
        "confidence": 0.40,
        "issues": ["Wrong sign", "Did not check domain"],
        "corrected_answer": "x = -2",
        "reasoning": "The quadratic was solved incorrectly.",
    })

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_correct_solution_no_hitl(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(self._CORRECT_JSON)
        mock_get_llm.return_value = mock_llm

        from agents.verifier_agent import VerifierAgent
        agent = VerifierAgent()
        result = agent.run(_make_parsed(), _make_solver_result())

        assert result.is_correct is True
        assert result.confidence == 0.97
        assert result.needs_hitl is False

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_wrong_solution_triggers_hitl(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(self._WRONG_JSON)
        mock_get_llm.return_value = mock_llm

        from agents.verifier_agent import VerifierAgent
        agent = VerifierAgent(hitl_threshold=0.75)
        result = agent.run(_make_parsed(), _make_solver_result("x = 2"))

        assert result.is_correct is False
        assert result.needs_hitl is True
        assert "Wrong sign" in result.issues
        assert result.corrected_answer == "x = -2"

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_markdown_fences_stripped(self, mock_get_llm):
        fenced = f"```json\n{self._CORRECT_JSON}\n```"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(fenced)
        mock_get_llm.return_value = mock_llm

        from agents.verifier_agent import VerifierAgent
        agent = VerifierAgent()
        result = agent.run(_make_parsed(), _make_solver_result())
        assert result.confidence == 0.97

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_custom_hitl_threshold(self, mock_get_llm):
        mid_confidence = json.dumps({
            "is_correct": True, "confidence": 0.80,
            "issues": [], "corrected_answer": "", "reasoning": "Mostly sure.",
        })
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(mid_confidence)
        mock_get_llm.return_value = mock_llm

        from agents.verifier_agent import VerifierAgent
        # With threshold 0.90, confidence 0.80 should trigger HITL
        agent = VerifierAgent(hitl_threshold=0.90)
        result = agent.run(_make_parsed(), _make_solver_result())
        assert result.needs_hitl is True

        # With threshold 0.75, confidence 0.80 should NOT trigger HITL
        agent2 = VerifierAgent(hitl_threshold=0.75)
        result2 = agent2.run(_make_parsed(), _make_solver_result())
        assert result2.needs_hitl is False


# ── Explainer Agent ───────────────────────────────────────────────────────────

class TestExplainerAgent:
    _EXPLANATION = (
        "Concept: Factoring quadratics.\n\n"
        "Step 1: Write x^2 - 5x + 6 = (x-2)(x-3).\n"
        "Step 2: Set each factor to zero: x=2 or x=3.\n\n"
        "Exam Tip: Always verify roots by substitution."
    )

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_produces_explanation(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(self._EXPLANATION)
        mock_get_llm.return_value = mock_llm

        from agents.explainer_agent import ExplainerAgent
        agent = ExplainerAgent()
        result = agent.run(
            _make_parsed(),
            _make_solver_result(),
            _make_verifier_result(),
        )
        assert "Step 1" in result.explanation
        assert result.final_answer == "x = 2 and x = 3"
        assert result.confidence == 0.95

    @patch("llm_router.router.LLMRouter.get_llm")
    def test_uses_corrected_answer(self, mock_get_llm):
        """When verifier provides a corrected_answer, explainer should use it."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response("Explanation using corrected answer.")
        mock_get_llm.return_value = mock_llm

        verifier = VerifierResult(
            is_correct=False,
            confidence=0.55,
            corrected_answer="x = -3",
            needs_hitl=True,
        )

        from agents.explainer_agent import ExplainerAgent
        agent = ExplainerAgent()
        result = agent.run(_make_parsed(), _make_solver_result(), verifier)

        # final_answer should come from corrected_answer, not solver
        assert result.final_answer == "x = -3"