from typing import Any, Dict, List, Optional, TypedDict


class ResearchState(TypedDict, total=False):
    research_id: str
    user_query: str
    research_depth: str
    include_academic: bool
    max_sources: int
    output_formats: List[str]

    # Plan
    research_plan: Dict[str, Any]
    sub_questions: List[str]
    search_queries: List[str]

    # Search & Extraction
    search_results: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    extracted_documents: List[Dict[str, Any]]
    evaluated_sources: List[Dict[str, Any]]

    # Analysis & Verification
    findings: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    verified_claims: List[Dict[str, Any]]
    evidence_sufficient: bool

    # Report & Exports
    final_report: str
    pdf_path: Optional[str]
    docx_path: Optional[str]
    markdown_path: Optional[str]

    # Execution controls
    iteration_count: int
    max_iterations: int
    current_agent: str
    progress: int
    errors: List[str]
    status: str
