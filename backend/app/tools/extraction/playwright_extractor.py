import hashlib
from typing import Optional, Tuple
from app.core.logging import logger
from app.tools.extraction.trafilatura_extractor import TrafilaturaExtractor


class PlaywrightExtractor:
    """
    Browser extraction for JavaScript-rendered web pages.
    Falls back cleanly to Trafilatura extractor when browser execution is unneeded or unavailable.
    """
    def __init__(self):
        self.trafilatura = TrafilaturaExtractor()

    async def extract(self, url: str) -> Tuple[Optional[str], str, Optional[str]]:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=15000)
                content = await page.content()
                await browser.close()

                import trafilatura
                text = trafilatura.extract(content, include_comments=False)
                if text and len(text.strip()) > 100:
                    chash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    return text.strip(), "success", chash
        except Exception as e:
            logger.info(f"Playwright browser rendering unavailable ({e}); falling back to HTTP extractor.")

        return await self.trafilatura.extract_content(url)
