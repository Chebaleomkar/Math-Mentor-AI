import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    INDEX_NAME = "math-mentor-kb"
    
    # Absolute path to the backend directory
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHROMA_DB_DIR = os.path.join(BACKEND_DIR, "chroma_db")

settings = Settings()