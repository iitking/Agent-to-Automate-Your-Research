from typing import Any, Dict, List


def calculate_source_relevance(sources: List[Dict[str, Any]]) -> float:
    if not sources:
        return 0.0
    scores = [s.get("relevance_score", 0.0) for s in sources]
    return round(sum(scores) / len(scores), 3)


def calculate_claim_verification_rate(claims: List[Dict[str, Any]]) -> float:
    if not claims:
        return 0.0
    verified = [c for c in claims if c.get("verification_status") in ("supported", "partially_supported")]
    return round(len(verified) / len(claims), 3)


def calculate_citation_grounding(report_markdown: str, sources: List[Dict[str, Any]]) -> float:
    from app.tools.validation.citation_validator import validate_report_citations
    res = validate_report_citations(report_markdown, sources)
    return res.coverage_score
