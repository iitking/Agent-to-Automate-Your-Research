from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import is_safe_url, normalize_url


class BraveSearchClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Executes real web search via Brave Search API.
        """
        if not self.api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY is not configured.")

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": count,
        }

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Brave search API error: {e}")
                raise RuntimeError(f"Brave search failed: {e}") from e

        results: List[Dict[str, Any]] = []
        web_results = data.get("web", {}).get("results", [])
        for item in web_results:
            url = item.get("url", "")
            if not url or not is_safe_url(url):
                continue

            results.append({
                "title": item.get("title", "").strip() or "Web Source",
                "url": normalize_url(url),
                "snippet": item.get("description", "").strip(),
                "score": 0.8,
                "provider": "brave",
                "source_type": "web",
                "published_at": item.get("page_age"),
            })

        return results
