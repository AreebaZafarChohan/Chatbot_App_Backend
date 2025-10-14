import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or ""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or ""

settings = Settings()
