"""
Command-Line Interface for RevisionGPT (Member 6).
Usage: python -m revisiongpt.cli flashcards "ACID Properties" --count 4
       python -m revisiongpt.cli review
       python -m revisiongpt.cli notes "Deadlocks"
       python -m revisiongpt.cli summary "Dynamic Programming"
"""

import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from revisiongpt import RevisionGPT


def main():
    parser = argparse.ArgumentParser(description="RevisionGPT - Revision Agent")
    subparsers = parser.add_subparsers(dest="command")

    # Flashcards
    p_fc = subparsers.add_parser("flashcards", help="Generate flashcards")
    p_fc.add_argument("topic", help="Topic for flashcards")
    p_fc.add_argument("--count", type=int, default=3, help="Number of cards")
    p_fc.add_argument("--difficulty", default="medium", choices=["easy", "medium", "hard"])

    # Review session
    p_rev = subparsers.add_parser("review", help="Start interactive SM-2 spaced repetition review")

    # Notes
    p_not = subparsers.add_parser("notes", help="Generate concise revision notes")
    p_not.add_argument("topic", help="Topic for cheat sheet")

    # Summary
    p_sum = subparsers.add_parser("summary", help="Generate hierarchical topic summary")
    p_sum.add_argument("topic", help="Topic for summary")

    # Stats
    subparsers.add_parser("stats", help="View spaced repetition deck statistics")

    args = parser.parse_args()
    rev = RevisionGPT()

    if args.command == "flashcards":
        print(f"[*] Generating flashcards for '{args.topic}'...")
        cards = rev.generate_flashcards(args.topic, count=args.count, difficulty=args.difficulty)
        print(f"[+] Generated {len(cards)} flashcards:\n")
        for i, c in enumerate(cards, 1):
            print(f"--- Card {i} [{c.difficulty.upper()}] ---")
            print(f"Q: {c.front}")
            print(f"A: {c.back}")
            if c.hint:
                print(f"Hint: {c.hint}")
            print()

    elif args.command == "review":
        due = rev.get_due_cards()
        if not due:
            print("🎉 No cards due for review today! Excellent job staying on track.")
            return

        print(f"[*] {len(due)} cards due for SM-2 review today.\n")
        for c in due:
            print("=" * 60)
            print(f"FRONT: {c.front}")
            if c.hint:
                input("Press Enter to see hint...")
                print(f"HINT: {c.hint}")
            input("Press Enter to flip card...")
            print(f"BACK: {c.back}")
            print("\nRate your recall (0 to 5):")
            print("  5: Perfect  4: Correct with hesitation  3: Correct with difficulty")
            print("  2: Wrong (easy recall)  1: Wrong (remembered)  0: Blackout")
            try:
                rating = int(input("Rating [0-5]: ").strip())
            except Exception:
                rating = 3
            updated = rev.review_card(c.id, rating)
            print(f"Next review scheduled in: {updated.interval} day(s) (EF: {updated.easiness_factor:.2f})\n")

    elif args.command == "notes":
        notes = rev.generate_revision_notes(args.topic)
        print("\n================ REVISION CHEAT SHEET ================")
        print(notes.full_markdown)

    elif args.command == "summary":
        summary = rev.generate_topic_summary(args.topic)
        print("\n================ TOPIC SUMMARY ================")
        print(summary.full_markdown)

    elif args.command == "stats":
        stats = rev.get_deck_stats()
        print("\n================ SPACED REPETITION STATS ================")
        for k, v in stats.items():
            print(f"- {k.replace('_', ' ').title()}: {v}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
