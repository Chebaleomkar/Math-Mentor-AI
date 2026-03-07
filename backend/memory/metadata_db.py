"""Metadata Database - SQLite for structured memory data."""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class MetadataDB:
    """SQLite database for structured memory metadata."""
    
    def __init__(self, db_path: str = "backend/memory/metadata.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                original_input TEXT NOT NULL,
                parsed_question TEXT,
                retrieved_context TEXT,
                final_answer TEXT,
                verifier_outcome TEXT,
                user_feedback TEXT,
                timestamp TEXT,
                problem_hash TEXT,
                topic TEXT,
                complexity TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT,
                original_input TEXT,
                correct_answer TEXT,
                user_comment TEXT,
                feedback_type TEXT,
                timestamp TEXT,
                FOREIGN KEY (memory_id) REFERENCES memory_entries(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incorrect_text TEXT,
                correct_text TEXT,
                occurrence_count INTEGER DEFAULT 1,
                last_seen TEXT,
                UNIQUE(incorrect_text, correct_text)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic ON memory_entries(topic)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_problem_hash ON memory_entries(problem_hash)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def add_memory_entry(self, entry_data: Dict[str, Any]) -> bool:
        """Add a memory entry to SQLite."""
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries 
                (id, original_input, parsed_question, retrieved_context, 
                 final_answer, verifier_outcome, user_feedback, timestamp, 
                 problem_hash, topic, complexity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_data.get("id"),
                entry_data.get("original_input"),
                json.dumps(entry_data.get("parsed_question", {})),
                entry_data.get("retrieved_context", ""),
                entry_data.get("final_answer"),
                json.dumps(entry_data.get("verifier_outcome", {})),
                entry_data.get("user_feedback"),
                entry_data.get("timestamp"),
                entry_data.get("problem_hash"),
                entry_data.get("topic"),
                entry_data.get("complexity", "medium"),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB insert error: {e}")
            return False
        finally:
            conn.close()
    
    def add_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Add user feedback entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO feedback_entries 
                (memory_id, original_input, correct_answer, user_comment, 
                 feedback_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                feedback_data.get("memory_id"),
                feedback_data.get("original_input"),
                feedback_data.get("correct_answer"),
                feedback_data.get("user_comment"),
                feedback_data.get("feedback_type"),
                feedback_data.get("timestamp", datetime.now().isoformat()),
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Feedback insert error: {e}")
            return False
        finally:
            conn.close()
    
    def add_ocr_correction(self, incorrect: str, correct: str) -> bool:
        """Add or update OCR correction rule."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ocr_corrections (incorrect_text, correct_text, occurrence_count, last_seen)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(incorrect_text, correct_text) 
                DO UPDATE SET occurrence_count = occurrence_count + 1, last_seen = ?
            """, (incorrect, correct, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            print(f"OCR correction error: {e}")
            return False
        finally:
            conn.close()
    
    def get_feedback_for_memory(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific memory entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM feedback_entries WHERE memory_id = ? ORDER BY timestamp DESC
            """, (memory_id,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        finally:
            conn.close()
    
    def get_corrections_by_count(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """Get frequently used OCR corrections."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM ocr_corrections WHERE occurrence_count >= ? 
                ORDER BY occurrence_count DESC
            """, (min_count,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM memory_entries")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT topic, COUNT(*) as count FROM memory_entries GROUP BY topic")
            by_topic = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute("SELECT user_feedback, COUNT(*) as count FROM memory_entries WHERE user_feedback IS NOT NULL GROUP BY user_feedback")
            by_feedback = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_entries": total,
                "entries_by_topic": by_topic,
                "entries_by_feedback": by_feedback,
                "last_updated": datetime.now().isoformat()
            }
        finally:
            conn.close()
