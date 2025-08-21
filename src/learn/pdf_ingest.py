from pathlib import Path

from pypdf import PdfReader


def extract(source: str | Path) -> str:
    p = Path(source)
    if p.suffix.lower() == ".pdf":
        reader = PdfReader(str(p))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    else:
        text = p.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)
