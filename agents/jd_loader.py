# agents/jd_loader.py

import os
import fitz  # PyMuPDF for PDF processing

def load_job_description(path: str) -> str:
    """
    Load a job description from PDF or Markdown/TXT into one big string.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n\n"
        doc.close()
        return text
    elif ext in (".md", ".markdown", ".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported JD file type: {ext}")
