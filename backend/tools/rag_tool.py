"""
tools/rag_tool.py
-----------------
LangChain tool that the SolverAgent can call to look up relevant
formulas, theorems, and solution templates from the knowledge base.

The tool formats retrieved chunks into a clean context string that
the LLM can reason over, and includes source attribution so the
UI can display "Retrieved from: ..." panels.
"""
from typing import List
from langchain_core.tools import tool

from rag.retriever import retrieve, RetrievedChunk


def _format_chunks(chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant context found in the knowledge base."

    lines = ["=== KNOWLEDGE BASE CONTEXT ===\n"]
    for i, chunk in enumerate(chunks, 1):
        header = f"[{i}] {chunk.title}"
        if chunk.section:
            header += f" › {chunk.section}"
        header += f"  (source: {chunk.source})"
        lines.append(header)
        lines.append(chunk.text)
        lines.append("")   # blank line between chunks

    return "\n".join(lines)


@tool
def retrieve_context(query: str) -> str:
    """
    Search the math knowledge base for relevant formulas, theorems,
    solution templates, or common pitfalls related to the query.

    Use this tool when you need to:
    - Look up a formula or identity you are not 100% sure about
    - Find a standard solution template for a problem type
    - Check domain constraints or common mistakes for a topic

    Args:
        query: A short description of what you are looking for,
               e.g. "quadratic formula", "integration by parts",
               "Bayes theorem", "eigenvalue definition"

    Returns:
        Relevant text chunks from the knowledge base with source info.
    """
    chunks = retrieve(query)
    return _format_chunks(chunks)


# ── Also expose raw retrieval for use outside agent tools ────────────────────
def get_retrieved_chunks(query: str) -> List[RetrievedChunk]:
    """Return raw RetrievedChunk objects (used by orchestrator for UI display)."""
    return retrieve(query)