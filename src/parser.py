"""Read and clean resume text from PDF files."""

from pathlib import Path
import re

import fitz


def clean_text(text: str) -> str:
    """Normalize whitespace in extracted PDF text."""
    return re.sub(r"\s+", " ", text).strip()


def read_resumes(resume_folder: str | Path) -> dict[str, str]:
    """Return cleaned text for each PDF in ``resume_folder``.

    Files are processed in name order to keep downstream rankings reproducible.
    The returned dictionary uses each file name (for example, ``john.pdf``) as
    its key. Non-PDF files are ignored.
    """
    folder = Path(resume_folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Resume folder does not exist: {folder}")

    resume_texts: dict[str, str] = {}
    for pdf_path in sorted(folder.glob("*.pdf"), key=lambda path: path.name.lower()):
        with fitz.open(pdf_path) as document:
            extracted_text = "".join(page.get_text() for page in document)
        resume_texts[pdf_path.name] = clean_text(extracted_text)

    return resume_texts
