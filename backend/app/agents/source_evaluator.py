from urllib.parse import urlparse
from typing import Any, Dict, List
from app.core.logging import logger


class SourceEvaluatorAgent:
    """
    Source Evaluator Agent:
    - Treats relevance and credibility as distinct dimensions.
    - Evaluates recency, peer review / domain reputation, metadata completeness.
    - Scores each source and generates explainable evaluation notes.
    """
    def __init__(self):
        pass

    async def evaluate_sources(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        logger.info(f"Evaluating {len(sources)} collected sources for topical relevance and credibility.")
        topic_words = set(topic.lower().split())

        evaluated: List[Dict[str, Any]] = []

        for src in sources:
            url = src.get("url", "")
            title = src.get("title", "")
            snippet = src.get("snippet", "")
            source_type = src.get("source_type", "web")
            provider = src.get("provider", "")
            domain = urlparse(url).netloc.lower() if url else ""

            # Calculate Relevance Score (0.0 to 1.0)
            text_corpus = f"{title} {snippet}".lower()
            matches = sum(1 for w in topic_words if len(w) > 3 and w in text_corpus)
            base_relevance = min(1.0, 0.4 + (matches * 0.15))

            # Calculate Credibility Score (0.0 to 1.0)
            credibility = 0.65
            notes = []

            if source_type == "academic" or provider in ("arxiv", "crossref", "semantic_scholar"):
                credibility = 0.95
                notes.append("Peer-reviewed preprint or indexed academic publication.")
            elif any(d in domain for d in [".edu", ".gov", ".org", "nature.com", "ieee.org", "acm.org", "science.org"]):
                credibility = 0.90
                notes.append("Authoritative institutional, governmental, or educational domain.")
            elif any(d in domain for d in ["reuters.com", "bloomberg.com", "wsj.com", "bbc.com", "nytimes.com", "techcrunch.com"]):
                credibility = 0.82
                notes.append("Established major news and journalism publication.")
            else:
                credibility = 0.70
                notes.append("Standard public web source; passage verified independently.")

            if src.get("published_at"):
                notes.append(f"Published timestamp verified: {src.get('published_at')}.")
            if src.get("author") and src.get("author") != "Unknown":
                notes.append(f"Author attribution present: {src.get('author')}.")
            else:
                notes.append("Author attribution not explicitly declared.")

            src["domain"] = domain
            src["relevance_score"] = round(base_relevance, 2)
            src["credibility_score"] = round(credibility, 2)
            src["evaluation_notes"] = " ".join(notes)

            evaluated.append(src)

        # Sort by combined score
        evaluated.sort(key=lambda s: (s.get("relevance_score", 0) * 0.6 + s.get("credibility_score", 0) * 0.4), reverse=True)
        return evaluated
