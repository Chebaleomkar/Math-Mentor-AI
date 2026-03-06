from fastapi import APIRouter
from pydantic import BaseModel

from agents.parser_agent import ParserAgent

router = APIRouter()

parser_agent = ParserAgent()


class QuestionRequest(BaseModel):
    question: str


@router.post("/parse")

def parse_question(request: QuestionRequest):
    result = parser_agent.run(request.question)
    return result