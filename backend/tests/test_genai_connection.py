import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.config import settings
from google import genai
from google.genai import types

def test_genai():
    print("Initializing Google GenAI client...")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    test_text = "What is the Pythagorean theorem?"
    print(f"Calling embed_content with text: '{test_text}'")
    
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=test_text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768,
            )
        )
        print("Success!")
        print(f"Embedding dimensions: {len(result.embeddings[0].values)}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_genai()
