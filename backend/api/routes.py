"""API Routes for Math Mentor - Including Memory & Self-Learning."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from agents import (
    ParserAgent,
    IntentRouterAgent,
    SolverAgent,
    VerifierAgent,
    ExplainerAgent,
    AgentCoordinator
)

router = APIRouter()

# Initialize agents
parser_agent = ParserAgent()
router_agent = IntentRouterAgent()
solver_agent = SolverAgent()
verifier_agent = VerifierAgent()
explainer_agent = ExplainerAgent()
coordinator = AgentCoordinator()


class QuestionRequest(BaseModel):
    question: str
    use_full_pipeline: bool = True


class VerificationRequest(BaseModel):
    question: str
    solution: str


class MemorySearchRequest(BaseModel):
    query: str
    topic: Optional[str] = None
    n_results: int = 5


class FeedbackRequest(BaseModel):
    memory_id: str
    correct_answer: str
    user_comment: str
    feedback_type: str = "correction"


class MemoryAddRequest(BaseModel):
    original_input: str
    parsed_question: dict
    final_answer: str
    topic: str
    complexity: str = "medium"


@router.post("/parse")
def parse_question(request: QuestionRequest):
    """Parse a math question into structured format."""
    result = parser_agent.run(request.question)
    return result


@router.post("/route")
def route_question(request: QuestionRequest):
    """Route the problem to determine solution strategy."""
    parsed = parser_agent.run(request.question)
    routing = router_agent.get_routing(parsed)
    return routing


@router.post("/solve")
def solve(request: QuestionRequest):
    """Solve a math problem using the agent pipeline."""
    if request.use_full_pipeline:
        result = coordinator.solve_problem(request.question)
    else:
        result = coordinator.solve_simple(request.question)
    return result


@router.post("/verify")
def verify_solution(request: VerificationRequest):
    """Verify an existing solution (for HITL review)."""
    result = coordinator.verify_only(request.question, request.solution)
    return result


@router.post("/explain")
def explain_solution(request: QuestionRequest):
    """Generate explanation for a solution."""
    parsed = parser_agent.run(request.question)
    solution = solver_agent.run(parsed)
    explanation = explainer_agent.run(parsed, solution)
    return explanation


# ==================== Memory & Self-Learning Endpoints ====================

@router.post("/memory/search")
def search_memory(request: MemorySearchRequest):
    """Search memory for similar problems."""
    try:
        result = coordinator.search_memory(
            query=request.query,
            topic=request.topic,
            n_results=request.n_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")


@router.post("/memory/add")
def add_to_memory(request: MemoryAddRequest):
    """Manually add a memory entry."""
    from memory import MemoryEntry
    
    try:
        entry = MemoryEntry(
            original_input=request.original_input,
            parsed_question=request.parsed_question,
            retrieved_context="",
            final_answer=request.final_answer,
            verifier_outcome={"is_correct": True, "confidence": 1.0},
            topic=request.topic,
            complexity=request.complexity
        )
        
        # Use coordinator's memory store for consistency
        memory_id = coordinator.memory_store.add_entry(entry)
        
        return {"success": True, "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")


@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for self-learning."""
    try:
        result = coordinator.add_feedback(
            memory_id=request.memory_id,
            correct_answer=request.correct_answer,
            user_comment=request.user_comment,
            feedback_type=request.feedback_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/memory/stats")
def get_memory_stats():
    """Get memory statistics."""
    try:
        stats = coordinator.get_memory_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": 5, "memory_enabled": True}
