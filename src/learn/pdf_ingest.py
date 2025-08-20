from pathlib import Path
from pypdf import PdfReader

def extract(source: str | Path) -> str:
    """
    Reads a PDF or TXT file and returns cleaned text.
    """
    p = Path(source)
    if p.suffix.lower() == ".pdf":
        reader = PdfReader(str(p))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    else:
        # treat as plain text file
        text = p.read_text(encoding="utf-8")

    # simple cleanup heuristics
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)
