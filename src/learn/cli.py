from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import cast

from learn.card_gen import from_text
from learn.pdf_ingest import extract
from learn.srs import SRSState, review
from learn.store import Store

QUALITY_MAX: int = 5


def cmd_ingest(args: argparse.Namespace) -> int:
    """Ingest a PDF/TXT, generate cards (LLM optional), and store them."""
    text = extract(args.file)
    cards = from_text(text, use_llm=args.use_llm)
    s = Store(args.db)
    n = s.add_cards(cards)
    print(f"Inserted {n} cards into {args.db}")
    return 0


def _iso_now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_quality() -> int:
    while True:
        q = input(f"Quality 0-{QUALITY_MAX}: ").strip()
        if q.isdigit():
            qi = int(q)
            if 0 <= qi <= QUALITY_MAX:
                return qi
        print(f"Please enter a number between 0 and {QUALITY_MAX}.")


def cmd_review(args: argparse.Namespace) -> int:
    """Simple terminal review loop using the SRS logic."""
    s = Store(args.db)
    due = s.get_due_cards(_iso_now_utc())
    if not due:
        print("🎉 No cards due. You're all caught up!")
        return 0

    print(f"{len(due)} card(s) due.\n")
    for card_id, question, answer in due:
        print(f"Q: {question}")
        input("Press Enter to reveal answer...")
        print(f"A: {answer}\n")

        # Last known state (interval, ease) -> SRSState | None
        last = s.get_last_state(card_id)
        state = SRSState(interval=last[0], ease=last[1]) if last else None

        quality = _read_quality()
        new_state, next_due = review(state, quality)

        # Persist review
        s.add_review(
            card_id=card_id,
            quality=quality,
            interval=new_state.interval,
            ease=new_state.ease,
            next_due_iso=next_due,
        )
        print(f"Next due in {new_state.interval} day(s) @ {next_due}\n")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="learn", description="Learn: CLI")
    p.add_argument("--db", default="learn.db", help="SQLite DB path (default: learn.db)")
    sp = p.add_subparsers(dest="cmd")

    # ingest
    ing = sp.add_parser("ingest", help="Ingest a PDF/TXT and generate cards")
    ing.add_argument("file", help="Path to PDF or TXT")
    ing.add_argument(
        "--use-llm",
        action="store_true",
        help="Generate cards with an LLM (falls back to heuristic on failure)",
    )
    ing.set_defaults(func=cmd_ingest)

    # review
    rev = sp.add_parser("review", help="Review due cards")
    rev.set_defaults(func=cmd_review)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(list(argv) if argv is not None else None)
    func: Callable[[argparse.Namespace], int] | None = cast(
        Callable[[argparse.Namespace], int] | None,
        getattr(args, "func", None),
    )
    if func is None:
        p.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
