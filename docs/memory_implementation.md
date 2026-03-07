# Memory & Self-Learning Implementation Guide

## Overview

The Memory Layer is a smart storage system that remembers every problem the Math Mentor has solved. It uses this memory to:

1. **Find similar past problems** when solving new questions
2. **Learn from corrections** to improve future solutions
3. **Apply OCR/audio correction rules** to fix common recognition errors

---

## What We Store in Memory

| Field | Description | Example |
|-------|-------------|---------|
| `original_input` | Raw user input (text/image/audio path) | "Solve: 2x + 5 = 15" |
| `parsed_question` | Structured problem from Parser Agent | `{topic: "algebra", variables: ["x"]}` |
| `retrieved_context` | RAG knowledge base chunks used | "Linear equation solving steps..." |
| `final_answer` | Solution produced by Solver | "x = 5" |
| `verifier_outcome` | Verification result | `is_correct: true, confidence: 0.95` |
| `user_feedback` | Human feedback (correct/incorrect) | "correct" or "wrong: answer is 6" |
| `timestamp` | When the problem was solved | `2024-12-01 15:30:00` |
| `problem_hash` | Unique fingerprint of problem type | `"algebra_linear_1var"` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER QUESTION                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PARSER AGENT                               │
│                  (Parse input → structured)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY LAYER (NEW)                           │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ Memory Store  │  │   Retriever   │  │ Pattern Matcher  │   │
│  │  (ChromaDB)   │  │ (semantic     │  │  (hash-based)    │   │
│  │               │  │  similarity)  │  │                  │   │
│  └───────────────┘  └───────────────┘  └──────────────────┘   │
│                             │                                   │
│         ┌───────────────────┴───────────────────┐              │
│         ▼                                       ▼              │
│  ┌──────────────────┐                ┌──────────────────┐     │
│  │ Similar Problems │                │ Solution Patterns│     │
│  │   from Memory    │                │    from Memory   │     │
│  └──────────────────┘                └──────────────────┘     │
└────────────────────────────┬────────────────────────────────────┘
                             │ Memory Context passed to Solver
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SOLVER AGENT                               │
│              (Uses memory + RAG + tools to solve)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERIFIER AGENT                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXPLAINER AGENT                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              MEMORY LAYER - SAVE INTERACTION                    │
│   Store: parsed_question + final_answer + verifier_outcome     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| **Vector Storage** | ChromaDB | Already in project for RAG |
| **Embeddings** | sentence-transformers | Same as RAG pipeline |
| **Metadata DB** | SQLite | Structured data (feedback, timestamps) |
| **Pattern Matching** | Hash-based + Semantic | Fast lookup + intelligent matching |

---

## Files Created

```
backend/
├── memory/
│   ├── __init__.py
│   ├── models.py              # MemoryEntry data class
│   ├── memory_store.py        # ChromaDB storage for embeddings
│   ├── metadata_db.py         # SQLite for structured data
│   ├── memory_retriever.py    # Search similar problems
│   └── pattern_matcher.py     # Hash-based pattern matching
```

---

## Integration with Agent Coordinator

The memory layer integrates into the existing `AgentCoordinator`:

1. **After Parser**: Query memory for similar problems
2. **Before Solver**: Pass memory context (similar problems + patterns)
3. **After Verifier**: Save the complete interaction to memory
4. **On HITL feedback**: Store user corrections for self-learning

---

## API Endpoints Added

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/memory/search` | POST | Find similar problems |
| `/memory/add` | POST | Manually add a memory entry |
| `/feedback` | POST | Submit user feedback |
| `/memory/stats` | GET | Memory statistics |

---

## Runtime Flow Example

**User asks:** "Solve 3x - 7 = 20"

1. **Parser** → `{topic: "algebra", variables: ["x"]}`
2. **Memory** searches for "algebra" problems
3. **Memory finds**: "We solved '2x + 5 = 15' → x = 5 before"
4. **Solver** receives question + memory context
5. **Verifier** checks: "x = 9" ✓ Correct!
6. **Memory saves** the complete interaction
7. **Next time**: Similar problems will use this pattern

---

## Self-Learning Mechanism

When a human corrects the system via HITL:

1. User submits feedback: "Answer is wrong, should be x = 6"
2. Memory stores: `{original_input, correct_answer, feedback}`
3. On similar problem: Memory prioritizes this correction pattern
4. System becomes more accurate over time

**No model retraining required** - pattern reuse is sufficient.

---

## OCR/Audio Correction Rules (Bonus)

Memory can store patterns like:
- OCR: "x²" misread as "x2" → correction rule
- Audio: "square root of" → "√" 
- Audio: "raised to power" → "^"

These rules are applied during parsing phase.

