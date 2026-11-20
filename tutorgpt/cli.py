"""
Command-Line Interface for TutorGPT (Member 1).
Usage: python -m tutorgpt.cli explain "Dynamic Programming" --level beginner
       python -m tutorgpt.cli rag "What are ACID properties?" --source notes.txt
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from tutorgpt import DifficultyLevel, TutorGPT


def main():
    parser = argparse.ArgumentParser(description="TutorGPT - AI Teaching Agent")
    subparsers = parser.add_subparsers(dest="command")

    # Explain command
    p_exp = subparsers.add_parser("explain", help="Explain an academic concept")
    p_exp.add_argument("concept", help="Concept to explain (e.g. 'CAP Theorem', 'Deadlocks')")
    p_exp.add_argument(
        "--level",
        choices=["beginner", "intermediate", "advanced"],
        default="intermediate",
        help="Difficulty level"
    )

    # RAG command
    p_rag = subparsers.add_parser("rag", help="Query with RAG over study materials")
    p_rag.add_argument("query", help="Question to ask")
    p_rag.add_argument("--file", help="File to ingest and query", default=None)
    p_rag.add_argument("--top_k", type=int, default=3, help="Number of retrieved chunks")

    args = parser.parse_args()

    tutor = TutorGPT()

    if args.command == "explain":
        level_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED,
        }
        res = tutor.explain_concept(args.concept, difficulty=level_map[args.level])
        print(f"\n================ TUTOR EXPLANATION ({args.level.upper()}) ================")
        print(res.full_markdown)

    elif args.command == "rag":
        if args.file:
            print(f"[*] Ingesting study material from: {args.file}...")
            count = tutor.ingest_file(args.file)
            print(f"[+] Indexed {count} semantic chunks.")

        res = tutor.answer_with_rag(args.query, top_k=args.top_k)
        print(f"\n================ RAG RESPONSE ================")
        print(res.answer)
        print("\n--- SOURCES CITED ---")
        for c in res.citations:
            print(f"- [{c.source_name} | Chunk #{c.chunk_id}] (Score: {c.score})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
