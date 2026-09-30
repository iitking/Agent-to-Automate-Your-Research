import os
import pytest
from app.tools.export.markdown_generator import generate_markdown_export
from app.tools.export.pdf_generator import generate_pdf_export
from app.tools.export.docx_generator import generate_docx_export


def test_export_generators(tmp_path):
    test_id = "test-export-001"
    title = "Evaluating Multi-Agent Systems in Scientific Discovery"
    markdown = """# Evaluating Multi-Agent Systems in Scientific Discovery

## 1. Title
Evaluating Multi-Agent Systems in Scientific Discovery

## 2. Executive Summary
This empirical study evaluates autonomous AI architectures across research workflows.

## 3. Research Objectives
- Evaluate reasoning speed
- Measure citation accuracy

## 12. References
[1] Vaswani et al. (2017). *Attention Is All You Need*. [arXiv](https://arxiv.org/abs/1706.03762)
"""

    # Test Markdown
    md_file = generate_markdown_export(test_id, markdown)
    assert os.path.exists(md_file)
    assert os.path.getsize(md_file) > 50

    # Test PDF with ReportLab
    pdf_file = generate_pdf_export(test_id, title, markdown)
    assert os.path.exists(pdf_file)
    assert os.path.getsize(pdf_file) > 1000  # Valid non-empty binary PDF

    # Test DOCX with python-docx
    docx_file = generate_docx_export(test_id, title, markdown)
    assert os.path.exists(docx_file)
    assert os.path.getsize(docx_file) > 1000  # Valid non-empty Word doc
