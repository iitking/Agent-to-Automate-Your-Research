import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "ResearchAgent"
    LOG_LEVEL: str = "INFO"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" | "ollama"
    LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Local LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Web Search
    TAVILY_API_KEY: Optional[str] = None
    BRAVE_SEARCH_API_KEY: Optional[str] = None

    # Academic Search
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None

    # Database: SQLite default for easy single-step startup; Asyncpg for PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./research.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Research Execution Limits
    MAX_RESEARCH_ITERATIONS: int = 3
    MAX_SEARCH_QUERIES: int = 15
    MAX_SOURCES: int = 20

    # Network and Content
    REQUEST_TIMEOUT: int = 30
    MAX_DOCUMENT_SIZE_MB: int = 15
    EXPORTS_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "exports")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure exports directory exists
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
