from learn.card_gen import from_text


def test_llm_flag_falls_back_cleanly():
    # With use_llm=True, the LLM stub raises, so we must fall back to the heuristic.
    cards = from_text("Hello world.\n\nThis is a paragraph.", use_llm=True)
    assert isinstance(cards, list)
    assert len(cards) >= 1
    q, a, src = cards[0]
    assert isinstance(q, str) and isinstance(a, str)
