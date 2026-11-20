"""
StudySync - Quick Terminal Demonstration of the 6-Agent Collaborative Cycle.
"""

import sys
from pathlib import Path

root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from shared.orchestrator import StudySyncOrchestrator


def main():
    print("=" * 70)
    print("🎓 StudySync: Six-Agent Collaborative Learning Ecosystem")
    print("=" * 70)

    orch = StudySyncOrchestrator()
    student_id = "Asha"
    print(f"\n[1] Initiating multi-agent cycle for student: '{student_id}'...")
    report = orch.run_collaborative_learning_cycle(student_id)

    print("\n--- STEP 1: Member 5 (PerformanceAnalyst AI) ---")
    print(f"Target Weak Area Diagnosed: {report['target_weak_concept']}")
    for r in report["analyst_report"]["recommendations"][:2]:
        print(f"  {r}")

    print("\n--- STEP 2: Member 4 (StudyPlanner AI) ---")
    plan = report["adapted_study_plan"]
    print(f"Plan Rebalanced: {len(plan['sessions'])} sessions allocated.")
    first_sess = plan["sessions"][0]
    print(f"  Next session on {first_sess['date']}: {first_sess['subject']} ({first_sess['minutes']} mins, focus: {first_sess['focus']})")

    print("\n--- STEP 3: Member 1 (TutorGPT) ---")
    lesson = report["tutorgpt_lesson"]
    print(f"Remedial Lesson Concept: {lesson['concept']} ({lesson['difficulty']})")
    print(f"  Definition: {lesson['core_definition'][:140]}...")

    print("\n--- STEP 4: Member 6 (RevisionGPT) ---")
    cards = report["revisiongpt_cards"]
    print(f"Active Recall Flashcards: {len(cards)} cards generated & scheduled with SM-2.")
    print(f"  Card 1 Front: {cards[0]['front']}")
    print(f"  Card 1 Back:  {cards[0]['back']}")

    print("\n--- STEP 5: Member 2 (QuizGen AI) ---")
    test = report["quizgen_test"]
    print(f"Post-Remediation Verification Test: {len(test['mcqs'])} MCQs, {len(test['descriptive'])} Descriptive.")
    print(f"  Sample MCQ: {test['mcqs'][0]['question']}")

    print("\n--- STEP 6: Member 3 (CodeMentor AI) ---")
    ex = report["codementor_exercise"]
    print(f"Coding Practice Problem: {ex.get('title')}")
    print(f"  Statement: {ex.get('statement')[:120]}...")

    print("\n" + "=" * 70)
    print("✅ All 6 Generative AI systems successfully collaborated!")
    print("=" * 70)


if __name__ == "__main__":
    main()
