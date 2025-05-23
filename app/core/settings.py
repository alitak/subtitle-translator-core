from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Application
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Storage
    STORAGE_DIR: str = "storage"
    SUBTITLES_DIR: str = "storage/subtitles"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create instance
settings = Settings()
