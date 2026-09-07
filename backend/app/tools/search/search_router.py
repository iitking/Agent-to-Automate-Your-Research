from typing import Any, Dict, List
from app.core.config import settings
from app.core.logging import logger
from app.tools.search.tavily_client import TavilySearchClient
from app.tools.search.brave_client import BraveSearchClient
from app.tools.search.ddg_client import LiveWebSearchClient


class SearchRouter:
    """
    Intelligent router for live web searches.
    Prioritizes Tavily -> Brave -> Live Web search.
    Never uses mock data.
    """
    def __init__(self):
        self.tavily = TavilySearchClient() if settings.TAVILY_API_KEY else None
        self.brave = BraveSearchClient() if settings.BRAVE_SEARCH_API_KEY else None
        self.live_web = LiveWebSearchClient()

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if self.tavily:
            try:
                logger.info(f"Searching via Tavily: {query}")
                return await self.tavily.search(query, max_results=max_results)
            except Exception as e:
                logger.warning(f"Tavily search failed, attempting fallback: {e}")

        if self.brave:
            try:
                logger.info(f"Searching via Brave: {query}")
                return await self.brave.search(query, count=max_results)
            except Exception as e:
                logger.warning(f"Brave search failed, attempting fallback: {e}")

        logger.info(f"Searching via live web search: {query}")
        return await self.live_web.search(query, max_results=max_results)
