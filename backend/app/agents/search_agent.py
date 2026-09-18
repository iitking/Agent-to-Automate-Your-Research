import asyncio
import uuid
from typing import Any, Dict, List
from app.core.config import settings
from app.core.logging import logger
from app.tools.search.search_router import SearchRouter
from app.tools.academic.arxiv_client import ArxivClient
from app.tools.academic.semantic_scholar_client import SemanticScholarClient
from app.tools.academic.crossref_client import CrossrefClient
from app.tools.validation.url_validator import normalize_url


class ResearchSearchAgent:
    """
    Research Search Agent:
    - Executes actual API calls against live web and academic engines.
    - Normalizes results into a common schema.
    - Eliminates duplicate URLs.
    - Records provider metadata.
    """
    def __init__(self):
        self.web_router = SearchRouter()
        self.arxiv = ArxivClient()
        self.semantic_scholar = SemanticScholarClient()
        self.crossref = CrossrefClient()

    async def execute_search(
        self,
        queries: List[str],
        include_academic: bool = True,
        max_sources: int = 20,
    ) -> List[Dict[str, Any]]:
        logger.info(f"Search Agent executing queries across web and academic providers (max: {max_sources})")

        collected_sources: List[Dict[str, Any]] = []
        seen_urls: set[str] = set()

        # Deduplicate and limit queries
        target_queries = list(dict.fromkeys(queries))[:settings.MAX_SEARCH_QUERIES]

        for query in target_queries:
            if len(collected_sources) >= max_sources:
                break

            tasks = [self.web_router.search(query, max_results=4)]
            if include_academic:
                tasks.append(self.arxiv.search(query, max_results=3))
                tasks.append(self.crossref.search(query, limit=3))
                if settings.SEMANTIC_SCHOLAR_API_KEY:
                    tasks.append(self.semantic_scholar.search(query, limit=3))

            results_groups = await asyncio.gather(*tasks, return_exceptions=True)

            for group in results_groups:
                if isinstance(group, Exception):
                    logger.warning(f"Search query error: {group}")
                    continue
                for item in group:
                    url = item.get("url")
                    if not url:
                        continue
                    clean_url = normalize_url(url)
                    if clean_url in seen_urls:
                        continue

                    seen_urls.add(clean_url)
                    item["id"] = str(uuid.uuid4())
                    item["url"] = clean_url
                    collected_sources.append(item)

                    if len(collected_sources) >= max_sources:
                        break

        logger.info(f"Search Agent collected {len(collected_sources)} unique real sources.")
        return collected_sources
