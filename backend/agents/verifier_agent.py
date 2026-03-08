"""
Verifier / Critic Agent
-----------------------
Checks the solver's output for:
  - Logical / mathematical correctness
  - Unit and domain validity
  - Edge-case coverage

Returns a VerifierResult with a confidence score (0-1) and optional issues list.
If confidence < threshold → sets needs_hitl = True so the orchestrator can
pause and ask the human to review.
"""
import json
import re

from langchain_core.prompts import ChatPromptTemplate

from llm_router.router import router
from models.schemas import ParsedProblem, SolverResult, VerifierResult

HITL_THRESHOLD = 0.75   # confidence below this triggers human review

_SYSTEM = """You are a rigorous Math Verifier Agent.

You will be given:
  1. The original problem
  2. The solver's full solution
  3. The claimed final answer

Your tasks:
A. Re-derive or check the answer independently using your own reasoning.
B. Identify any logical errors, wrong formulas, domain violations, or missed edge cases.
C. Assign a confidence score between 0.0 (completely wrong) and 1.0 (certainly correct).

Respond ONLY with a valid JSON object — no markdown, no explanation:
{{
  "is_correct": <true | false>,
  "confidence": <float 0.0-1.0>,
  "issues": ["<issue1>", "..."],
  "corrected_answer": "<corrected final answer, or empty string if correct>",
  "reasoning": "<brief explanation of your check>"
}}
"""

_HUMAN = """Problem:
{problem_text}

Topic: {topic}

Solver Solution:
{solution}

Claimed Final Answer: {final_answer}"""


class VerifierAgent:
    def __init__(self, hitl_threshold: float = HITL_THRESHOLD):
        self.llm = router.get_llm()
        self.hitl_threshold = hitl_threshold
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", _SYSTEM), ("human", _HUMAN)]
        )

    def run(
        self,
        parsed_problem: ParsedProblem,
        solver_result: SolverResult,
    ) -> VerifierResult:
        chain = self.prompt | self.llm
        response = chain.invoke({
            "problem_text": parsed_problem.problem_text,
            "topic": parsed_problem.topic,
            "solution": solver_result.solution,
            "final_answer": solver_result.final_answer,
        })

        text = response.content.strip()
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        data = json.loads(text)

        needs_hitl = data.get("confidence", 1.0) < self.hitl_threshold

        return VerifierResult(
            is_correct=data.get("is_correct", False),
            confidence=data.get("confidence", 0.0),
            issues=data.get("issues", []),
            corrected_answer=data.get("corrected_answer", ""),
            reasoning=data.get("reasoning", ""),
            needs_hitl=needs_hitl,
        )