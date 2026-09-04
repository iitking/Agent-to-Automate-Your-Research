from typing import Optional
from pydantic import BaseModel


class FindingItem(BaseModel):
    id: str
    research_task_id: str
    question: str
    finding: str
    confidence: float = 0.9
    source_ids: list[str] = []

    class Config:
        from_attributes = True


class ClaimItem(BaseModel):
    id: str
    research_task_id: str
    claim_text: str
    verification_status: str  # supported, partially_supported, contradicted, insufficient_evidence
    supporting_passage: Optional[str] = None
    page_number: Optional[int] = None
    source_id: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    confidence_score: float = 0.0

    class Config:
        from_attributes = True
