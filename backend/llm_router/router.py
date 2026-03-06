from langchain_groq import ChatGroq
from core.config import settings


class LLMRouter:

    def __init__(self):
        self.primary_model = "llama-3.3-70b-versatile"

    def get_llm(self):

        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=self.primary_model,
            temperature=0
        )

        return llm


router = LLMRouter()