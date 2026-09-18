import asyncio
from typing import Any, Dict, List
from app.core.logging import logger
from app.tools.extraction.trafilatura_extractor import TrafilaturaExtractor
from app.tools.extraction.pdf_extractor import PDFExtractor
from app.tools.extraction.playwright_extractor import PlaywrightExtractor


class InformationExtractionAgent:
    """
    Information Extraction Agent:
    - Retrieves real accessible pages using Trafilatura and PDF extractor.
    - Handles HTML articles, academic abstracts, and PDF files.
    - Preserves source provenance and records extraction statuses honestly.
    """
    def __init__(self):
        self.html_extractor = TrafilaturaExtractor()
        self.pdf_extractor = PDFExtractor()
        self.browser_extractor = PlaywrightExtractor()

    async def extract_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Information Extraction Agent extracting content from {len(sources)} sources.")

        extracted_sources: List[Dict[str, Any]] = []

        async def process_single(source: Dict[str, Any]):
            url = source.get("url", "")
            source_type = source.get("source_type", "web")
            pdf_url = source.get("pdf_url") or (url if url.lower().endswith(".pdf") else None)

            # If PDF available
            if pdf_url:
                text, status, content_hash, pages = await self.pdf_extractor.extract_pdf(pdf_url)
                if status == "success" and text:
                    source["extraction_status"] = "success"
                    source["extracted_text"] = text
                    source["content_hash"] = content_hash
                    source["content_length"] = len(text)
                    source["page_count"] = pages
                    return source

            # Web HTML extraction
            text, status, content_hash = await self.html_extractor.extract_content(url)
            if status == "success" and text:
                source["extraction_status"] = "success"
                source["extracted_text"] = text
                source["content_hash"] = content_hash
                source["content_length"] = len(text)
            else:
                # If extraction failed but search returned a detailed snippet/abstract, retain it with honest status
                snippet = source.get("snippet", "")
                if snippet and len(snippet) > 100:
                    source["extraction_status"] = "snippet_only"
                    source["extracted_text"] = snippet
                    source["content_length"] = len(snippet)
                else:
                    source["extraction_status"] = status
                    source["extracted_text"] = None
                    source["content_length"] = 0

            return source

        # Concurrently extract with a concurrency semaphore
        semaphore = asyncio.Semaphore(5)

        async def sem_process(s):
            async with semaphore:
                return await process_single(s)

        results = await asyncio.gather(*[sem_process(s) for s in sources], return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                logger.warning(f"Source extraction worker error: {res}")
            elif isinstance(res, dict):
                extracted_sources.append(res)

        successful = sum(1 for s in extracted_sources if s.get("extraction_status") in ("success", "snippet_only"))
        logger.info(f"Extraction complete: {successful}/{len(extracted_sources)} sources successfully extracted.")
        return extracted_sources
