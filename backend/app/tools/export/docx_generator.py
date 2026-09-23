import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.core.config import settings
from app.core.logging import logger


def generate_docx_export(research_id: str, title: str, markdown_content: str) -> str:
    """
    Generates a structured DOCX Word document from research markdown.
    Validates file creation and returns the generated absolute path.
    """
    os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
    docx_path = os.path.join(settings.EXPORTS_DIR, f"{research_id}.docx")

    doc = Document()

    # Document Title
    clean_title = title.replace("\n", " ").strip()
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(clean_title)
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    title_p.paragraph_format.space_after = Pt(8)

    # Subtitle
    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Autonomous Multi-Agent AI Research Report · Evidence-Verified")
    sub_run.font.size = Pt(10)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    sub_p.paragraph_format.space_after = Pt(18)

    lines = markdown_content.split("\n")
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            p = doc.add_paragraph(stripped)
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.space_after = Pt(2)
            continue

        if not stripped:
            continue

        if stripped.startswith("# ") and stripped[2:].strip().lower() == clean_title.lower():
            continue

        if stripped.startswith("# "):
            h = doc.add_heading(stripped[2:], level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)
        elif stripped.startswith("## "):
            h = doc.add_heading(stripped[3:], level=2)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
        elif stripped.startswith("### "):
            h = doc.add_heading(stripped[4:], level=3)
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("> "):
            quote_p = doc.add_paragraph()
            quote_p.paragraph_format.left_indent = Inches(0.3)
            quote_p.paragraph_format.space_after = Pt(6)
            run = quote_p.add_run(stripped[2:].strip())
            run.font.italic = True
            run.font.color.rgb = RGBColor(71, 85, 105)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bp = doc.add_paragraph(stripped[2:].strip(), style='List Bullet')
            bp.paragraph_format.space_after = Pt(3)
        elif re.match(r"^\d+\.\s+", stripped):
            num_content = re.sub(r"^\d+\.\s+", "", stripped)
            np = doc.add_paragraph(num_content, style='List Number')
            np.paragraph_format.space_after = Pt(3)
        else:
            p = doc.add_paragraph(stripped)
            p.paragraph_format.space_after = Pt(6)

    doc.save(docx_path)

    if not os.path.exists(docx_path) or os.path.getsize(docx_path) == 0:
        raise RuntimeError("DOCX generation failed or output file is empty.")

    logger.info(f"DOCX report generated successfully at {docx_path}")
    return docx_path
