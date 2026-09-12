import hashlib
import io
from typing import Optional, Tuple
import pymupdf  # PyMuPDF
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.tools.validation.url_validator import is_safe_url


class PDFExtractor:
    """
    Real PDF text extractor using PyMuPDF (fitz).
    Extracts text from accessible live PDF files with page numbers.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "ResearchAgent/1.0 (PDF Extractor; mailto:support@researchagent.local)"
        }

    async def extract_pdf(self, url: str) -> Tuple[Optional[str], str, Optional[str], int]:
        """
        Extracts text from a remote PDF file.
        Returns: (extracted_text, status, content_hash, page_count)
        """
        if not is_safe_url(url):
            return None, "failed: unsafe_url", None, 0

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=settings.REQUEST_TIMEOUT + 15,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return None, f"failed: HTTP {response.status_code}", None, 0

                max_bytes = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024
                if len(response.content) > max_bytes:
                    return None, "failed: pdf_too_large", None, 0

                pdf_bytes = response.content

            # Open with PyMuPDF
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            page_count = len(doc)
            if page_count == 0:
                return None, "failed: empty_pdf", None, 0

            text_parts = []
            # Extract first 30 pages max to stay fast and focused
            max_pages = min(page_count, 30)
            for page_num in range(max_pages):
                page = doc.load_page(page_num)
                page_text = page.get_text("text").strip()
                if page_text:
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")

            full_text = "\n\n".join(text_parts).strip()
            if not full_text or len(full_text) < 100:
                return None, "failed: scanned_or_empty_text", None, page_count

            content_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
            return full_text, "success", content_hash, page_count

        except Exception as e:
            logger.warning(f"PDF extraction failed for {url}: {e}")
            return None, f"failed: {str(e)[:100]}", None, 0
