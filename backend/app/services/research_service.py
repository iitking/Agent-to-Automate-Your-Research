import asyncio
import time
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional
import uuid
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.core.logging import logger
from app.database.connection import AsyncSessionLocal
from app.database.models import (
    ResearchTask,
    ResearchPlan,
    ResearchSource,
    ExtractedDocument,
    ResearchFinding,
    Claim,
    Citation,
    ResearchReport,
    AgentExecutionLog,
    User,
)
from app.graph.workflow import build_research_graph


class EventBroadcaster:
    """Pub/Sub broker for live SSE stream of agent actions."""
    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, research_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        if research_id not in self._subscribers:
            self._subscribers[research_id] = []
        self._subscribers[research_id].append(q)
        return q

    def unsubscribe(self, research_id: str, q: asyncio.Queue):
        if research_id in self._subscribers:
            if q in self._subscribers[research_id]:
                self._subscribers[research_id].remove(q)
            if not self._subscribers[research_id]:
                del self._subscribers[research_id]

    async def broadcast(self, research_id: str, event_data: Dict[str, Any]):
        if research_id in self._subscribers:
            for q in list(self._subscribers[research_id]):
                await q.put(event_data)


broadcaster = EventBroadcaster()


class ResearchService:
    def __init__(self):
        self.graph = build_research_graph()

    async def create_research_task(
        self,
        topic: str,
        research_depth: str = "comprehensive",
        max_sources: int = 20,
        include_academic_papers: bool = True,
        output_formats: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> ResearchTask:
        task_id = str(uuid.uuid4())
        formats = output_formats or ["markdown", "pdf", "docx"]

        async with AsyncSessionLocal() as session:
            # Ensure default user exists if needed
            if user_id:
                user_res = await session.execute(select(User).where(User.id == user_id))
                user = user_res.scalars().first()
                if not user:
                    user = User(id=user_id, email=f"{user_id}@researchagent.local")
                    session.add(user)
                    await session.commit()

            task = ResearchTask(
                id=task_id,
                user_id=user_id,
                topic=topic,
                status="queued",
                research_depth=research_depth,
                max_sources=max_sources,
                include_academic_papers=include_academic_papers,
                current_agent="coordinator",
                progress_percentage=0,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

        # Trigger execution in background
        asyncio.create_task(self._execute_workflow(task_id, topic, research_depth, max_sources, include_academic_papers, formats))

        return task

    async def _execute_workflow(
        self,
        task_id: str,
        topic: str,
        research_depth: str,
        max_sources: int,
        include_academic_papers: bool,
        output_formats: List[str],
    ):
        logger.info(f"Starting research workflow for task {task_id}")
        start_time = time.time()

        initial_state = {
            "research_id": task_id,
            "user_query": topic,
            "research_depth": research_depth,
            "include_academic": include_academic_papers,
            "max_sources": max_sources,
            "output_formats": output_formats,
            "iteration_count": 0,
            "max_iterations": settings.MAX_RESEARCH_ITERATIONS,
            "sources": [],
            "findings": [],
            "claims": [],
            "errors": [],
            "progress": 5,
            "status": "running",
        }

        async def emit(agent_name: str, status: str, progress: int, message: str):
            await broadcaster.broadcast(task_id, {
                "research_id": task_id,
                "agent": agent_name,
                "status": status,
                "progress": progress,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            async with AsyncSessionLocal() as session:
                log_entry = AgentExecutionLog(
                    id=str(uuid.uuid4()),
                    research_task_id=task_id,
                    agent_name=agent_name,
                    execution_status=status,
                    execution_time=round(time.time() - start_time, 2),
                    message=message,
                )
                session.add(log_entry)
                await session.execute(
                    update(ResearchTask)
                    .where(ResearchTask.id == task_id)
                    .values(current_agent=agent_name, progress_percentage=progress, status="running")
                )
                await session.commit()

        try:
            await emit("orchestrator", "started", 5, f"Initializing research workflow for: '{topic}'")

            # Stream through graph steps
            final_state = initial_state
            async for step_state in self.graph.astream(initial_state):
                for node_name, node_output in step_state.items():
                    current_agent = node_output.get("current_agent", node_name)
                    progress = node_output.get("progress", final_state.get("progress", 10))
                    status_text = node_output.get("status", "in_progress")
                    
                    # Update accumulator
                    final_state.update(node_output)

                    await emit(
                        current_agent,
                        "running",
                        progress,
                        f"Agent [{current_agent.upper()}] completed phase {node_name} ({status_text})."
                    )

            # Persist finalized graph state into Database
            await self._persist_research_results(task_id, final_state)

            await emit("coordinator", "completed", 100, "Autonomous research and report generation completed successfully.")

            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(ResearchTask)
                    .where(ResearchTask.id == task_id)
                    .values(
                        status="completed",
                        progress_percentage=100,
                        current_agent="done",
                        completed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()

            logger.info(f"Research task {task_id} successfully completed in {round(time.time() - start_time, 2)}s.")

        except Exception as e:
            logger.error(f"Error during research workflow for task {task_id}: {e}", exc_info=True)
            err_msg = str(e)
            await emit("orchestrator", "error", 0, f"Error: {err_msg}")

            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(ResearchTask)
                    .where(ResearchTask.id == task_id)
                    .values(
                        status="failed",
                        error_message=err_msg,
                        completed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()

    async def _persist_research_results(self, task_id: str, state: Dict[str, Any]):
        """Persists plan, sources, extracted documents, findings, claims, and report to SQL DB."""
        async with AsyncSessionLocal() as session:
            # 1. Plan
            plan_data = state.get("research_plan")
            if plan_data:
                plan = ResearchPlan(
                    id=str(uuid.uuid4()),
                    research_task_id=task_id,
                    plan_data=plan_data,
                )
                session.add(plan)

            # 2. Sources & Extracted documents
            sources = state.get("sources", [])
            source_model_map = {}
            for s in sources:
                src_id = s.get("id") or str(uuid.uuid4())
                src_obj = ResearchSource(
                    id=src_id,
                    research_task_id=task_id,
                    title=s.get("title", "Untitled Source"),
                    url=s.get("url", ""),
                    domain=s.get("domain"),
                    author=s.get("author"),
                    published_at=s.get("published_at"),
                    source_type=s.get("source_type", "web"),
                    provider=s.get("provider", "web"),
                    relevance_score=s.get("relevance_score", 0.0),
                    credibility_score=s.get("credibility_score", 0.0),
                    extraction_status=s.get("extraction_status", "pending"),
                    evaluation_notes=s.get("evaluation_notes"),
                    snippet=s.get("snippet"),
                    content_length=s.get("content_length", 0),
                )
                session.add(src_obj)
                source_model_map[src_id] = src_obj

                extracted_text = s.get("extracted_text")
                if extracted_text:
                    doc = ExtractedDocument(
                        id=str(uuid.uuid4()),
                        source_id=src_id,
                        content=extracted_text,
                        content_hash=s.get("content_hash"),
                    )
                    session.add(doc)

            # 3. Findings
            findings = state.get("findings", [])
            for f in findings:
                finding_obj = ResearchFinding(
                    id=f.get("id") or str(uuid.uuid4()),
                    research_task_id=task_id,
                    question=f.get("question", ""),
                    finding=f.get("finding", ""),
                    confidence=f.get("confidence", 0.9),
                    evidence_ids=f.get("source_ids", []),
                )
                session.add(finding_obj)

            # 4. Claims & Citations
            claims = state.get("claims", [])
            for c in claims:
                claim_id = c.get("id") or str(uuid.uuid4())
                claim_obj = Claim(
                    id=claim_id,
                    research_task_id=task_id,
                    claim_text=c.get("claim_text", ""),
                    verification_status=c.get("verification_status", "insufficient_evidence"),
                )
                session.add(claim_obj)

                src_id = c.get("source_id")
                if src_id and src_id in source_model_map:
                    citation_obj = Citation(
                        id=str(uuid.uuid4()),
                        claim_id=claim_id,
                        source_id=src_id,
                        supporting_passage=c.get("supporting_passage"),
                        page_number=c.get("page_number"),
                    )
                    session.add(citation_obj)

            # 5. Report
            final_report = state.get("final_report")
            if final_report:
                report_obj = ResearchReport(
                    id=str(uuid.uuid4()),
                    research_task_id=task_id,
                    markdown_content=final_report,
                    pdf_path=state.get("pdf_path"),
                    docx_path=state.get("docx_path"),
                    word_count=len(final_report.split()),
                    references_count=len(sources),
                )
                session.add(report_obj)

            await session.commit()
