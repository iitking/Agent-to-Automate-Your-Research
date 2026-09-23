import re
from typing import Dict, List, Set, Tuple


class CitationValidationResult:
    def __init__(
        self,
        is_valid: bool,
        valid_citations: List[str],
        unresolved_citations: List[str],
        unused_sources: List[str],
        coverage_score: float,
        details: str,
    ):
        self.is_valid = is_valid
        self.valid_citations = valid_citations
        self.unresolved_citations = unresolved_citations
        self.unused_sources = unused_sources
        self.coverage_score = coverage_score
        self.details = details


def validate_report_citations(
    markdown_content: str,
    source_records: List[Dict],
) -> CitationValidationResult:
    """
    Validates that:
    1. Every citation key or reference [Source: ...] or [1], [2], etc.
       matches an actual retrieved source in source_records.
    2. Calculates citation coverage and flags any fabricated or orphan citations.
    """
    valid_source_ids: Set[str] = {str(s.get("id")) for s in source_records if s.get("id")}
    valid_urls: Set[str] = {s.get("url", "").rstrip("/") for s in source_records if s.get("url")}
    
    # Extract markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
    found_links = link_pattern.findall(markdown_content)

    valid_citations: List[str] = []
    unresolved_citations: List[str] = []
    used_source_urls: Set[str] = set()

    for text, url in found_links:
        clean_url = url.rstrip("/")
        if clean_url in valid_urls:
            valid_citations.append(f"{text} -> {clean_url}")
            used_source_urls.add(clean_url)
        else:
            unresolved_citations.append(f"{text} -> {clean_url}")

    # Extract [Source-ID: ...] if any
    source_id_pattern = re.compile(r'\[(?:Source|Ref):?\s*([a-zA-Z0-9_-]+)\]', re.IGNORECASE)
    found_ids = source_id_pattern.findall(markdown_content)
    for sid in found_ids:
        if sid in valid_source_ids:
            valid_citations.append(f"ID:{sid}")
        else:
            unresolved_citations.append(f"Unknown-ID:{sid}")

    total_citations = len(valid_citations) + len(unresolved_citations)
    coverage = (len(valid_citations) / total_citations) if total_citations > 0 else 1.0
    unused_sources = [
        s.get("url") for s in source_records
        if s.get("url") and s.get("url").rstrip("/") not in used_source_urls
    ]

    is_valid = len(unresolved_citations) == 0

    details = (
        f"Verified {len(valid_citations)} citations. "
        f"Unresolved citations: {len(unresolved_citations)}. "
        f"Sources utilized in report: {len(used_source_urls)}/{len(source_records)}."
    )

    return CitationValidationResult(
        is_valid=is_valid,
        valid_citations=valid_citations,
        unresolved_citations=unresolved_citations,
        unused_sources=unused_sources,
        coverage_score=round(coverage, 2),
        details=details,
    )
