from fastapi import APIRouter
from pydantic import BaseModel

from agents.parser_agent import ParserAgent
from agents.solver_agent import SolverAgent

router = APIRouter()

parser_agent = ParserAgent()
solver_agent = SolverAgent()

class QuestionRequest(BaseModel):
    question: str


@router.post("/parse")

def parse_question(request: QuestionRequest):
    result = parser_agent.run(request.question)
    return result

@router.post("/solve")

def solve(request: QuestionRequest):

    parsed = parser_agent.run(request.question)

    solution = solver_agent.run(parsed)

    return {
        "parsed": parsed,
        "solution": solution
    }