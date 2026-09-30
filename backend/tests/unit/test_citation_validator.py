from app.tools.validation.citation_validator import validate_report_citations


def test_citation_validation():
    sources = [
        {"id": "src-1", "url": "https://arxiv.org/abs/2401.12345", "title": "AI Paper"},
        {"id": "src-2", "url": "https://nature.com/articles/s41586-024", "title": "Nature Review"},
    ]

    # Content referencing legitimate sources
    valid_markdown = """
    # Research Report
    Generative AI significantly alters workflows [AI Paper](https://arxiv.org/abs/2401.12345).
    Nature published landmark findings [Nature](https://nature.com/articles/s41586-024).
    """

    res = validate_report_citations(valid_markdown, sources)
    assert res.is_valid is True
    assert len(res.unresolved_citations) == 0
    assert res.coverage_score == 1.0

    # Content referencing a fabricated URL
    fabricated_markdown = """
    # Research Report
    Fake paper claim [Fake Paper](https://fake-journal.org/fabricated-study-123).
    """
    res_fake = validate_report_citations(fabricated_markdown, sources)
    assert res_fake.is_valid is False
    assert len(res_fake.unresolved_citations) == 1
