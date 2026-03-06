from pydantic import BaseModel
from typing import List

class ParsedProblem(BaseModel):
    
    problem_text: str
    topic: str
    variables: List[str]
    constraints: List[str]
    needs_clarification: bool