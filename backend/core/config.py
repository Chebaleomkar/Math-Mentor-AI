import os
from dotenv import load_dotenv

# Try multiple locations for .env file
possible_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),  # backend/.env
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),  # root/.env
    '.env',  # current directory
]

for env_path in possible_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    INDEX_NAME = "math-mentor-kb"
    
    # Absolute path to the backend directory
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHROMA_DB_DIR = os.path.join(BACKEND_DIR, "chroma_db")

settings = Settings()