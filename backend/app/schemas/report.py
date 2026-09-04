from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportItem(BaseModel):
    id: str
    research_task_id: str
    markdown_content: str
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None
    word_count: int = 0
    references_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
