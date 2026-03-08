from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
import re

from llm_router.router import router
from tools.rag_tool import retrieve_context
from tools.sympy_tool import solve_equation, derivative, integrate_expr, simplify_expr
from tools.python_tool import execute_python
from models.schemas import ParsedProblem, SolverResult, ToolCall


_SYSTEM = """You are an expert JEE-level Math Solver Agent.

You receive a structured math problem and must return a complete, correct solution.

Guidelines:
- Think step-by-step BEFORE calling any tool.
- Use `retrieve_context` to look up formulas or theorems you are not 100% certain about.
- Use `solve_equation`, `derivative`, `integrate_expr`, or `simplify_expr` for exact symbolic work.
- Use `execute_python` for numerical verification, combinatorics (nCr, nPr), or complex arithmetic.
- Only call tools when they genuinely help — do not use them unnecessarily.

After arriving at the answer, write a line that starts exactly with:

FINAL ANSWER: <your answer>

Problem topic: {topic}
Constraints: {constraints}
"""


def _serialize_steps(intermediate_steps) -> list[ToolCall]:
    calls = []

    for action, observation in intermediate_steps:
        calls.append(
            ToolCall(
                tool=getattr(action, "tool", str(action)),
                input=str(getattr(action, "tool_input", "")),
                output=str(observation),
            )
        )

    return calls


class SolverAgent:

    def __init__(self):
        self.llm = router.get_llm()

        self.tools = [
            retrieve_context,
            solve_equation,
            derivative,
            integrate_expr,
            simplify_expr,
            execute_python,
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", _SYSTEM),
            ("human", "{problem_text}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def run(self, parsed_problem: ParsedProblem) -> SolverResult:

        constraints = parsed_problem.constraints or ["none"]

        response = self.executor.invoke({
            "problem_text": parsed_problem.problem_text,
            "topic": parsed_problem.topic,
            "constraints": ", ".join(constraints),
        })

        raw_output = response.get("output", "")

        # Extract final answer safely
        match = re.search(r"FINAL ANSWER\s*:\s*(.+)", raw_output, re.IGNORECASE)

        if match:
            final_answer = match.group(1).strip()
        else:
            final_answer = raw_output

        tool_calls = _serialize_steps(response.get("intermediate_steps", []))

        return SolverResult(
            solution=raw_output,
            final_answer=final_answer,
            tool_calls=tool_calls,
        )