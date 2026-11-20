"""
Universal Document Ingestion Parser for StudySync.
Extracts clean plain text from PDF, DOCX, PPTX, Markdown, and Text files.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF pages using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(f"--- [Page {i}] ---\n{text.strip()}")
        return "\n\n".join(pages_text)
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract paragraphs and tables from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        lines = []
        for p in doc.paragraphs:
            if p.text.strip():
                lines.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    lines.append(f"| {row_text} |")
        return "\n\n".join(lines)
    except Exception as e:
        # Fallback to pure-python zipfile/xml parsing
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            texts = [node.text for node in tree.iter() if node.text]
            return " ".join(texts)
        except Exception:
            raise ValueError(f"Could not extract text from DOCX: {e}")


def extract_text_from_pptx(file_bytes: bytes) -> str:
    """Extract slide text, titles, notes, and tables from PPTX using python-pptx."""
    try:
        import pptx
        prs = pptx.Presentation(io.BytesIO(file_bytes))
        slides_text = []
        for i, slide in enumerate(prs.slides, 1):
            slide_lines = [f"--- [Slide {i}] ---"]
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_lines.append(shape.text.strip())
                if shape.has_table:
                    for row in shape.table.rows:
                        row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                        if row_cells:
                            slide_lines.append(" | ".join(row_cells))
            slides_text.append("\n".join(slide_lines))
        return "\n\n".join(slides_text)
    except Exception as e:
        raise ValueError(f"Could not extract text from PPTX: {e}")


def extract_text_from_plain(file_bytes: bytes) -> str:
    """Decode plain text or markdown with fallback encodings."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return file_bytes.decode(enc)
        except Exception:
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def parse_uploaded_file(file_name: str, file_bytes: bytes) -> str:
    """
    Main entry point: detects file format by extension and extracts clean text.
    Supported extensions: .pdf, .docx, .doc, .pptx, .ppt, .txt, .md, .py, .csv, .json
    """
    ext = Path(file_name).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    elif ext in (".pptx", ".ppt"):
        return extract_text_from_pptx(file_bytes)
    else:
        return extract_text_from_plain(file_bytes)
