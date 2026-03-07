from pydantic import BaseModel
from typing import List

class ParsedProblem(BaseModel):
    """Output from Parser Agent"""
    problem_text: str
    topic: str
    variables: List[str]
    constraints: List[str]
    needs_clarification: bool


class WorkflowPlan(BaseModel):
    """Output from Intent Router Agent"""
    primary_topic: str
    complexity: str  # simple, medium, complex
    required_techniques: List[str]
    solution_approach: str
    requires_tools: bool
    requires_verification: bool
    estimated_steps: int


class SolutionResult(BaseModel):
    """Output from Solver Agent"""
    solution: str
    steps: List[str]
    final_answer: str
    confidence: float
    tools_used: List[str]


class VerificationResult(BaseModel):
    """Output from Verifier Agent"""
    is_correct: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    needs_human_review: bool


class ExplanationResult(BaseModel):
    """Output from Explainer Agent"""
    explanation: str
    key_concepts: List[str]
    step_by_step: List[str]
    tips: List[str]