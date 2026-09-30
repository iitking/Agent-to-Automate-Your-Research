import pytest
from app.tools.extraction.trafilatura_extractor import TrafilaturaExtractor


@pytest.mark.asyncio
async def test_live_trafilatura_extraction():
    extractor = TrafilaturaExtractor()
    # Live URL with well-formatted public text
    url = "https://en.wikipedia.org/wiki/Deep_learning"
    text, status, content_hash = await extractor.extract_content(url)

    assert status == "success"
    assert text is not None
    assert len(text) > 500
    assert content_hash is not None
    assert "neural" in text.lower() or "learning" in text.lower()
