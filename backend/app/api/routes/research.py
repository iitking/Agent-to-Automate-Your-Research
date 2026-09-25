import asyncio
import json
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.connection import get_db
from app.database.models import (
    ResearchTask,
    ResearchSource,
    ResearchFinding,
    Claim,
    Citation,
    ResearchReport,
    AgentExecutionLog,
)
from app.schemas.research import (
    ResearchCreateRequest,
    ResearchTaskResponse,
    ResearchStatusResponse,
)
from app.schemas.source import SourceItem
from app.schemas.claim import FindingItem, ClaimItem
from app.schemas.report import ReportItem
from app.services.research_service import ResearchService, broadcaster

router = APIRouter(prefix="/api/research", tags=["Research"])
research_service = ResearchService()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_research(payload: ResearchCreateRequest):
    """Create and queue a new research task."""
    task = await research_service.create_research_task(
        topic=payload.topic,
        research_depth=payload.research_depth.value,
        max_sources=payload.max_sources,
        include_academic_papers=payload.include_academic_papers,
        output_formats=payload.output_formats,
        user_id=payload.user_id,
    )
    return {
        "research_id": task.id,
        "status": task.status,
        "topic": task.topic,
        "message": "Research task queued successfully.",
    }


@router.get("", response_model=List[ResearchTaskResponse])
async def list_research(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List research tasks."""
    stmt = (
        select(ResearchTask)
        .order_by(desc(ResearchTask.created_at))
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    tasks = res.scalars().all()

    response = []
    for t in tasks:
        # Count sources, findings, claims
        s_count = await db.scalar(select(func.count(ResearchSource.id)).where(ResearchSource.research_task_id == t.id)) or 0
        f_count = await db.scalar(select(func.count(ResearchFinding.id)).where(ResearchFinding.research_task_id == t.id)) or 0
        c_count = await db.scalar(select(func.count(Claim.id)).where(Claim.research_task_id == t.id)) or 0

        response.append(ResearchTaskResponse(
            id=t.id,
            user_id=t.user_id or "default",
            topic=t.topic,
            status=t.status,
            research_depth=t.research_depth,
            created_at=t.created_at,
            completed_at=t.completed_at,
            sources_count=s_count,
            findings_count=f_count,
            claims_count=c_count,
            error_message=t.error_message,
            current_agent=t.current_agent,
            progress_percentage=t.progress_percentage or 0,
        ))

    return response


@router.get("/{research_id}")
async def get_research_details(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get research task details and summary statistics."""
    task = await db.get(ResearchTask, research_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found.")

    s_count = await db.scalar(select(func.count(ResearchSource.id)).where(ResearchSource.research_task_id == task.id)) or 0
    f_count = await db.scalar(select(func.count(ResearchFinding.id)).where(ResearchFinding.research_task_id == task.id)) or 0
    c_count = await db.scalar(select(func.count(Claim.id)).where(Claim.research_task_id == task.id)) or 0

    return {
        "id": task.id,
        "topic": task.topic,
        "status": task.status,
        "research_depth": task.research_depth,
        "max_sources": task.max_sources,
        "include_academic_papers": task.include_academic_papers,
        "current_agent": task.current_agent,
        "progress_percentage": task.progress_percentage or 0,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
        "error_message": task.error_message,
        "sources_count": s_count,
        "findings_count": f_count,
        "claims_count": c_count,
    }


@router.get("/{research_id}/status", response_model=ResearchStatusResponse)
async def get_research_status(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get actual live status and agent logs."""
    task = await db.get(ResearchTask, research_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found.")

    logs_res = await db.execute(
        select(AgentExecutionLog)
        .where(AgentExecutionLog.research_task_id == research_id)
        .order_by(AgentExecutionLog.created_at.asc())
    )
    logs = logs_res.scalars().all()

    return ResearchStatusResponse(
        research_id=task.id,
        status=task.status,
        progress=task.progress_percentage or 0,
        current_agent=task.current_agent,
        message=task.error_message,
        logs=[{
            "agent": l.agent_name,
            "status": l.execution_status,
            "time": l.execution_time,
            "message": l.message,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        } for l in logs],
    )


@router.get("/{research_id}/events")
async def stream_research_events(research_id: str):
    """Server-Sent Events (SSE) streaming live agent actions to the frontend."""
    async def event_generator():
        q = broadcaster.subscribe(research_id)
        try:
            # Send initial ping
            yield f"data: {json.dumps({'event': 'connected', 'research_id': research_id})}\n\n"
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ("completed", "error") or data.get("progress") == 100:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.unsubscribe(research_id, q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{research_id}/sources", response_model=List[SourceItem])
async def get_research_sources(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List retrieved real sources."""
    res = await db.execute(
        select(ResearchSource)
        .where(ResearchSource.research_task_id == research_id)
        .order_by(ResearchSource.relevance_score.desc())
    )
    return res.scalars().all()


@router.get("/{research_id}/findings", response_model=List[FindingItem])
async def get_research_findings(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List synthesized findings."""
    res = await db.execute(
        select(ResearchFinding)
        .where(ResearchFinding.research_task_id == research_id)
    )
    findings = res.scalars().all()
    return [
        FindingItem(
            id=f.id,
            research_task_id=f.research_task_id,
            question=f.question,
            finding=f.finding,
            confidence=f.confidence or 0.9,
            source_ids=f.evidence_ids or [],
        )
        for f in findings
    ]


@router.get("/{research_id}/claims", response_model=List[ClaimItem])
async def get_research_claims(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List verified claims and citation passages."""
    res = await db.execute(
        select(Claim)
        .where(Claim.research_task_id == research_id)
    )
    claims = res.scalars().all()

    items = []
    for c in claims:
        # Check citation if exists
        cit_res = await db.execute(select(Citation).where(Citation.claim_id == c.id))
        cit = cit_res.scalars().first()
        src = None
        if cit and cit.source_id:
            src = await db.get(ResearchSource, cit.source_id)

        items.append(ClaimItem(
            id=c.id,
            research_task_id=c.research_task_id,
            claim_text=c.claim_text,
            verification_status=c.verification_status,
            supporting_passage=cit.supporting_passage if cit else None,
            page_number=cit.page_number if cit else None,
            source_id=cit.source_id if cit else None,
            source_title=src.title if src else None,
            source_url=src.url if src else None,
            confidence_score=0.9 if c.verification_status == "supported" else 0.5,
        ))

    return items


@router.get("/{research_id}/report", response_model=ReportItem)
async def get_research_report(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve final generated report."""
    res = await db.execute(
        select(ResearchReport).where(ResearchReport.research_task_id == research_id)
    )
    report = res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet for this research task.")
    return report


@router.get("/{research_id}/export")
async def export_report(
    research_id: str,
    format: str = Query("markdown", pattern="^(markdown|pdf|docx)$"),
    db: AsyncSession = Depends(get_db),
):
    """Download the generated report in markdown, pdf, or docx."""
    res = await db.execute(
        select(ResearchReport).where(ResearchReport.research_task_id == research_id)
    )
    report = res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not available.")

    task = await db.get(ResearchTask, research_id)
    clean_title = (task.topic[:40] if task else "Research_Report").replace(" ", "_")

    if format == "pdf":
        file_path = report.pdf_path
        media_type = "application/pdf"
        filename = f"{clean_title}.pdf"
    elif format == "docx":
        file_path = report.docx_path
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{clean_title}.docx"
    else:
        # Markdown
        file_path = os.path.join(settings.EXPORTS_DIR, f"{research_id}.md")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report.markdown_content)
        media_type = "text/markdown"
        filename = f"{clean_title}.md"

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"{format.upper()} export file not found.")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )


@router.delete("/{research_id}", status_code=status.HTTP_200_OK)
async def delete_research(
    research_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete research task and associated records."""
    task = await db.get(ResearchTask, research_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found.")

    await db.delete(task)
    await db.commit()
    return {"status": "success", "message": "Research task deleted successfully."}
