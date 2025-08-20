# tests/test_pdf_ingest.py
from pathlib import Path
from src.learn.pdf_ingest import extract

def test_extract_txt(tmp_path: Path):
    f = tmp_path / "demo.txt"
    f.write_text("Hello\n\nWorld", encoding="utf-8")
    out = extract(f)
    assert "Hello" in out and "World" in out

# tests/test_srs.py
from src.learn.srs import SRSState, review

def test_srs_progression():
    st, _ = review(None, 4)    # 1st success -> 1 day
    assert st.interval == 1
    st2, _ = review(st, 4)     # 2nd -> 6 days
    assert st2.interval == 6

# tests/test_store.py
from src.learn.store import Store

def test_store_roundtrip(tmp_path):
    db = tmp_path / "t.db"
    s = Store(db)
    s.add_cards([("Q","A",None)])
    due = s.get_due_cards("2100-01-01T00:00:00+00:00")
    assert len(due) == 1
