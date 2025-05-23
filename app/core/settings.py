from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Storage
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "storage")
    SUBTITLES_DIR: str = os.path.join(STORAGE_DIR, "subtitles")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create instance
settings = Settings()
