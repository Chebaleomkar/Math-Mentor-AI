import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from agents.solver_agent import SolverAgent
from pydantic import BaseModel

class ParsedProblem(BaseModel):
    problem_text: str

def test_solver():
    print("Testing solver agent...")
    agent = SolverAgent()
    problem = ParsedProblem(problem_text="What is the Pythagorean theorem?")
    result = agent.run(parsed_problem=problem)
    print("Context Used:\n", result["context_used"])
    print("\nSolution:\n", result["solution"])

if __name__ == "__main__":
    test_solver()
