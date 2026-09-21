from typing import Any, Dict, Literal
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.core.logging import logger
from app.graph.state import ResearchState
from app.agents.planner import ResearchPlannerAgent
from app.agents.search_agent import ResearchSearchAgent
from app.agents.extractor import InformationExtractionAgent
from app.agents.source_evaluator import SourceEvaluatorAgent
from app.agents.analyst import ResearchAnalystAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.report_writer import ReportWriterAgent
from app.tools.export.markdown_generator import generate_markdown_export
from app.tools.export.pdf_generator import generate_pdf_export
from app.tools.export.docx_generator import generate_docx_export


# Instantiate Agent Singletons
planner_agent = ResearchPlannerAgent()
search_agent = ResearchSearchAgent()
extractor_agent = InformationExtractionAgent()
evaluator_agent = SourceEvaluatorAgent()
analyst_agent = ResearchAnalystAgent()
fact_checker_agent = FactCheckerAgent()
report_writer_agent = ReportWriterAgent()


async def plan_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: PLAN")
    topic = state.get("user_query", "")
    depth = state.get("research_depth", "comprehensive")
    include_academic = state.get("include_academic", True)
    max_sources = state.get("max_sources", 20)

    plan = await planner_agent.plan(
        topic=topic,
        research_depth=depth,
        include_academic=include_academic,
        max_sources=max_sources,
    )

    return {
        "research_plan": plan.model_dump(),
        "sub_questions": plan.sub_questions,
        "search_queries": plan.search_queries,
        "current_agent": "planner",
        "progress": 15,
        "status": "planning_completed",
    }


async def search_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: SEARCH")
    queries = state.get("search_queries", [])
    include_academic = state.get("include_academic", True)
    max_sources = state.get("max_sources", 20)

    existing_sources = state.get("sources", [])
    remaining_budget = max(2, max_sources - len(existing_sources))

    new_sources = await search_agent.execute_search(
        queries=queries,
        include_academic=include_academic,
        max_sources=remaining_budget,
    )

    # Merge sources avoiding duplicate URLs
    seen_urls = {s.get("url") for s in existing_sources if s.get("url")}
    combined = list(existing_sources)
    for s in new_sources:
        if s.get("url") not in seen_urls:
            seen_urls.add(s.get("url"))
            combined.append(s)

    return {
        "sources": combined,
        "current_agent": "search_agent",
        "progress": 35,
        "status": "search_completed",
    }


async def extraction_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: EXTRACT")
    sources = state.get("sources", [])

    extracted = await extractor_agent.extract_sources(sources)

    return {
        "sources": extracted,
        "current_agent": "extractor",
        "progress": 50,
        "status": "extraction_completed",
    }


async def evaluation_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: EVALUATE")
    topic = state.get("user_query", "")
    sources = state.get("sources", [])

    evaluated = await evaluator_agent.evaluate_sources(topic, sources)

    return {
        "sources": evaluated,
        "evaluated_sources": evaluated,
        "current_agent": "source_evaluator",
        "progress": 60,
        "status": "evaluation_completed",
    }


async def analysis_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: ANALYZE")
    sub_questions = state.get("sub_questions", [])
    sources = state.get("sources", [])

    findings = await analyst_agent.analyze(sub_questions, sources)

    return {
        "findings": findings,
        "current_agent": "analyst",
        "progress": 75,
        "status": "analysis_completed",
    }


async def verification_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: VERIFY")
    findings = state.get("findings", [])
    sources = state.get("sources", [])
    iteration = state.get("iteration_count", 1)

    claims, sufficient = await fact_checker_agent.verify_claims(findings, sources)

    return {
        "claims": claims,
        "verified_claims": claims,
        "evidence_sufficient": sufficient,
        "iteration_count": iteration + 1,
        "current_agent": "fact_checker",
        "progress": 85,
        "status": "verification_completed",
    }


def should_continue_research(state: ResearchState) -> Literal["search", "write_report"]:
    """
    Conditional routing:
    If evidence is insufficient and retry budget remains, generate additional targeted queries.
    Otherwise proceed to write the final report.
    """
    sufficient = state.get("evidence_sufficient", True)
    iteration = state.get("iteration_count", 1)
    max_iter = state.get("max_iterations", settings.MAX_RESEARCH_ITERATIONS)

    if not sufficient and iteration < max_iter:
        logger.info(f"Evidence insufficient; triggering search refinement loop (iteration {iteration}/{max_iter})")
        return "search"
    
    return "write_report"


async def report_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: WRITE_REPORT")
    topic = state.get("user_query", "")
    plan = state.get("research_plan", {})
    sources = state.get("sources", [])
    findings = state.get("findings", [])
    claims = state.get("claims", [])

    report_markdown = await report_writer_agent.write_report(
        topic=topic,
        plan=plan,
        sources=sources,
        findings=findings,
        claims=claims,
    )

    return {
        "final_report": report_markdown,
        "current_agent": "report_writer",
        "progress": 92,
        "status": "report_written",
    }


async def export_node(state: ResearchState) -> Dict[str, Any]:
    logger.info("Executing Graph Node: EXPORT")
    research_id = state.get("research_id", "report")
    topic = state.get("user_query", "Autonomous Research Report")
    report_markdown = state.get("final_report", "")
    output_formats = state.get("output_formats", ["markdown", "pdf", "docx"])

    pdf_path = None
    docx_path = None
    markdown_path = None

    if "markdown" in output_formats or True:
        markdown_path = generate_markdown_export(research_id, report_markdown)

    if "pdf" in output_formats:
        try:
            pdf_path = generate_pdf_export(research_id, topic, report_markdown)
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")

    if "docx" in output_formats:
        try:
            docx_path = generate_docx_export(research_id, topic, report_markdown)
        except Exception as e:
            logger.error(f"Failed to generate DOCX: {e}")

    return {
        "markdown_path": markdown_path,
        "pdf_path": pdf_path,
        "docx_path": docx_path,
        "current_agent": "export_generator",
        "progress": 100,
        "status": "completed",
    }


def build_research_graph() -> StateGraph:
    """Builds and compiles the full LangGraph state machine workflow."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("plan", plan_node)
    workflow.add_node("search", search_node)
    workflow.add_node("extract", extraction_node)
    workflow.add_node("evaluate", evaluation_node)
    workflow.add_node("analyze", analysis_node)
    workflow.add_node("verify", verification_node)
    workflow.add_node("report", report_node)
    workflow.add_node("export", export_node)

    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "search")
    workflow.add_edge("search", "extract")
    workflow.add_edge("extract", "evaluate")
    workflow.add_edge("evaluate", "analyze")
    workflow.add_edge("analyze", "verify")

    workflow.add_conditional_edges(
        "verify",
        should_continue_research,
        {
            "search": "search",
            "write_report": "report",
        },
    )

    workflow.add_edge("report", "export")
    workflow.add_edge("export", END)

    return workflow.compile()
