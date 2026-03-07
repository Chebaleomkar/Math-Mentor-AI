"""Pattern Matcher - Hash-based pattern matching for memory."""

import hashlib
from typing import List, Dict, Any, Optional
from .memory_store import MemoryStore
from .metadata_db import MetadataDB


class PatternMatcher:
    """Handles hash-based pattern matching for problem types."""
    
    def __init__(self):
        self.vector_store = MemoryStore()
        self.metadata_db = MetadataDB()
    
    def generate_problem_hash(
        self,
        topic: str,
        complexity: str,
        num_variables: int
    ) -> str:
        """Generate a hash for a problem type."""
        content = f"{topic}:{complexity}:{num_variables}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def find_pattern_match(
        self,
        topic: str,
        complexity: str = "medium",
        num_variables: int = 1
    ) -> List[Dict[str, Any]]:
        """Find exact pattern matches in memory."""
        problem_hash = self.generate_problem_hash(topic, complexity, num_variables)
        return self.vector_store.get_by_hash(problem_hash)
    
    def apply_correction_rules(self, text: str) -> str:
        """Apply learned OCR/audio correction rules to text."""
        corrections = self.metadata_db.get_corrections_by_count(min_count=2)
        
        if not corrections:
            return text
        
        corrected = text
        for rule in corrections:
            incorrect = rule["incorrect_text"]
            correct = rule["correct_text"]
            if incorrect in corrected:
                corrected = corrected.replace(incorrect, correct)
        
        return corrected
    
    def add_correction_rule(self, incorrect: str, correct: str) -> bool:
        """Add a new OCR/audio correction rule."""
        return self.metadata_db.add_ocr_correction(incorrect, correct)
    
    def get_common_patterns(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get common problem-solving patterns from memory."""
        all_entries = self.vector_store.get_all_entries(limit=100)
        
        if not all_entries:
            return []
        
        patterns = []
        for entry in all_entries:
            if topic and entry["metadata"].get("topic") != topic:
                continue
            
            patterns.append({
                "problem": entry["metadata"].get("original_input", ""),
                "answer": entry["metadata"].get("final_answer", ""),
                "topic": entry["metadata"].get("topic", ""),
                "problem_hash": entry["metadata"].get("problem_hash", ""),
                "is_correct": entry["metadata"].get("is_correct", True),
            })
        
        return patterns
