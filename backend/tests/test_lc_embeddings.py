import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings

def test_models():
    models_to_test = [
        "models/embedding-001",
        "embedding-001",
        "models/text-embedding-004",
        "text-embedding-004",
        "models/gemini-embedding-001",
        "gemini-embedding-001"
    ]
    
    for m in models_to_test:
        print(f"Testing model: {m}...")
        try:
            emb = GoogleGenerativeAIEmbeddings(
                model=m,
                google_api_key=settings.GEMINI_API_KEY
            )
            res = emb.embed_query("hello world")
            print(f"Success! {m} works. Embedding dimension: {len(res)}\n")
        except Exception as e:
            print(f"Error for {m}: {e}\n")

if __name__ == "__main__":
    test_models()
