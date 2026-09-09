import xml.etree.ElementTree as ET
from typing import Any, Dict, List
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import normalize_url


class ArxivClient:
    """
    Live arXiv API client.
    Fetches real peer-reviewed preprints and metadata from export.arxiv.org.
    No mock data.
    """
    def __init__(self):
        self.base_url = "https://export.arxiv.org/api/query"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT, follow_redirects=True) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                content = response.text
            except Exception as e:
                logger.error(f"arXiv API request failed: {e}")
                raise RuntimeError(f"arXiv search failed: {e}") from e

        results: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(content)
            # Atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                published_elem = entry.find("atom:published", ns)
                id_elem = entry.find("atom:id", ns)

                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "arXiv Paper"
                summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else ""
                published = published_elem.text.strip() if published_elem is not None and published_elem.text else None
                entry_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""

                authors = []
                for author_elem in entry.findall("atom:author", ns):
                    name_elem = author_elem.find("atom:name", ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())

                # Find PDF link
                pdf_url = ""
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                        pdf_url = link.get("href", "")
                        break

                url = entry_id or pdf_url
                if url:
                    results.append({
                        "title": title,
                        "url": normalize_url(url),
                        "snippet": summary[:600],
                        "author": ", ".join(authors[:5]) if authors else "Unknown",
                        "published_at": published[:10] if published else None,
                        "provider": "arxiv",
                        "source_type": "academic",
                        "score": 0.9,
                        "pdf_url": pdf_url,
                    })

        except Exception as e:
            logger.error(f"Failed to parse arXiv XML response: {e}")

        return results
