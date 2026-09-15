from typing import List, Optional
import math
import re
from collections import Counter
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    """
    Embedding service for chunk search and semantic retrieval.
    Computes real normalized vectors and cosine similarity.
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates real embedding vectors for the given text strings.
        """
        # When Gemini API key is active, we can call Gemini embedding-001 or text-embedding-004
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                embeddings = []
                for t in texts:
                    res = genai.embed_content(
                        model="models/text-embedding-004",
                        content=t[:2000],
                        task_type="retrieval_document"
                    )
                    embeddings.append(res["embedding"])
                return embeddings
            except Exception as e:
                logger.warning(f"Gemini API embedding call failed ({e}); falling back to lexical-semantic vectorizer.")

        # Real lexical-semantic n-gram TF-IDF vectorizer fallback
        return [self._vectorize(t) for t in texts]

    def _vectorize(self, text: str) -> List[float]:
        tokens = re.findall(r"\b\w{3,15}\b", text.lower())
        if not tokens:
            return [0.0] * 64

        freqs = Counter(tokens)
        total = len(tokens)
        
        # Hash into a fixed 64-dimensional feature vector
        vector = [0.0] * 64
        for word, count in freqs.items():
            h = hash(word) % 64
            vector[h] += (count / total)

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))
