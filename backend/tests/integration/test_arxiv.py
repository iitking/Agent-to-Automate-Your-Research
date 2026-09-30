import pytest
from app.tools.academic.arxiv_client import ArxivClient


@pytest.mark.asyncio
async def test_live_arxiv_query():
    client = ArxivClient()
    # Query real arXiv database
    results = await client.search("quantum computing quantum error correction", max_results=3)

    # Real records must be returned
    assert len(results) > 0
    paper = results[0]
    assert paper["provider"] == "arxiv"
    assert paper["source_type"] == "academic"
    assert "arxiv.org" in paper["url"]
    assert len(paper["title"]) > 5
    assert len(paper["snippet"]) > 20
