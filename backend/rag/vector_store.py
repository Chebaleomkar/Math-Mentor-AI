import os
import sys

# Add backend to path to allow importing core
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings

def build_vector_store():
    # Use the existing knowledge_base directory inside rag folder
    kb_dir = os.path.join(current_dir, "knowledge_base")
    db_dir = os.path.join(current_dir, "db")

    loader = DirectoryLoader(kb_dir, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY
    )

    vectordb = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings
    )

    import time
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Adding chunks {i} to {i+len(batch)} of {len(chunks)}...")
        vectordb.add_documents(batch)
        time.sleep(6)  # Avoid Free Tier 15 RPM limits

    vectordb.persist()

    return vectordb

if __name__ == "__main__":
    print("Building vector store...")
    build_vector_store()
    print("Done!")
