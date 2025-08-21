from __future__ import annotations

MAX_ANSWER_LEN = 280
MAX_CARDS = 10


def split_paragraphs(text: str, min_len: int = 40) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [p for p in paras if len(p) >= min_len]


def from_text(text: str) -> list[tuple[str, str, str | None]]:
    """
    Heuristic placeholder: convert paragraphs into simple Q/A cards.
    Returns: list[(question, answer, source_ref)]
    """
    cards: list[tuple[str, str, str | None]] = []
    for i, para in enumerate(split_paragraphs(text), start=1):
        q = f"What is the main idea of paragraph {i}?"
        a = para[:MAX_ANSWER_LEN] + ("..." if len(para) > MAX_ANSWER_LEN else "")
        cards.append((q, a, f"para:{i}"))
        if len(cards) >= MAX_CARDS:
            break
    if not cards and text.strip():
        cards.append(("What is the main idea?", text[:MAX_ANSWER_LEN], None))
    return cards
