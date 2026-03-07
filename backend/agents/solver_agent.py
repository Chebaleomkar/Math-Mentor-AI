"""Solver Agent - Solves math problems using RAG + tools + Memory context."""

from llm_router.router import router
from tools.sympy_tool import solve_equation, derivative
from tools.python_tool import execute_python
from tools.rag_tool import retrieve_context

from langgraph.prebuilt import create_react_agent


class SolverAgent:
    def __init__(self):
        self.llm = router.get_llm()
        
        # 1. Provide all tools the Agent has access to
        self.tools = [solve_equation, derivative, execute_python, retrieve_context]

        # 2. Define the Agent's reasoning prompt
        prompt = """You are an expert Math Solver Agent. You are highly intelligent and capable of reasoning through complex math problems (Algebra, Calculus, Probability, Linear Algebra).
            
            You should solve the problem primarily using your own reasoning and mathematical intelligence. However, you also have access to the following optional tools to ensure accuracy:
            - `retrieve_context`: Use this to look up specific forgotten formulas or math concepts from the knowledge base.
            - `solve_equation` & `derivative`: Use these to verify roots, factors, or complex algebraic derivatives.
            - `execute_python`: Use this for raw numerical calculations or evaluating complex arithmetic.
            
            You don't have to use tools if you are confident in your own solution, but they are available to ensure accuracy. Always explain your step-by-step reasoning clearly."""

        # 3. Create the LangGraph Agent execution pipeline
        self.agent_executor = create_react_agent(self.llm, tools=self.tools, prompt=prompt)

    def run(self, parsed_problem, memory_context=None):
        """
        Solve a math problem.
        
        Args:
            parsed_problem: ParsedProblem object from Parser Agent
            memory_context: Optional memory context from Memory Layer
            
        Returns:
            SolutionResult with solution, steps, final_answer, confidence, tools_used
        """
        problem = parsed_problem.problem_text
        topic = parsed_problem.topic
        
        # Build context string
        context_parts = [f"Problem: {problem}", f"Topic: {topic}"]
        
        if parsed_problem.variables:
            context_parts.append(f"Variables: {', '.join(parsed_problem.variables)}")
        
        if parsed_problem.constraints:
            context_parts.append(f"Constraints: {', '.join(parsed_problem.constraints)}")
        
        # Add memory context if available
        if memory_context and memory_context.get("has_memory"):
            context_parts.append("\n" + memory_context.get("context", ""))
        
        context = "\n".join(context_parts)
        
        # The LLM will now automatically invoke tools as many times as it needs to find the answer!
        response = self.agent_executor.invoke({"messages": [("user", context)]})
        
        solution_text = response["messages"][-1].content
        
        # Parse solution into structured format
        parsed_solution = self._parse_solution(solution_text)
        
        return parsed_solution
    
    def _parse_solution(self, solution_text: str) -> dict:
        """Parse the LLM response into a structured solution result."""
        import re
        
        result = {
            "solution": solution_text,
            "steps": [],
            "final_answer": "",
            "confidence": 0.8,
            "tools_used": []
        }
        
        # Try to extract final answer
        answer_patterns = [
            r'(?:answer|solution|result|therefore|thus|hence)\s*[:=]?\s*\(?([A-Za-z0-9\.\-\s=]+?)\)?',
            r'x\s*=\s*([\d\.\-]+)',
            r'y\s*=\s*([\d\.\-]+)',
            r'\$\$([^^]+)\$\$',
            r'final.*?[:=]\s*([^\n]+)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, solution_text, re.IGNORECASE)
            if match:
                result["final_answer"] = match.group(1).strip()
                break
        
        # Try to extract steps
        step_pattern = r'(?:step\s*\d+|\d+\.|\-)\s*([^\n]+)'
        steps = re.findall(step_pattern, solution_text, re.IGNORECASE)
        if steps:
            result["steps"] = steps[:5]  # Limit to 5 steps
        
        return result
