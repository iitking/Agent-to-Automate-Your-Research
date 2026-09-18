import uuid
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.core.logging import logger
from app.services.llm_service import get_llm_provider


class VerifiedClaim(BaseModel):
    claim_text: str = Field(description="Atomized, checkable proposition")
    verification_status: str = Field(
        description="One of: 'supported', 'partially_supported', 'contradicted', 'insufficient_evidence'"
    )
    supporting_passage: str = Field(description="Exact snippet or sentence from source that grounds the status")
    source_id: str = Field(description="Source ID matching the source record")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)


class FactCheckerOutput(BaseModel):
    verified_claims: list[VerifiedClaim] = Field(description="List of verified claims with entailment statuses")
    evidence_sufficient: bool = Field(description="True if enough verified evidence exists to write the comprehensive report")


class FactCheckerAgent:
    """
    Fact Checker Agent:
    - Atomizes synthesized findings into verifiable factual claims.
    - Matches claims against extracted passages.
    - Labels status as supported, partially_supported, contradicted, or insufficient_evidence.
    - Preserves supporting passages.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def verify_claims(
        self,
        findings: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], bool]:
        logger.info(f"Fact Checker verifying claims against {len(sources)} source documents.")

        source_map = {s.get("id"): s for s in sources if s.get("id")}
        
        # Build passage context
        source_texts = []
        for sid, s in list(source_map.items())[:10]:
            title = s.get("title", "")
            passage = (s.get("extracted_text") or s.get("snippet") or "")[:1500]
            source_texts.append(f"Source ID: {sid} | Title: {title}\nPassage: {passage}\n")

        findings_text = "\n".join(
            f"- Finding: {f.get('finding')} (Associated Sources: {f.get('source_ids')})"
            for f in findings
        )

        system_prompt = (
            "You are a rigorous Fact-Checking Agent. "
            "Your job is to decompose findings into individual claims and verify whether each claim "
            "is directly supported by the retrieved passages.\n"
            "Statuses MUST be one of:\n"
            "- 'supported' (entailed by the passage)\n"
            "- 'partially_supported' (some parts supported, nuance missing)\n"
            "- 'contradicted' (directly conflicts with the passage)\n"
            "- 'insufficient_evidence' (cannot be found in provided passages)\n\n"
            "Preserve the exact supporting passage and valid Source ID for each claim."
        )

        user_prompt = (
            f"FINDINGS TO VERIFY:\n{findings_text}\n\n"
            f"RETRIEVED PASSAGES:\n" + "\n".join(source_texts) + "\n\n"
            f"Verify every claim against the evidence."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result: FactCheckerOutput = await self.llm.generate(messages, schema=FactCheckerOutput, temperature=0.1)

        claims_list = []
        for vc in result.verified_claims:
            matched_src = source_map.get(vc.source_id, {})
            claims_list.append({
                "id": str(uuid.uuid4()),
                "claim_text": vc.claim_text,
                "verification_status": vc.verification_status,
                "supporting_passage": vc.supporting_passage,
                "source_id": vc.source_id,
                "source_title": matched_src.get("title", "Unknown Source"),
                "source_url": matched_src.get("url", ""),
                "confidence_score": vc.confidence_score,
            })

        logger.info(f"Fact Checker verified {len(claims_list)} claims (Evidence sufficient: {result.evidence_sufficient}).")
        return claims_list, result.evidence_sufficient
