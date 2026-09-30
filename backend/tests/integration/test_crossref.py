import pytest
from app.tools.academic.crossref_client import CrossrefClient


@pytest.mark.asyncio
async def test_live_crossref_query():
    client = CrossrefClient()
    results = await client.search("machine learning transformers", limit=3)

    assert len(results) > 0
    work = results[0]
    assert work["provider"] == "crossref"
    assert work["source_type"] == "academic"
    assert "doi.org" in work["url"] or "http" in work["url"]
    assert len(work["title"]) > 3
