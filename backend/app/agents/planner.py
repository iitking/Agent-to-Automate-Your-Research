from typing import Any, Dict
from pydantic import BaseModel, Field
from app.core.logging import logger
from app.schemas.research import ResearchPlanSchema
from app.services.llm_service import get_llm_provider


class PlannerOutput(BaseModel):
    title: str = Field(description="Clear, refined academic/investigative title for the research")
    objectives: list[str] = Field(description="3 to 5 core objectives of this research")
    sub_questions: list[str] = Field(description="4 to 6 specific sub-questions that deconstruct the topic")
    search_queries: list[str] = Field(description="6 to 10 highly targeted, effective search queries for web & academic indexes")
    categories: list[str] = Field(description="Key domains or literature categories to examine")


class ResearchPlannerAgent:
    """
    Research Planner Agent:
    - Interprets the user's research question and constraints.
    - Defines objectives and scope.
    - Generates focused sub-questions.
    - Produces targeted search queries for real search and academic discovery.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    async def plan(
        self,
        topic: str,
        research_depth: str = "comprehensive",
        include_academic: bool = True,
        max_sources: int = 20,
    ) -> ResearchPlanSchema:
        logger.info(f"Research Planner generating plan for: '{topic}' (depth: {research_depth})")

        system_prompt = (
            "You are an expert Research Director and Methodologist. "
            "Your task is to analyze the research topic, establish clear research objectives, "
            "break it down into mutually exclusive, collectively exhaustive (MECE) sub-questions, "
            "and formulate high-precision search queries suitable for live web and academic search APIs."
        )

        user_prompt = (
            f"Research Topic: {topic}\n"
            f"Research Depth: {research_depth}\n"
            f"Include Academic Papers: {include_academic}\n"
            f"Max Target Sources: {max_sources}\n\n"
            f"Formulate a rigorous research plan with focused sub-questions and search queries."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result: PlannerOutput = await self.llm.generate(messages, schema=PlannerOutput, temperature=0.1)

        return ResearchPlanSchema(
            title=result.title,
            objectives=result.objectives,
            sub_questions=result.sub_questions,
            search_queries=result.search_queries,
            categories=result.categories,
        )
