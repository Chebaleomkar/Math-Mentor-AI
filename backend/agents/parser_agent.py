from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from llm_router.router import router
from models.schemas import ParsedProblem


class ParserAgent:

    def __init__(self):

        self.llm = router.get_llm()

        self.parser = PydanticOutputParser(pydantic_object=ParsedProblem)

        self.prompt = ChatPromptTemplate.from_template(
            """
You are a math problem parser.

Extract structured information from the math question.

Return JSON.

{format_instructions}

Question:
{question}
"""
        )

    def run(self, question: str):

        formatted_prompt = self.prompt.format(
            question=question,
            format_instructions=self.parser.get_format_instructions()
        )

        response = self.llm.invoke(formatted_prompt)

        parsed = self.parser.parse(response.content)

        return parsed