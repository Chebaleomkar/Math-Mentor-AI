import os
import sys

# Add backend to path to allow importing core
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings


def get_retriever():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY
    )

    db_dir = os.path.join(current_dir, "db")

    vectordb = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings
    )

    retriever = vectordb.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever
