from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import is_safe_url, normalize_url


class TavilySearchClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a real web search via Tavily API.
        No dummy/mock fallback - raises if credentials missing or API fails.
        """
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not configured.")

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": max_results,
        }

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Tavily API HTTP error: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Tavily search failed: {e.response.text}") from e
            except Exception as e:
                logger.error(f"Tavily search request error: {e}")
                raise RuntimeError(f"Tavily search failed: {e}") from e

        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            url = item.get("url", "")
            if not url or not is_safe_url(url):
                continue

            results.append({
                "title": item.get("title", "").strip() or "Web Source",
                "url": normalize_url(url),
                "snippet": item.get("content", "").strip(),
                "score": float(item.get("score", 0.85)),
                "provider": "tavily",
                "source_type": "web",
                "published_at": item.get("published_date"),
            })

        return results
