from llm_router.router import router
from rag.retriever import get_retriever


class SolverAgent:

    def __init__(self):

        self.llm = router.get_llm()
        self.retriever = get_retriever()

    def run(self, parsed_problem):

        query = parsed_problem.problem_text

        docs = self.retriever.invoke(query)

        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a math solver.

Use the provided context if useful.

Context:
{context}

Problem:
{query}

Solve the problem step by step.
"""

        response = self.llm.invoke(prompt)

        return {
            "context_used": context,
            "solution": response.content
        }