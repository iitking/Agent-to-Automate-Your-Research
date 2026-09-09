from typing import Any, Dict, List
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import normalize_url


class CrossrefClient:
    """
    Live Crossref REST API client.
    Fetches real peer-reviewed DOI metadata.
    """
    def __init__(self):
        self.base_url = "https://api.crossref.org/works"
        self.headers = {
            "User-Agent": "ResearchAgent/1.0 (mailto:support@researchagent.local)"
        }

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "rows": limit,
        }

        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(self.base_url, params=params)
                if response.status_code != 200:
                    logger.warning(f"Crossref returned status {response.status_code}")
                    return results
                data = response.json()
            except Exception as e:
                logger.warning(f"Crossref API error: {e}")
                return results

        items = data.get("message", {}).get("items", [])
        for item in items:
            titles = item.get("title", [])
            title = titles[0].strip() if titles else ""
            doi = item.get("DOI", "")
            url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)

            if not url or not title:
                continue

            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)

            publisher = item.get("publisher", "")
            created_parts = item.get("created", {}).get("date-parts", [[]])[0]
            year = str(created_parts[0]) if created_parts else None

            results.append({
                "title": title,
                "url": normalize_url(url),
                "snippet": f"Published by {publisher} in {year or 'academic record'}. DOI: {doi}",
                "author": ", ".join(authors[:3]) if authors else publisher or "Unknown",
                "published_at": year,
                "provider": "crossref",
                "source_type": "academic",
                "score": 0.85,
            })

        return results
