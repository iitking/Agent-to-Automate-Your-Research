# Evaluation Benchmark

This directory contains evaluation benchmarks for assessing research quality, citation accuracy, and real source retrieval.

## Metrics
- **Source Relevance**: Topical alignment of retrieved academic and web documents.
- **Citation Grounding**: Proportion of report statements with verifiable citations mapped directly to retrieved source IDs.
- **Evidence Coverage**: Completeness of sub-questions addressed with empirical passages.
- **Claim Verification Rate**: Percentage of extracted claims with defensible truth statuses.

## Running Evaluation
```bash
python evaluation/evaluate.py
```
