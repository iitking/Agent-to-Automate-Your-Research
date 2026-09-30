# End-to-End Workflow

```
[User Request] 
      │
      ▼
1. Research Planner Agent (Sub-questions & Search Queries)
      │
      ▼
2. Research Search Agent (Web + Academic query execution)
      │
      ▼
3. Content Extraction Agent (Trafilatura & PyMuPDF)
      │
      ▼
4. Source Evaluator Agent (Topical relevance & Credibility scoring)
      │
      ▼
5. Research Analyst Agent (Cross-source synthesis by sub-question)
      │
      ▼
6. Fact Checker Agent (Claim decomposition & passage verification)
      │
      ├─► [Evidence Insufficient & Budget Remains] ──► Refine & Loop to Search
      │
      ▼ [Evidence Sufficient or Limit Reached]
7. Report Writer Agent (12 Mandatory Sections & References)
      │
      ▼
8. Export Generator (Markdown, ReportLab PDF, python-docx DOCX)
```
