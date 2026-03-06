import os
from google import genai
from google.genai import types
import chromadb
from typing import List, Dict, Any

from core.config import settings

def get_genai_client():
    if not settings.GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY in environment.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using Google AI."""
    client = get_genai_client()
    
    # Truncate if too long (rough approximation for tokens)
    if len(text) > 8000:
        text = text[:8000]
    
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        )
    )
    return result.embeddings[0].values

def get_chroma_collection():
    """Initializes and returns the ChromaDB collection."""
    # Ensure the directory exists
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
    
    # Get or create the collection
    collection = client.get_or_create_collection(
        name=settings.INDEX_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def retrieve_math_context(query: str, k: int = 3) -> str:
    """
    Functional retriever that fetches relevant math context from ChromaDB.
    Outputs a formatted string for the LLM to use.
    """
    collection = get_chroma_collection()
    
    # Generate embedding for the query
    query_embedding = generate_embedding(query)
    
    # Search ChromaDB
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["metadatas", "documents"]
    )
    
    if not response['documents'] or not response['documents'][0]:
        return "No specific math documentation found for this query."
        
    context = "### MATH KNOWLEDGE BASE CONTEXT ###\n"
    
    # Chroma returns lists of lists (for batched queries)
    documents = response['documents'][0]
    metadatas = response['metadatas'][0] if response['metadatas'] else [{}] * len(documents)
    
    for doc, metadata in zip(documents, metadatas):
        source = metadata.get("source", "Reference")
        
        # Extract filename from path if it's a full path
        source_name = os.path.basename(source)
        context += f"\n--- From: {source_name} ---\n{doc}\n"
        
    return context
