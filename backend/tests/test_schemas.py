"""
tests/test_schemas.py
----------------------
Unit tests for models/schemas.py.
No external calls — pure model validation.
"""
import json
import pytest
from pydantic import ValidationError

from models.schemas import (
    ParsedProblem,
    SolverResult,
    ToolCall,
    VerifierResult,
    ExplanationResult,
    MemoryRecord,
    HITLResponse,
    SolveResponse,
    RetrievedSource,
)


class TestParsedProblem:
    def test_minimal_creation(self):
        p = ParsedProblem(problem_text="Solve x^2=4", topic="algebra")
        assert p.problem_text == "Solve x^2=4"
        assert p.variables == []
        assert p.constraints == []
        assert p.needs_clarification is False

    def test_full_creation(self):
        p = ParsedProblem(
            problem_text="Find P(A|B)",
            topic="probability",
            variables=["A", "B"],
            constraints=["P(B) > 0"],
            needs_clarification=True,
            clarification_reason="P(A∩B) not given",
        )
        assert p.topic == "probability"
        assert "P(B) > 0" in p.constraints
        assert p.needs_clarification is True

    def test_missing_problem_text_raises(self):
        with pytest.raises(ValidationError):
            ParsedProblem(topic="algebra")  # problem_text is required

    def test_json_serialisable(self):
        p = ParsedProblem(problem_text="test", topic="other")
        data = json.loads(p.model_dump_json())
        assert data["problem_text"] == "test"


class TestSolverResult:
    def test_with_tool_calls(self):
        tc = ToolCall(tool="solve_equation", input="x^2=4", output="x=2, x=-2")
        sr = SolverResult(
            solution="Full solution text",
            final_answer="x = 2, x = -2",
            tool_calls=[tc],
        )
        assert len(sr.tool_calls) == 1
        assert sr.tool_calls[0].tool == "solve_equation"

    def test_json_serialisable(self):
        sr = SolverResult(solution="sol", final_answer="42")
        data = json.loads(sr.model_dump_json())
        assert data["final_answer"] == "42"
        assert data["tool_calls"] == []


class TestVerifierResult:
    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            VerifierResult(is_correct=True, confidence=1.5)
        with pytest.raises(ValidationError):
            VerifierResult(is_correct=True, confidence=-0.1)

    def test_needs_hitl_default_false(self):
        v = VerifierResult(is_correct=True, confidence=0.9)
        assert v.needs_hitl is False

    def test_low_confidence_sets_needs_hitl(self):
        # needs_hitl is set by VerifierAgent logic, not model — confirm field works
        v = VerifierResult(is_correct=False, confidence=0.4, needs_hitl=True)
        assert v.needs_hitl is True


class TestMemoryRecord:
    def _make_record(self) -> MemoryRecord:
        from datetime import datetime, timezone
        return MemoryRecord(
            id="test-123",
            raw_input="What is 2+2?",
            parsed_problem=ParsedProblem(problem_text="2+2", topic="algebra"),
            solver_result=SolverResult(solution="4", final_answer="4"),
            verifier_result=VerifierResult(is_correct=True, confidence=1.0),
            explanation=ExplanationResult(
                explanation="2+2=4 by addition",
                final_answer="4",
                confidence=1.0,
            ),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def test_creation(self):
        r = self._make_record()
        assert r.id == "test-123"
        assert r.user_feedback is None

    def test_full_json_round_trip(self):
        r = self._make_record()
        json_str = r.model_dump_json()
        data = json.loads(json_str)
        restored = MemoryRecord(**data)
        assert restored.id == r.id
        assert restored.parsed_problem.topic == "algebra"


class TestHITLResponse:
    def test_approved(self):
        h = HITLResponse(approved=True)
        assert h.approved is True
        assert h.edited_answer is None

    def test_rejected_with_correction(self):
        h = HITLResponse(approved=False, edited_answer="x = 3", comment="Wrong sign")
        assert h.edited_answer == "x = 3"


class TestSolveResponse:
    def test_json_serialisable(self):
        sr = SolveResponse(
            parsed_problem=ParsedProblem(problem_text="test", topic="algebra"),
            solver_result=SolverResult(solution="sol", final_answer="42"),
            verifier_result=VerifierResult(is_correct=True, confidence=0.9),
            explanation=ExplanationResult(explanation="exp", final_answer="42", confidence=0.9),
            retrieved_sources=[
                RetrievedSource(
                    title="Algebra Basics",
                    source="algebra.md",
                    section="Quadratics",
                    snippet="ax^2+bx+c=0",
                    score=0.12,
                )
            ],
            hitl_required=False,
            memory_id="abc-123",
        )
        data = json.loads(sr.model_dump_json())
        assert data["memory_id"] == "abc-123"
        assert len(data["retrieved_sources"]) == 1