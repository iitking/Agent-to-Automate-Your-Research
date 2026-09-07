import re
from typing import Any, Dict, List
from urllib.parse import unquote
from bs4 import BeautifulSoup
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import is_safe_url, normalize_url


class LiveWebSearchClient:
    """
    Direct live web search using DuckDuckGo's public search engine.
    Always retrieves live web pages - no mock data.
    Used when Tavily/Brave API keys are not supplied or as supplementary live search.
    """
    def __init__(self):
        self.endpoint = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(headers=self.headers, timeout=settings.REQUEST_TIMEOUT, follow_redirects=True) as client:
            try:
                response = await client.post(self.endpoint, data={"q": query})
                if response.status_code != 200:
                    logger.warning(f"DuckDuckGo search returned status {response.status_code}")
                    return results

                soup = BeautifulSoup(response.text, "html.parser")
                web_elements = soup.find_all("div", class_="result")

                for el in web_elements:
                    if len(results) >= max_results:
                        break

                    title_tag = el.find("a", class_="result__a")
                    snippet_tag = el.find("a", class_="result__snippet")

                    if not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    raw_href = title_tag.get("href", "")

                    # Extract actual target URL from DDG redirect url (uddg parameter)
                    match = re.search(r"uddg=([^&]+)", raw_href)
                    if match:
                        actual_url = unquote(match.group(1))
                    elif raw_href.startswith("http"):
                        actual_url = raw_href
                    else:
                        continue

                    if not is_safe_url(actual_url):
                        continue

                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    results.append({
                        "title": title or "Web Source",
                        "url": normalize_url(actual_url),
                        "snippet": snippet,
                        "score": 0.8,
                        "provider": "live_web",
                        "source_type": "web",
                        "published_at": None,
                    })

            except Exception as e:
                logger.error(f"Live web search request failed: {e}")
                raise RuntimeError(f"Live web search failed: {e}") from e

        return results
