"""Memory Retriever - Search and retrieve similar problems from memory."""

from typing import List, Dict, Any, Optional
from .memory_store import MemoryStore
from .metadata_db import MetadataDB
from .models import MemoryEntry, MemorySearchResult


class MemoryRetriever:
    """Handles retrieval of similar problems from memory."""
    
    def __init__(self):
        self.vector_store = MemoryStore()
        self.metadata_db = MetadataDB()
    
    def retrieve_similar(self, query: str, topic: Optional[str] = None, n_results: int = 5, include_feedback: bool = True) -> MemorySearchResult:
        """
        Search for similar problems in memory.
        
        Args:
            query: The problem text to search for
            topic: Optional topic filter
            n_results: Number of results to return
            include_feedback: Whether to include feedback data
            
        Returns:
            MemorySearchResult with similar entries
        """
        similar = self.vector_store.search_similar(
            query=query,
            topic=topic,
            n_results=n_results
        )
        
        entries = []
        for item in similar:
            entry_dict = {
                "id": item["id"],
                "original_input": item["metadata"].get("original_input", ""),
                "parsed_question": item["metadata"],
                "final_answer": item["metadata"].get("final_answer", ""),
                "verifier_outcome": {"is_correct": item["metadata"].get("is_correct", True)},
                "problem_hash": item["metadata"].get("problem_hash", ""),
                "topic": item["metadata"].get("topic", ""),
                "distance": item.get("distance", 0),
            }
            
            if include_feedback:
                feedback = self.metadata_db.get_feedback_for_memory(item["id"])
                if feedback:
                    entry_dict["user_feedback"] = feedback[0].get("user_comment", "")
            
            entries.append(MemoryEntry(**entry_dict))
        
        return MemorySearchResult(
            entries=entries,
            total_found=len(entries),
            search_query=query
        )
    
    def get_memory_context(self, problem_text: str, topic: str, n_similar: int = 3) -> Dict[str, Any]:
        """
        Get memory context to pass to the Solver Agent.
        
        This creates a context string with similar problems and patterns.
        """
        result = self.retrieve_similar(
            query=problem_text,
            topic=topic,
            n_results=n_similar
        )
        
        if not result.entries:
            return {
                "has_memory": False,
                "context": "",
                "similar_problems": [],
                "patterns": []
            }
        
        similar_problems = []
        patterns = []
        
        for entry in result.entries:
            similar_problems.append({
                "problem": entry.original_input,
                "answer": entry.final_answer,
                "topic": entry.topic,
            })
            
            if entry.user_feedback:
                patterns.append({
                    "type": "feedback_correction",
                    "original": entry.original_input,
                    "correction": entry.user_feedback
                })
        
        context_parts = ["## Similar Problems Solved Before:"]
        for i, prob in enumerate(similar_problems, 1):
            context_parts.append(f"{i}. Problem: {prob['problem']}")
            context_parts.append(f"   Answer: {prob['answer']}")
            
            if patterns and i <= len(patterns):
                context_parts.append(f"   Note: {patterns[i-1].get('correction', '')}")
        
        return {
            "has_memory": True,
            "context": "\n".join(context_parts),
            "similar_problems": similar_problems,
            "patterns": patterns,
            "total_found": result.total_found
        }
    
    def get_correction_rules(self) -> List[Dict[str, Any]]:
        """Get OCR/audio correction rules from memory."""
        return self.metadata_db.get_corrections_by_count(min_count=1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.metadata_db.get_stats()
