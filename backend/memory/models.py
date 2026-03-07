"""Data models for Memory Layer."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MemoryEntry(BaseModel):
    """Represents a single memory entry in the system."""
    id: Optional[str] = None
    original_input: str
    parsed_question: Dict[str, Any]
    retrieved_context: str
    final_answer: str
    verifier_outcome: Dict[str, Any]
    user_feedback: Optional[str] = None
    timestamp: str = None
    problem_hash: str
    topic: str
    complexity: str = "medium"
    
    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.now().isoformat()
        super().__init__(**data)


class FeedbackEntry(BaseModel):
    """Represents user feedback on a solution."""
    memory_id: str
    original_input: str
    correct_answer: str
    user_comment: str
    feedback_type: str  # "correction", "confirmation", "rejection"
    timestamp: str = None
    
    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.now().isoformat()
        super().__init__(**data)


class MemorySearchResult(BaseModel):
    """Result from memory search."""
    entries: List[MemoryEntry]
    total_found: int
    search_query: str


class MemoryStats(BaseModel):
    """Statistics about the memory system."""
    total_entries: int
    entries_by_topic: Dict[str, int]
    entries_by_feedback: Dict[str, int]
    last_updated: str
