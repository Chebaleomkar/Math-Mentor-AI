"""
Parser Agent
------------
Cleans raw OCR / ASR / typed text and returns a structured ParsedProblem.
Uses a JSON-mode prompt that works reliably with Groq models.
"""
import json
import re

from langchain_core.prompts import ChatPromptTemplate

from llm_router.router import router
from models.schemas import ParsedProblem


_SYSTEM = """You are a precise math problem parser.

Your job:
1. Clean any OCR / speech-to-text noise from the raw input.
2. Identify the math topic (algebra | calculus | probability | linear_algebra | other).
3. Extract variables and constraints if present.
4. Decide whether the problem is clear enough to solve, or needs human clarification.

Always respond with ONLY a valid JSON object — no markdown, no explanation.

JSON schema:
{{
  "problem_text": "<cleaned, unambiguous problem statement>",
  "topic": "<algebra | calculus | probability | linear_algebra | other>",
  "variables": ["<var1>", "..."],
  "constraints": ["<constraint1>", "..."],
  "needs_clarification": <true | false>,
  "clarification_reason": "<why clarification is needed, or empty string>"
}}
"""

_HUMAN = "Raw input:\n{raw_input}"


class ParserAgent:
    def __init__(self):
        self.llm = router.get_llm()
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", _SYSTEM), ("human", _HUMAN)]
        )

    def run(self, raw_input: str) -> ParsedProblem:
        chain = self.prompt | self.llm
        response = chain.invoke({"raw_input": raw_input})

        # Groq sometimes wraps JSON in ```json ... ``` — strip it
        text = response.content.strip()
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        data = json.loads(text)
        return ParsedProblem(**data)