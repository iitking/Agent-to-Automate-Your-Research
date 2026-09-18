from typing import Any, Dict, List
from app.core.logging import logger
from app.services.llm_service import get_llm_provider
from app.tools.validation.citation_validator import validate_report_citations


class ReportWriterAgent:
    """
    Report Writer Agent:
    - Generates a canonical, publication-grade Markdown research report.
    - Strictly follows the 12 required sections.
    - Enforces citation grounding to real retrieved sources.
    - Incorporates claim verification statuses and evidence gaps.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def write_report(
        self,
        topic: str,
        plan: Dict[str, Any],
        sources: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        claims: List[Dict[str, Any]],
    ) -> str:
        logger.info(f"Report Writer composing canonical report for topic: '{topic}'")

        # Format bibliography of verified sources
        references_block = []
        for i, s in enumerate(sources, 1):
            title = s.get("title", "Untitled Source")
            url = s.get("url", "")
            author = s.get("author") or "N/A"
            pub = s.get("published_at") or "Undated"
            provider = s.get("provider", "web")
            references_block.append(f"[{i}] {author} ({pub}). *{title}*. [{provider.capitalize()}]({url})")

        references_text = "\n".join(references_block)

        # Verified claims summary
        claims_summary = []
        for c in claims:
            status = c.get("verification_status")
            text = c.get("claim_text")
            url = c.get("source_url")
            claims_summary.append(f"- **[{status.upper()}]** {text} (Reference: {url})")

        findings_text = "\n".join(f"- **{f.get('question')}**: {f.get('finding')}" for f in findings)

        system_prompt = (
            "You are an Elite Research Scientist and Lead Author. "
            "Write a thorough, comprehensive, authoritative, academic-grade research report in Markdown.\n\n"
            "MANDATORY REPORT STRUCTURE - YOU MUST INCLUDE ALL 12 NUMBERED SECTIONS EXACTLY:\n"
            "# <Report Title>\n\n"
            "## 1. Title\n"
            "## 2. Executive Summary\n"
            "## 3. Research Objectives\n"
            "## 4. Research Questions\n"
            "## 5. Methodology\n"
            "## 6. Detailed Findings\n"
            "## 7. Comparative Analysis\n"
            "## 8. Evidence and Supporting Sources\n"
            "## 9. Conflicting Information\n"
            "## 10. Limitations\n"
            "## 11. Conclusion\n"
            "## 12. References\n\n"
            "CITATION AND GROUNDING RULES:\n"
            "1. You MUST cite real sources using Markdown links from the provided list, e.g. [Title](URL) or [Author, Year](URL).\n"
            "2. Under section '12. References', output the exact reference bibliography provided to you.\n"
            "3. Under '9. Conflicting Information' and '10. Limitations', honestly state nuances, evidence gaps, and claims with partial or insufficient support.\n"
            "4. NEVER invent or hallucinate URLs or authors."
        )

        user_prompt = (
            f"TOPIC: {topic}\n\n"
            f"OBJECTIVES:\n" + "\n".join(f"- {o}" for o in plan.get("objectives", [])) + "\n\n"
            f"SUB-QUESTIONS:\n" + "\n".join(f"- {q}" for q in plan.get("sub_questions", [])) + "\n\n"
            f"FINDINGS FROM SOURCES:\n{findings_text}\n\n"
            f"VERIFIED CLAIMS:\n" + "\n".join(claims_summary) + "\n\n"
            f"AVAILABLE REFERENCES:\n{references_text}\n\n"
            f"Write the full 12-section research report now."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        markdown_report = await self.llm.generate(messages, temperature=0.15)

        # Validate references in the written report
        validation = validate_report_citations(markdown_report, sources)
        logger.info(f"Report citation validation: {validation.details}")

        # Ensure Section 12 References is present
        if "## 12. References" not in markdown_report:
            markdown_report += f"\n\n## 12. References\n\n{references_text}\n"

        return markdown_report
