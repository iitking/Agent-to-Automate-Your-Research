from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import normalize_url


class SemanticScholarClient:
    """
    Live Semantic Scholar Graph API client.
    Fetches real academic paper records, citations, and publication metadata.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SEMANTIC_SCHOLAR_API_KEY
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,abstract,year,externalIds,citationCount,openAccessPdf,url",
        }

        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(self.base_url, headers=headers, params=params)
                if response.status_code == 429:
                    logger.warning("Semantic Scholar rate limited; skipping.")
                    return results
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.warning(f"Semantic Scholar API error: {e}")
                return results

        papers = data.get("data", [])
        for p in papers:
            title = p.get("title", "").strip()
            url = p.get("url") or (f"https://doi.org/{p.get('externalIds', {}).get('DOI')}" if p.get("externalIds", {}).get("DOI") else None)
            if not url or not title:
                continue

            authors = [a.get("name", "") for a in p.get("authors", []) if a.get("name")]
            year = str(p.get("year")) if p.get("year") else None
            abstract = p.get("abstract") or ""

            results.append({
                "title": title,
                "url": normalize_url(url),
                "snippet": abstract[:600] if abstract else f"Paper published in {year or 'recent years'}.",
                "author": ", ".join(authors[:4]) if authors else "Unknown",
                "published_at": year,
                "provider": "semantic_scholar",
                "source_type": "academic",
                "score": 0.88,
            })

        return results
