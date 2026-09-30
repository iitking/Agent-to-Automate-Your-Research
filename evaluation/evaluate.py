import asyncio
import json
import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.tools.academic.arxiv_client import ArxivClient
from app.tools.academic.crossref_client import CrossrefClient
from app.tools.search.ddg_client import LiveWebSearchClient
from evaluation.metrics import calculate_source_relevance


async def run_evaluation():
    print("Running Research Evaluation Benchmark on Real Sources...")
    dataset_file = Path(__file__).resolve().parent / "datasets" / "sample_questions.json"
    with open(dataset_file, "r") as f:
        questions = json.load(f)

    arxiv = ArxivClient()
    crossref = CrossrefClient()
    ddg = LiveWebSearchClient()

    results = []
    for item in questions:
        topic = item["topic"]
        print(f"\n[Benchmarking] Topic: '{topic}'")

        try:
            papers = await arxiv.search(topic, max_results=3)
            articles = await crossref.search(topic, limit=3)
            web_results = await ddg.search(topic, max_results=3)

            total_sources = len(papers) + len(articles) + len(web_results)
            print(f"  -> Retrieved {len(papers)} arXiv papers, {len(articles)} Crossref papers, {len(web_results)} web sources.")

            results.append({
                "id": item["id"],
                "topic": topic,
                "domain": item["domain"],
                "real_sources_retrieved": total_sources,
                "status": "PASS" if total_sources > 0 else "FAIL",
            })
        except Exception as e:
            print(f"  -> Error: {e}")
            results.append({
                "id": item["id"],
                "topic": topic,
                "status": "ERROR",
                "error": str(e),
            })

    print("\n--- Benchmark Summary ---")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(run_evaluation())
