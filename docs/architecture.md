# Architecture Specification

## Overview
**ResearchAgent** is built around an autonomous multi-agent architecture powered by LangGraph, FastAPI, SQLAlchemy, and a React + Vite dashboard.

## Key Subsystems
1. **Agent Orchestration**: LangGraph coordinates stateful transitions between planning, searching, extracting, evaluating, synthesizing, verifying, writing, and exporting.
2. **Search & Discovery**: Integrates live Tavily, Brave Search, public web search, arXiv API, Crossref API, and Semantic Scholar.
3. **Extraction & Normalization**: Uses Trafilatura for article extraction and PyMuPDF for document text extraction from PDFs.
4. **Fact Checking**: Deconstructs findings into discrete claims and verifies entailment against extracted passages with statuses: `supported`, `partially_supported`, `contradicted`, `insufficient_evidence`.
5. **Persistence**: SQLAlchemy 2.0 with PostgreSQL or local SQLite engine.
6. **Report Generation**: Produces canonical Markdown, ReportLab PDF, and python-docx Word documents.
