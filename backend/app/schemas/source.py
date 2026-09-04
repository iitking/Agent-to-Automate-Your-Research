from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    id: str
    research_task_id: str
    title: str
    url: str
    domain: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    source_type: str = "web"  # web, academic, pdf
    provider: str = "tavily"  # tavily, brave, arxiv, semantic_scholar, crossref
    relevance_score: float = 0.0
    credibility_score: float = 0.0
    extraction_status: str = "pending"  # pending, success, failed, skipped
    evaluation_notes: Optional[str] = None
    snippet: Optional[str] = None
    content_length: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
