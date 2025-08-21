import argparse
from datetime import datetime

from learn.card_gen import from_text
from learn.pdf_ingest import extract
from learn.srs import SRSState, review
from learn.store import Store

QUALITY_MAX = 5


def cmd_ingest(args):
    text = extract(args.input)
    cards = from_text(text)
    inserted = Store(args.db).add_cards(cards)
    print(f"Inserted {inserted} cards into {args.db}")


def cmd_review(args):
    s = Store(args.db)
    now_iso = datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
    due = s.get_due_cards(now_iso)
    if not due:
        print("No cards due. 🎉")
        return
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


def main():
    p = argparse.ArgumentParser(prog="learn")
    p.add_argument("--db", default="learn.db")
    sub = p.add_subparsers(required=True)

    ing = sub.add_parser("ingest", help="Create cards from a document (PDF/TXT)")
    ing.add_argument("input")
    ing.set_defaults(func=cmd_ingest)

    rev = sub.add_parser("review", help="Review due cards")
    rev.set_defaults(func=cmd_review)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
