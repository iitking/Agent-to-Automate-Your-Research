import uuid
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.core.logging import logger
from app.services.llm_service import get_llm_provider


class SingleFinding(BaseModel):
    question: str = Field(description="Sub-question investigated")
    finding: str = Field(description="Synthesized evidence-backed finding")
    source_ids: list[str] = Field(description="Source IDs that directly provide this evidence")
    confidence: float = Field(default=0.9, description="Confidence score based on cross-source agreement")
    disagreements_or_gaps: str = Field(default="", description="Any conflicting viewpoints or missing data points")


class AnalystOutput(BaseModel):
    findings: list[SingleFinding] = Field(description="List of verified research findings grouped by sub-questions")
    summary_of_evidence: str = Field(description="High-level synthesis of evidence coverage and gaps")


class ResearchAnalystAgent:
    """
    Research Analyst Agent:
    - Synthesizes findings across multiple extracted sources.
    - Ties every finding directly to source IDs.
    - Identifies consensus, debates, and evidence limitations.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def analyze(
        self,
        sub_questions: List[str],
        extracted_sources: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        logger.info(f"Research Analyst synthesizing evidence across {len(extracted_sources)} sources for {len(sub_questions)} questions.")

        # Build context from extracted passages
        source_passages = []
        for s in extracted_sources:
            sid = s.get("id", "")
            title = s.get("title", "")
            text = (s.get("extracted_text") or s.get("snippet") or "")[:2000]
            if text:
                source_passages.append(f"--- [Source ID: {sid}] Title: {title} ---\n{text}\n")

        evidence_corpus = "\n".join(source_passages[:10])

        system_prompt = (
            "You are a Senior Research Analyst. "
            "Analyze the provided retrieved source texts to answer the research sub-questions. "
            "CRITICAL RULES:\n"
            "1. Ground findings solely in the provided source texts.\n"
            "2. For every finding, list the exact [Source ID] values that contain that evidence.\n"
            "3. If sources disagree or evidence is scarce, state the disagreement or gap explicitly.\n"
            "4. Never invent facts or citations."
        )

        user_prompt = (
            f"SUB-QUESTIONS TO ANSWER:\n"
            + "\n".join(f"- {q}" for q in sub_questions)
            + f"\n\nRETRIEVED SOURCE PASSAGES:\n{evidence_corpus}\n\n"
            f"Synthesize the findings."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result: AnalystOutput = await self.llm.generate(messages, schema=AnalystOutput, temperature=0.1)

        findings_list = []
        for f in result.findings:
            findings_list.append({
                "id": str(uuid.uuid4()),
                "question": f.question,
                "finding": f.finding,
                "source_ids": f.source_ids,
                "confidence": f.confidence,
                "disagreements": f.disagreements_or_gaps,
            })

        logger.info(f"Research Analyst produced {len(findings_list)} evidence-backed findings.")
        return findings_list
