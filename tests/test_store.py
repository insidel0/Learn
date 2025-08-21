from learn.store import Store


def test_store_roundtrip(tmp_path):
    db = tmp_path / "t.db"
    s = Store(db)
    s.add_cards([("Q", "A", None)])
    due = s.get_due_cards("2100-01-01T00:00:00+00:00")
    assert len(due) == 1
