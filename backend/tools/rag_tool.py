from rag.retriever import get_retriever
from langchain_core.tools import tool

retriever = get_retriever()

@tool
def retrieve_context(query: str) -> str:
    """Searches the math knowledge base for relevant formulas, concepts, or templates."""
    docs = retriever.invoke(query)
    context = [doc.page_content for doc in docs]
    return "\n".join(context)
