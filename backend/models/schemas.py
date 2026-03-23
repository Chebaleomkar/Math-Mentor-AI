"""
models/schemas.py
-----------------
All Pydantic models shared across the entire backend.

Design rules:
  - Every field has a default so partial construction never raises
  - steps_taken stores serialisable dicts, NOT raw LangChain tuples
  - All models are JSON-serialisable (model_dump_json() safe)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Parser ────────────────────────────────────────────────────────────────────


class ParsedProblem(BaseModel):
    problem_text: str = Field(description="Cleaned, unambiguous problem statement")
    topic: str = Field(
        default="other",
        description="algebra | calculus | probability | linear_algebra | other",
    )
    variables: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    needs_clarification: bool = Field(default=False)
    clarification_reason: str = Field(default="")


# ── Solver ────────────────────────────────────────────────────────────────────


class ToolCall(BaseModel):
    """One tool invocation recorded during solving."""

    tool: str
    input: str
    output: str


class SolverResult(BaseModel):
    solution: str = Field(description="Full solution text produced by the agent")
    final_answer: str = Field(description="Extracted final answer line")
    # Serialisable list of tool calls — NOT raw LangChain AgentStep tuples
    tool_calls: List[ToolCall] = Field(default_factory=list)


# ── Verifier ──────────────────────────────────────────────────────────────────


class VerifierResult(BaseModel):
    is_correct: bool = Field(default=False)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    corrected_answer: str = Field(default="")
    reasoning: str = Field(default="")
    needs_hitl: bool = Field(default=False)


# ── Explainer ─────────────────────────────────────────────────────────────────


class ExplanationResult(BaseModel):
    explanation: str = Field(default="")
    final_answer: str = Field(default="")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


# ── RAG context (for UI display) ──────────────────────────────────────────────


class RetrievedSource(BaseModel):
    title: str
    source: str
    section: str
    snippet: str  # first 300 chars of the chunk
    score: float


# ── Memory ────────────────────────────────────────────────────────────────────


class ExecutionTrace(BaseModel):
    """Stores the execution trace for a solve request."""

    agent_sequence: List[str] = Field(
        default_factory=list,
        description="Order of agents called: parser, rag, solver, verifier, explainer",
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list, description="All tool executions during solving"
    )
    context_retrieved: List[RetrievedSource] = Field(
        default_factory=list, description="Retrieved context from RAG"
    )
    start_time: str = Field(default="", description="ISO timestamp when solve started")
    end_time: str = Field(default="", description="ISO timestamp when solve completed")
    total_duration_seconds: float = Field(
        default=0.0, description="Total execution time"
    )


class MemoryRecord(BaseModel):
    id: str
    raw_input: str
    parsed_problem: ParsedProblem
    solver_result: SolverResult
    verifier_result: VerifierResult
    explanation: ExplanationResult
    user_feedback: Optional[str] = None  # "correct" | "incorrect" | "corrected"
    user_comment: Optional[str] = None
    timestamp: str
    execution_trace: ExecutionTrace = Field(default_factory=ExecutionTrace)


class MemorySummary(BaseModel):
    """Lightweight record returned by GET /memory list."""

    id: str
    problem_text: str
    topic: str
    final_answer: str
    user_feedback: Optional[str]
    timestamp: str
    agent_sequence: List[str] = Field(
        default_factory=list, description="Agents called for this problem"
    )
    tool_count: int = Field(default=0, description="Number of tool calls made")
    context_count: int = Field(
        default=0, description="Number of context sources retrieved"
    )


# ── HITL ──────────────────────────────────────────────────────────────────────


class HITLRequest(BaseModel):
    reason: str
    current_answer: str
    problem_text: str


class HITLResponse(BaseModel):
    approved: bool
    edited_answer: Optional[str] = None
    comment: Optional[str] = None


# ── API request / response ────────────────────────────────────────────────────


class SolveRequest(BaseModel):
    input_type: str = Field(description="text | image | audio")
    content: str = Field(
        description="Plain text, or base64-encoded bytes for image/audio"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Original filename — used for audio MIME detection",
    )


class SolveResponse(BaseModel):
    parsed_problem: ParsedProblem
    solver_result: SolverResult
    verifier_result: VerifierResult
    explanation: ExplanationResult
    retrieved_sources: List[RetrievedSource] = Field(default_factory=list)
    hitl_required: bool = Field(default=False)
    is_cache_hit: bool = Field(default=False)
    memory_id: str


class FeedbackRequest(BaseModel):
    feedback: str = Field(description="correct | incorrect")
    comment: Optional[str] = ""


# ── Extraction responses (image + audio) ──────────────────────────────────────


class ExtractionResponse(BaseModel):
    """Returned by /extract/image and /extract/image/base64."""

    extracted_text: str
    confidence: str  # "high" | "medium" | "low"
    needs_review: bool
    notes: str


class TranscriptionResponse(BaseModel):
    """Returned by /extract/audio and /extract/audio/base64."""

    transcript: str
    cleaned_text: str
    language: str
    duration_seconds: float
    needs_review: bool
    notes: str
