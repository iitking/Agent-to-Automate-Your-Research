import os
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


def generate_markdown_export(research_id: str, markdown_content: str) -> str:
    """
    Saves canonical markdown report to the exports directory.
    Returns the file path.
    """
    os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
    file_path = os.path.join(settings.EXPORTS_DIR, f"{research_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info(f"Markdown report generated at {file_path}")
    return file_path
