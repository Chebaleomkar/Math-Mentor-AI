"""
Explainer / Tutor Agent
-----------------------
Takes the verified (and possibly corrected) solution and produces a
clear, step-by-step student-friendly explanation with:
  - Concept reminder
  - Numbered solution steps
  - Common mistake warning (if verifier found issues)
  - Exam tip
"""
from langchain_core.prompts import ChatPromptTemplate

from llm_router.router import router
from models.schemas import ParsedProblem, SolverResult, VerifierResult, ExplanationResult


_SYSTEM = """You are a friendly, expert JEE Math Tutor.

Your job is to explain the solution to a student who is learning.

Rules:
- Start with a one-line concept reminder (what theorem/formula is key here).
- Give a numbered step-by-step solution. Each step must have:
    - What you're doing and WHY.
    - The actual calculation.
- If there were mistakes in the original solution, clearly point out what went wrong.
- End with a short "Exam Tip" relevant to this problem type.
- Use plain text math notation (e.g. x^2, sqrt(x), integral of f dx). No LaTeX.
- Keep it concise but complete — a student should be able to follow every step."""

_HUMAN = """Problem:
{problem_text}

Topic: {topic}

Correct Final Answer: {final_answer}

Full Solution:
{solution}

Issues found by verifier (if any): {issues}"""


class ExplainerAgent:
    def __init__(self):
        self.llm = router.get_llm()
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", _SYSTEM), ("human", _HUMAN)]
        )

    def run(
        self,
        parsed_problem: ParsedProblem,
        solver_result: SolverResult,
        verifier_result: VerifierResult,
    ) -> ExplanationResult:
        # Use corrected answer if verifier found a better one
        final_answer = (
            verifier_result.corrected_answer
            if verifier_result.corrected_answer
            else solver_result.final_answer
        )

        chain = self.prompt | self.llm
        response = chain.invoke({
            "problem_text": parsed_problem.problem_text,
            "topic": parsed_problem.topic,
            "final_answer": final_answer,
            "solution": solver_result.solution,
            "issues": "; ".join(verifier_result.issues) if verifier_result.issues else "None",
        })

        return ExplanationResult(
            explanation=response.content.strip(),
            final_answer=final_answer,
            confidence=verifier_result.confidence,
        )