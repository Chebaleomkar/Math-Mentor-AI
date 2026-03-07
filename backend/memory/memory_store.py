"""Memory Store - ChromaDB-based vector storage for memory embeddings."""

import os
import hashlib
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from .models import MemoryEntry


class MemoryStore:
    """Handles vector storage of memory entries using ChromaDB."""
    
    def __init__(self, persist_directory: str = "backend/chroma_db/memory"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="math_memory",
            metadata={"description": "Math Mentor memory embeddings"}
        )
    
    def _generate_id(self, entry: MemoryEntry) -> str:
        """Generate unique ID for a memory entry."""
        content = f"{entry.original_input}:{entry.topic}:{entry.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_hash(self, entry: MemoryEntry) -> str:
        """Generate problem hash for pattern matching."""
        content = f"{entry.topic}:{entry.complexity}:{len(entry.parsed_question.get('variables', []))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_embedding_text(self, entry: MemoryEntry) -> str:
        """Create text for embedding from memory entry."""
        return f"""
        Problem: {entry.original_input}
        Topic: {entry.topic}
        Parsed: {entry.parsed_question}
        Solution: {entry.final_answer}
        Context: {entry.retrieved_context}
        """.strip()
    
    def add_entry(self, entry: MemoryEntry) -> str:
        """Add a memory entry to the vector store."""
        entry_id = self._generate_id(entry)
        entry.id = entry_id
        entry.problem_hash = self._generate_hash(entry)
        
        embedding_text = self._get_embedding_text(entry)
        
        self.collection.add(
            ids=[entry_id],
            documents=[embedding_text],
            metadatas=[
                {
                    "topic": entry.topic,
                    "complexity": entry.complexity,
                    "problem_hash": entry.problem_hash,
                    "original_input": entry.original_input,
                    "final_answer": entry.final_answer,
                    "is_correct": entry.verifier_outcome.get("is_correct", True),
                    "timestamp": entry.timestamp,
                }
            ]
        )
        
        return entry_id
    
    def search_similar(
        self, 
        query: str, 
        topic: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar problems in memory."""
        where_filter = {"topic": topic} if topic else None
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            if not results or not results.get("ids") or not results["ids"][0]:
                return []
            
            similar_entries = []
            for i, entry_id in enumerate(results["ids"][0]):
                similar_entries.append({
                    "id": entry_id,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else 0
                })
            
            return similar_entries
            
        except Exception as e:
            print(f"Memory search error: {e}")
            return []
    
    def get_by_hash(self, problem_hash: str) -> List[Dict[str, Any]]:
        """Get entries by problem hash (exact pattern match)."""
        try:
            results = self.collection.get(
                where={"problem_hash": problem_hash}
            )
            
            if not results or not results.get("ids"):
                return []
            
            entries = []
            for i, entry_id in enumerate(results["ids"]):
                entries.append({
                    "id": entry_id,
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                })
            
            return entries
            
        except Exception as e:
            print(f"Get by hash error: {e}")
            return []
    
    def get_all_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all memory entries."""
        try:
            results = self.collection.get(limit=limit)
            if not results or not results.get("ids"):
                return []
            
            entries = []
            for i, entry_id in enumerate(results["ids"]):
                entries.append({
                    "id": entry_id,
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                })
            
            return entries
            
        except Exception as e:
            print(f"Get all error: {e}")
            return []
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        try:
            self.collection.delete(ids=[entry_id])
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    def count(self) -> int:
        """Get total number of memory entries."""
        return self.collection.count()
