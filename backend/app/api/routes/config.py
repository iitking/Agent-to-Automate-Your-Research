from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/api/config", tags=["Configuration"])


class ConfigStatus(BaseModel):
    llm_provider: str
    llm_model: str
    gemini_key_configured: bool
    openai_key_configured: bool
    tavily_key_configured: bool
    brave_key_configured: bool
    database_url: str
    max_sources: int


class UpdateConfigPayload(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    llm_provider: Optional[str] = None


@router.get("", response_model=ConfigStatus)
async def get_config():
    return ConfigStatus(
        llm_provider=settings.LLM_PROVIDER,
        llm_model=settings.LLM_MODEL,
        gemini_key_configured=bool(settings.GEMINI_API_KEY),
        openai_key_configured=bool(settings.OPENAI_API_KEY),
        tavily_key_configured=bool(settings.TAVILY_API_KEY),
        brave_key_configured=bool(settings.BRAVE_SEARCH_API_KEY),
        database_url="sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
        max_sources=settings.MAX_SOURCES,
    )


@router.post("")
async def update_config(payload: UpdateConfigPayload):
    """Allows updating runtime API keys from the settings UI."""
    if payload.gemini_api_key:
        settings.GEMINI_API_KEY = payload.gemini_api_key.strip()
    if payload.openai_api_key:
        settings.OPENAI_API_KEY = payload.openai_api_key.strip()
    if payload.tavily_api_key:
        settings.TAVILY_API_KEY = payload.tavily_api_key.strip()
    if payload.brave_api_key:
        settings.BRAVE_SEARCH_API_KEY = payload.brave_api_key.strip()
    if payload.llm_provider:
        settings.LLM_PROVIDER = payload.llm_provider.strip().lower()

    logger.info("Runtime API keys updated from client.")
    return {"status": "success", "message": "Settings updated successfully."}
