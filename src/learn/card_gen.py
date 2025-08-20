from typing import List, Tuple, Optional

def split_paragraphs(text: str, min_len: int = 40) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [p for p in paras if len(p) >= min_len]

def from_text(text: str) -> List[Tuple[str, str, Optional[str]]]:
    """
    Heuristic placeholder: convert paragraphs into simple Q/A cards.
    Returns: list[(question, answer, source_ref)]
    """
    cards: List[Tuple[str, str, Optional[str]]] = []
    for i, para in enumerate(split_paragraphs(text), start=1):
        q = f"What is the main idea of paragraph {i}?"
        a = para[:280] + ("..." if len(para) > 280 else "")
        cards.append((q, a, f"para:{i}"))
        if len(cards) >= 10:
            break
    if not cards and text.strip():
        # fallback: single card from whole text
        cards.append(("What is the main idea?", text[:280], None))
    return cards
