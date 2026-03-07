from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence

from llm_router.router import router
from models.schemas import ParsedProblem


class ParserAgent:
    """
    Parser Agent - Converts raw input (text/OCR/ASR) into structured problem format.
    
    Responsibilities:
    - Clean OCR/ASR output
    - Identify missing or ambiguous information
    - Convert question into structured format
    - Set needs_clarification flag if human input is required
    """

    def __init__(self):
        self.llm = router.get_llm()
        self.parser = PydanticOutputParser(pydantic_object=ParsedProblem)

        self.prompt = ChatPromptTemplate.from_template(
            """You are a math problem parser. Your job is to extract structured information 
from a math question and determine if it needs human clarification.

INSTRUCTIONS:
1. Extract the problem text cleanly
2. Identify the topic (algebra, calculus, probability, linear_algebra, geometry, trigonometry)
3. List all variables used
4. Note any constraints or conditions
5. Set needs_clarification=true ONLY if:
   - The problem text is ambiguous or unclear
   - Missing necessary information to solve
   - Mathematical notation is unclear (e.g., "x squared" vs "2x")

{format_instructions}

Question:
{question}
"""
        )

        # Create a runnable sequence for easier chaining
        self.chain: RunnableSequence = self.prompt | self.llm

    def run(self, question: str) -> ParsedProblem:
        """
        Parse a math question into structured format.
        
        Args:
            question: Raw question text (from user input, OCR, or ASR)
            
        Returns:
            ParsedProblem: Structured problem with topic, variables, constraints
        """
        formatted_prompt = self.prompt.format(
            question=question,
            format_instructions=self.parser.get_format_instructions()
        )

        response = self.llm.invoke(formatted_prompt)
        parsed = self.parser.parse(response.content)

        return parsed

    def run_with_confidence(self, question: str) -> dict:
        """
        Parse with confidence score for HITL decisions.
        
        Returns:
            dict: Contains parsed problem and confidence indicators
        """
        parsed = self.run(question)
        
        # Determine if we need HITL based on multiple factors
        needs_hitl = parsed.needs_clarification
        
        # Check for low information (short problems might be ambiguous)
        if len(parsed.problem_text.split()) < 5:
            needs_hitl = True
            
        return {
            "parsed": parsed,
            "needs_hitl": needs_hitl,
            "reason": "Ambiguous or incomplete problem" if needs_hitl else "Clear problem"
        }