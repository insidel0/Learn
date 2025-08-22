from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Callable, Optional, Sequence, cast

from learn.card_gen import from_text
from learn.pdf_ingest import extract
from learn.srs import SRSState, review
from learn.store import Store

QUALITY_MAX: int = 5


def cmd_ingest(args: argparse.Namespace) -> int:
    text: str = extract(args.input)
    cards = from_text(text)
    inserted: int = Store(args.db).add_cards(cards)
    print(f"Inserted {inserted} cards into {args.db}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    s = Store(args.db)
    now_iso: str = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
    due = s.get_due_cards(now_iso)
    if not due:
        print("No cards due. 🎉")
        return 0

    for card_id, q, a in due:
        print("\nQ:", q)
        input("Press Enter to reveal answer...")
        print("A:", a)

        while True:
            try:
                qual = int(input("Quality 0-5: "))
                if 0 <= qual <= QUALITY_MAX:
                    break
            except ValueError:
                pass

        last = s.get_last_state(card_id)
        state = SRSState(interval=last[0], ease=last[1], reps=1) if last else SRSState()
        new_state, next_due = review(state, qual)
        s.add_review(card_id, qual, new_state.interval, new_state.ease, next_due)
        print(f"Next due in {new_state.interval} day(s) @ {next_due}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="learn")
    p.add_argument("--db", default="learn.db")
    sub = p.add_subparsers(required=True)

    ing = sub.add_parser("ingest", help="Create cards from a document (PDF/TXT)")
    ing.add_argument("input")
    ing.set_defaults(func=cmd_ingest)

    rev = sub.add_parser("review", help="Review due cards")
    rev.set_defaults(func=cmd_review)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    p = build_parser()
    args = p.parse_args(list(argv) if argv is not None else None)
    func: Optional[Callable[[argparse.Namespace], int]] = cast(
        Optional[Callable[[argparse.Namespace], int]],
        getattr(args, "func", None),
    )
    if func is None:
        p.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
