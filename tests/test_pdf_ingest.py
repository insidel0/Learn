from pathlib import Path

from learn.pdf_ingest import extract


def test_extract_txt(tmp_path: Path):
    f = tmp_path / "demo.txt"
    f.write_text("Hello\n\nWorld", encoding="utf-8")
    out = extract(f)
    assert "Hello" in out and "World" in out
