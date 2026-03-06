import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.config import settings
from pinecone import Pinecone

def test_pinecone_connection():
    print("Testing Pinecone connection...")
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        print("Connected.")
        indexes = pc.list_indexes()
        print(f"Indexes found: {[index['name'] for index in indexes]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pinecone_connection()
