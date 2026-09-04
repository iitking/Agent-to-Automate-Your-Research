from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class ResearchCreateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="The research question or topic")
    research_depth: ResearchDepth = Field(default=ResearchDepth.COMPREHENSIVE, description="Depth of research")
    max_sources: int = Field(default=20, ge=3, le=50, description="Max sources to retrieve")
    include_academic_papers: bool = Field(default=True, description="Query academic repositories like arXiv / Semantic Scholar")
    output_formats: List[str] = Field(default_factory=lambda: ["markdown", "pdf", "docx"], description="Desired export formats")
    user_id: Optional[str] = Field(default="user_default", description="Identifier of the user")


class ResearchPlanSchema(BaseModel):
    title: str = Field(description="Refined research title")
    objectives: List[str] = Field(default_factory=list, description="Primary research goals")
    sub_questions: List[str] = Field(default_factory=list, description="Focused sub-questions to investigate")
    search_queries: List[str] = Field(default_factory=list, description="Targeted search queries for web & academic")
    categories: List[str] = Field(default_factory=list, description="Recommended source categories")


class ResearchTaskResponse(BaseModel):
    id: str
    user_id: str
    topic: str
    status: str
    research_depth: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    sources_count: int = 0
    findings_count: int = 0
    claims_count: int = 0
    error_message: Optional[str] = None
    current_agent: Optional[str] = None
    progress_percentage: int = 0

    class Config:
        from_attributes = True


class ResearchStatusResponse(BaseModel):
    research_id: str
    status: str
    progress: int
    current_agent: Optional[str] = None
    message: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)
