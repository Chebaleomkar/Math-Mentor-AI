import re
import json
from llm_router.router import router
from tools.sympy_tool import solve_equation, derivative
from tools.python_tool import execute_python
from tools.rag_tool import retrieve_context

from langgraph.prebuilt import create_react_agent
from models.schemas import SolutionResult

_SYSTEM = """You are an expert JEE-level Math Solver Agent. You are highly intelligent and capable of reasoning through complex math problems (Algebra, Calculus, Probability, Linear Algebra).
        
Your PRIMARY job is to solve the problem using your mathematical intelligence.
        
You have access to these OPTIONAL tools:
- `retrieve_context`: Search the math knowledge base for formulas, concepts, or solution templates
- `solve_equation`: Use SymPy to solve algebraic equations exactly
- `derivative`: Use SymPy to calculate derivatives
- `execute_python`: Use for numerical calculations or evaluating complex arithmetic

INSTRUCTIONS:
1. Read and understand the problem thoroughly
2. Plan your solution approach
3. Solve step-by-step, showing your reasoning
4. Use tools when you need verification or get stuck
5. Provide the final answer clearly
6. Estimate your confidence in the solution (0-1)

When solving:
- Show ALL working steps
- Verify your answer when possible
- If using tools, explain why you're using them
- State your final answer clearly at the end
"""


class SolverAgent:
    """
    Solver Agent - Solves math problems using RAG + tools.
    
    Responsibilities:
    - Solve the problem using mathematical reasoning
    - Use tools when needed (RAG, sympy, python)
    - Provide step-by-step solution
    - Return confidence score
    """

    def __init__(self):
        self.llm = router.get_llm()
        
        # Tools the Agent can use
        self.tools = [solve_equation, derivative, execute_python, retrieve_context]
        
        # System prompt defining the agent's behavior
        self.prompt = _SYSTEM

        # Create LangGraph ReAct agent
        self.agent_executor = create_react_agent(
            self.llm, 
            tools=self.tools, 
            prompt=self.prompt
        )

    def run(self, parsed_problem):
        """
        Solve the parsed math problem.
        
        Args:
            parsed_problem: ParsedProblem from ParserAgent
            
        Returns:
            SolutionResult: Complete solution with steps and confidence
        """
        problem = parsed_problem.problem_text
        topic = parsed_problem.topic
        constraints = parsed_problem.constraints
        
        # Build context for the solver
        context = f"""Problem: {problem}
Topic: {topic}
Constraints: {', '.join(constraints)}

Solve this problem step by step. Show all your work and reasoning."""

        # Invoke the agent - it will use tools as needed
        response = self.agent_executor.invoke({"messages": [("user", context)]})
        
        # Extract the final response
        final_message = response["messages"][-1].content
        
        # Try to parse into structured format, fallback to raw if needed
        try:
            solution_result = self._parse_solution(final_message)
        except Exception:
            solution_result = SolutionResult(
                solution=final_message,
                steps=self._extract_steps(final_message),
                final_answer=self._extract_answer(final_message),
                confidence=0.7,
                tools_used=[]
            )
        
        return solution_result
    
    def _parse_solution(self, response: str) -> SolutionResult:
        """Parse the LLM response into structured SolutionResult."""
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return SolutionResult(
                    solution=data.get('solution', response),
                    steps=data.get('steps', []),
                    final_answer=data.get('final_answer', ''),
                    confidence=data.get('confidence', 0.7),
                    tools_used=data.get('tools_used', [])
                )
            except:
                pass
        
        return SolutionResult(
            solution=response,
            steps=self._extract_steps(response),
            final_answer=self._extract_answer(response),
            confidence=0.7,
            tools_used=[]
        )
    
    def _extract_steps(self, text: str) -> list:
        """Extract step-by-step solution from response."""
        lines = text.split('\n')
        steps = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                steps.append(line)
        return steps if steps else [text]
    
    def _extract_answer(self, text: str) -> str:
        """Extract the final answer from solution text."""
        patterns = [
            r'(?:answer|result|final answer)[:\s]+(.+?)(?:\n|$)',
            r'(?:∴|therefore|thus)[:\s]+(.+?)(?:\n|$)',
            r'(?:=|==)\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return lines[-1] if lines else ""