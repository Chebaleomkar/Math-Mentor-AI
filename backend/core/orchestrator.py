"""
core/orchestrator.py
--------------------
Central pipeline:
  Parser → Memory lookup → Solver → Verifier → (HITL?) → Explainer → Save

Returns SolveResponse which includes retrieved_sources for UI display.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from agents.parser_agent import ParserAgent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from agents.explainer_agent import ExplainerAgent
from core import memory as mem_store
from models.schemas import (
    MemoryRecord,
    RetrievedSource,
    SolveResponse,
    HITLResponse,
)
from tools.rag_tool import get_retrieved_chunks


class Orchestrator:
    def __init__(self):
        self.parser = ParserAgent()
        self.solver = SolverAgent()
        self.verifier = VerifierAgent()
        self.explainer = ExplainerAgent()

    # ── Main pipeline ─────────────────────────────────────────────────────────

    def run(self, raw_input: str, input_type: str = "text") -> SolveResponse:
        # 1. Parse raw input → structured problem
        parsed = self.parser.run(raw_input)

        # 2. Memory lookup — find similar past problems
        similar = mem_store.find_similar(parsed.problem_text, top_k=3)
        if similar:
            hint_block = "\n\n[MEMORY CONTEXT — similar solved problems]\n"
            for s in similar:
                hint_block += f"• Problem: {s['problem_text']}\n  Answer: {s['final_answer']}\n"
            # Append memory hints so solver can reuse patterns
            parsed.problem_text += hint_block

        # 3. Retrieve RAG context for UI display (solver agent also calls internally)
        raw_chunks = get_retrieved_chunks(parsed.problem_text, top_k=4)
        retrieved_sources = [
            RetrievedSource(
                title=c.title,
                source=c.source,
                section=c.section,
                snippet=c.text[:300],
                score=c.score,
            )
            for c in raw_chunks
        ]

        # 4. Solve
        solver_result = self.solver.run(parsed)

        # 5. Verify
        verifier_result = self.verifier.run(parsed, solver_result)

        # 6. Explain
        explanation = self.explainer.run(parsed, solver_result, verifier_result)

        # 7. Persist to memory
        mem_id = str(uuid.uuid4())
        record = MemoryRecord(
            id=mem_id,
            raw_input=raw_input,
            parsed_problem=parsed,
            solver_result=solver_result,
            verifier_result=verifier_result,
            explanation=explanation,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        mem_store.save_record(record)

        hitl_required = parsed.needs_clarification or verifier_result.needs_hitl

        return SolveResponse(
            parsed_problem=parsed,
            solver_result=solver_result,
            verifier_result=verifier_result,
            explanation=explanation,
            retrieved_sources=retrieved_sources,
            hitl_required=hitl_required,
            memory_id=mem_id,
        )

    # ── HITL ──────────────────────────────────────────────────────────────────

    def apply_hitl_feedback(
        self, memory_id: str, hitl_response: HITLResponse
    ) -> Optional[str]:
        record_data = mem_store.get_record(memory_id)
        if not record_data:
            return None

        if hitl_response.approved:
            mem_store.update_feedback(memory_id, "correct", hitl_response.comment)
            return record_data["explanation"]["final_answer"]

        corrected = hitl_response.edited_answer or ""
        comment = f"Human correction: {corrected}. {hitl_response.comment or ''}".strip()
        mem_store.update_feedback(memory_id, "corrected", comment)

        # Update the stored record with corrected answer so memory learns it
        record_data["explanation"]["final_answer"] = corrected
        record_data["user_feedback"] = "corrected"
        mem_store.save_record(record_data)
        return corrected

    # ── User feedback ─────────────────────────────────────────────────────────

    def record_feedback(self, memory_id: str, feedback: str, comment: str = ""):
        mem_store.update_feedback(memory_id, feedback, comment or None)