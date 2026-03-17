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

        # Groq/LLMs often output LaTeX with single backslashes which breaks JSON
        # e.g. {"text": "\int"} is invalid. We need {"text": "\\int"}
        # Escape backslashes that aren't already part of an escape sequence
        # We'll use a simple heuristic: replace \ with \\ unless it's already escaped or a valid escape
        text = text.replace('\\', '\\\\')
        # But wait, if the LLM *did* output \\, we now have \\\\. Let's fix that.
        text = text.replace('\\\\\\\\', '\\\\')
        # Also fix common quotes issue if any
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: if we still can't parse, try a more aggressive regex cleanup
            # or just try to extract the problem_text field manually if it's really broken
            try:
                # Minimal fix: sometimes the model adds extra quotes or doesn't escape newlines
                text_alt = re.sub(r'\n', ' ', text)
                data = json.loads(text_alt)
            except:
                # Note: HTTPException is not defined in this file, assuming it's imported elsewhere or needs to be added.
                # For now, raising a generic Exception or logging.
                raise Exception(f"LLM returned invalid JSON after multiple attempts: {text[:100]}...")

        return ParsedProblem(**data)