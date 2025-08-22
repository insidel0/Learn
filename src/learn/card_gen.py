from __future__ import annotations

import sys

# Existing heuristic limits
MAX_ANSWER_LEN = 280
MAX_CARDS = 10

Card = tuple[str, str, str | None]  # (question, answer, source_ref)


def split_paragraphs(text: str, min_len: int = 40) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [p for p in paras if len(p) >= min_len]


# --- Heuristic baseline (unchanged behavior) ---------------------------------


def heuristic_from_text(text: str) -> list[Card]:
    """
    Heuristic placeholder: convert paragraphs into simple Q/A cards.
    Returns: list[(question, answer, source_ref)]
    """
    cards: list[Card] = []
    for i, para in enumerate(split_paragraphs(text), start=1):
        q = f"What is the main idea of paragraph {i}?"
        a = para[:MAX_ANSWER_LEN] + ("..." if len(para) > MAX_ANSWER_LEN else "")
        cards.append((q, a, f"para:{i}"))
        if len(cards) >= MAX_CARDS:
            break
    if not cards and text.strip():
        cards.append(("What is the main idea?", text[:MAX_ANSWER_LEN], None))
    return cards


# --- LLM scaffold (safe fallback) --------------------------------------------


def card_gen_llm(_text: str) -> list[Card]:
    """
    Placeholder for an upcoming LLM implementation.
    Intentionally raises to exercise the fallback path until wired.
    """
    raise RuntimeError("LLM generation not yet implemented")


def from_text(text: str, use_llm: bool = False) -> list[Card]:
    """
    Unified entrypoint:
    - If use_llm=True, try LLM first, then fallback to heuristic on any error.
    - Otherwise, use the existing heuristic.
    """
    if use_llm:
        try:
            return card_gen_llm(text)
        except Exception as e:  # noqa: BLE001 - we want a broad, safe fallback
            print(f"[card-gen] LLM failed ({e}); falling back to heuristic.", file=sys.stderr)
    return heuristic_from_text(text)
