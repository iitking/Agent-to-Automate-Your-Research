import hashlib
from typing import Dict, Optional, Tuple
import httpx
import trafilatura
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import is_safe_url


class TrafilaturaExtractor:
    """
    Real content extraction tool using Trafilatura and HTTPX.
    Extracts article text and metadata from live accessible web pages.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def extract_content(self, url: str) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Retrieves live URL and extracts text content.
        Returns: (extracted_text, status, content_hash)
        """
        if not is_safe_url(url):
            return None, "failed: unsafe_url", None

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=settings.REQUEST_TIMEOUT,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            ) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return None, f"failed: HTTP {response.status_code}", None

                # Limit document size to prevent memory bloat
                max_bytes = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024
                if len(response.content) > max_bytes:
                    return None, "failed: document_too_large", None

                html = response.text

            # Extract main article text with trafilatura
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_recall=True,
            )

            if not text or len(text.strip()) < 100:
                # If trafilatura fails to parse body, fallback to basic text extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)

            if not text or len(text.strip()) < 80:
                return None, "failed: insufficient_text", None

            cleaned_text = text.strip()
            content_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
            return cleaned_text, "success", content_hash

        except Exception as e:
            logger.warning(f"Extraction failed for {url}: {e}")
            return None, f"failed: {str(e)[:100]}", None
