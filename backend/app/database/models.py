from datetime import datetime, timezone
import uuid
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    research_tasks = relationship("ResearchTask", back_populates="user", cascade="all, delete-orphan")


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    topic = Column(Text, nullable=False)
    status = Column(String(50), default="queued", index=True)  # queued, planning, searching, extracting, evaluating, analyzing, verifying, writing, completed, failed
    research_depth = Column(String(50), default="comprehensive")
    max_sources = Column(Integer, default=20)
    include_academic_papers = Column(Boolean, default=True)
    current_agent = Column(String(100), nullable=True)
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="research_tasks")
    plan = relationship("ResearchPlan", back_populates="task", uselist=False, cascade="all, delete-orphan")
    sources = relationship("ResearchSource", back_populates="task", cascade="all, delete-orphan")
    findings = relationship("ResearchFinding", back_populates="task", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="task", cascade="all, delete-orphan")
    report = relationship("ResearchReport", back_populates="task", uselist=False, cascade="all, delete-orphan")
    logs = relationship("AgentExecutionLog", back_populates="task", cascade="all, delete-orphan")


class ResearchPlan(Base):
    __tablename__ = "research_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False)
    plan_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="plan")


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(String(100), nullable=True)
    source_type = Column(String(50), default="web")  # web, academic, pdf
    provider = Column(String(50), default="tavily")  # tavily, brave, arxiv, semantic_scholar, crossref
    relevance_score = Column(Float, default=0.0)
    credibility_score = Column(Float, default=0.0)
    extraction_status = Column(String(50), default="pending")  # pending, success, failed, skipped
    evaluation_notes = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    content_length = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="sources")
    document = relationship("ExtractedDocument", back_populates="source", uselist=False, cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="source", cascade="all, delete-orphan")


class ExtractedDocument(Base):
    __tablename__ = "extracted_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("research_sources.id", ondelete="CASCADE"), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)
    extracted_at = Column(DateTime(timezone=True), default=utc_now)

    source = relationship("ResearchSource", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("extracted_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # JSON array of floats for cross-engine compatibility

    document = relationship("ExtractedDocument", back_populates="chunks")


class ResearchFinding(Base):
    __tablename__ = "research_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    finding = Column(Text, nullable=False)
    confidence = Column(Float, default=0.9)
    evidence_ids = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="findings")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    verification_status = Column(String(50), default="insufficient_evidence")  # supported, partially_supported, contradicted, insufficient_evidence
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="claims")
    citations = relationship("Citation", back_populates="claim", cascade="all, delete-orphan")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String(36), ForeignKey("research_sources.id", ondelete="CASCADE"), nullable=False)
    supporting_passage = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    claim = relationship("Claim", back_populates="citations")
    source = relationship("ResearchSource", back_populates="citations")


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, unique=True)
    markdown_content = Column(Text, nullable=False)
    pdf_path = Column(Text, nullable=True)
    docx_path = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    references_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="report")


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    research_task_id = Column(String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    execution_status = Column(String(50), nullable=False)  # started, running, completed, error
    execution_time = Column(Float, default=0.0)  # seconds
    token_usage = Column(JSON, default=dict)
    message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    task = relationship("ResearchTask", back_populates="logs")
