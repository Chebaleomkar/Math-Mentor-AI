"""
agents/solver_agent.py
----------------------
Main reasoning agent that solves math problems using tools.

Uses:
- RAG retrieval for formulas
- SymPy tools for symbolic math
- Python sandbox for numeric computation
"""

import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from llm_router.router import router
from tools.rag_tool import retrieve_context
from tools.sympy_tool import solve_equation, derivative, integrate_expr, simplify_expr
from tools.python_tool import execute_python

from models.schemas import ParsedProblem, SolverResult, ToolCall


# ──────────────────────────────────────────────────────────────
# SYSTEM PROMPT (Improved for reliable tool calling)
# ──────────────────────────────────────────────────────────────
_SYSTEM = """
You are an expert JEE-level mathematics solver.

Your goal is to solve challenging mathematics problems accurately and clearly.

You have strong reasoning ability and mathematical knowledge. Use logical
step-by-step reasoning to derive the solution.

You also have access to external tools that can help with symbolic algebra,
calculus, and numerical computation.

AVAILABLE TOOLS
---------------
1. retrieve_context → look up formulas, theorems, and solution templates
2. solve_equation → solve algebraic equations symbolically
3. derivative → compute symbolic derivatives
4. integrate_expr → compute symbolic integrals
5. simplify_expr → simplify expressions
6. execute_python → perform numerical computation or verification


HOW TO SOLVE PROBLEMS
---------------------

1. First analyze the problem carefully.
2. Use mathematical reasoning to determine the correct method.
3. Perform algebraic manipulation mentally when possible.
4. Use tools when they are helpful for:
   - symbolic algebra
   - solving equations
   - calculus operations
   - complex arithmetic
   - verifying results

IMPORTANT GUIDELINES
--------------------

• Tools are helpers, not mandatory steps.
• You may solve parts of the problem using reasoning alone.
• Use tools when computation would be tedious, error-prone, or symbolic.
• Never fabricate tool outputs.
• If you call a tool, use its result in the reasoning.

Always explain your reasoning clearly step by step.

When the solution is complete, end with:

FINAL ANSWER: <result>

Do not include anything after the final answer.
"""

# ──────────────────────────────────────────────────────────────
# Utility: Serialize intermediate tool calls
# ──────────────────────────────────────────────────────────────

def _serialize_steps(intermediate_steps) -> List[ToolCall]:
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


# ──────────────────────────────────────────────────────────────
# Solver Agent
# ──────────────────────────────────────────────────────────────

class SolverAgent:

    def __init__(self):

        self.llm = router.get_llm()

        # Registered tools
        self.tools = [
            retrieve_context,
            solve_equation,
            derivative,
            integrate_expr,
            simplify_expr,
            execute_python,
        ]

        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", _SYSTEM),
            ("human",
             "Solve the following math problem.\n\n"
             "Problem: {problem_text}\n"
             "Topic: {topic}\n"
             "Constraints: {constraints}\n"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create tool-calling agent
        agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            self.prompt
        )

        # Executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    # ──────────────────────────────────────────────────────────
    # Run Solver
    # ──────────────────────────────────────────────────────────

    def run(self, parsed_problem: ParsedProblem) -> SolverResult:
        constraints = parsed_problem.constraints or ["none"]

        try:
            response = self.executor.invoke({
                "problem_text": parsed_problem.problem_text,
                "topic": parsed_problem.topic,
                "constraints": ", ".join(constraints),
            })
            raw_output = response.get("output", "").strip()
            tool_calls = _serialize_steps(response.get("intermediate_steps", []))

        except Exception as e:
            # Provide more context in case of API or Runtime failures
            error_msg = str(e)
            return SolverResult(
                solution=f"### Solver Exception\nAn internal error occurred while reasoning: `{error_msg}`",
                final_answer=f"SOLVER_ERROR: {error_msg[:30]}...",
                tool_calls=[]
            )

        # ── Extraction logic ──
        # Search for the LAST occurrence of 'FINAL ANSWER:'
        matches = list(re.finditer(r"FINAL ANSWER\s*:\s*(.+)", raw_output, re.IGNORECASE))
        if matches:
            final_answer = matches[-1].group(1).strip()
        else:
            lines = [l for l in raw_output.split("\n") if l.strip()]
            if lines:
                last_line = lines[-1].strip()
                if len(last_line) < 40:
                    final_answer = last_line
                else:
                    final_answer = "Review solution above"
            else:
                final_answer = "N/A"

        return SolverResult(
            solution=raw_output,
            final_answer=final_answer,
            tool_calls=tool_calls,
        )