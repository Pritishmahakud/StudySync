"""
StudySync CLI / JSON Bridge.
Allows the Next.js frontend API routes to directly invoke the 6 Python GenAI agents
and the SQLite database with zero external server dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict

# Ensure CodeSync root is in sys.path
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tutorgpt.agent import TutorGPT
from tutorgpt.models import DifficultyLevel
from revisiongpt.agent import RevisionGPT
from quizgen.quizgen import generate_mcqs
from codementor.agent import CodeMentorAgent
from studyplanner.scheduler import PlanRequest, Subject, build_plan
from performance_analyst.analyst import PerformanceAnalyst


def handle_tutor_ask(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent = TutorGPT()
    query = payload.get("query", "Explain Two-Phase Locking")
    diff_str = payload.get("difficulty", "intermediate").lower()
    difficulty = {
        "beginner": DifficultyLevel.BEGINNER,
        "intermediate": DifficultyLevel.INTERMEDIATE,
        "advanced": DifficultyLevel.ADVANCED,
    }.get(diff_str, DifficultyLevel.INTERMEDIATE)

    use_rag = payload.get("use_rag", True)
    if use_rag and len(agent.rag.chunks) > 0:
        res = agent.answer_with_rag(query=query)
        return {
            "status": "success",
            "explanation": res.answer,
            "citations": [
                {
                    "source": c.source,
                    "chunk_id": c.chunk_id,
                    "relevance_score": round(c.relevance_score, 3),
                    "text": c.text,
                }
                for c in res.citations
            ],
            "rag_grounded": res.rag_grounded,
            "unsupported_warning": res.unsupported_warning,
        }
    else:
        exp = agent.explain_concept(concept=query, difficulty=difficulty)
        return {
            "status": "success",
            "explanation": exp.full_markdown or exp.core_definition,
            "core_definition": exp.core_definition,
            "analogy": exp.analogy,
            "step_by_step": exp.step_by_step,
            "practical_example": exp.practical_example,
            "socratic_check_question": exp.socratic_check_question,
            "rag_grounded": False,
        }


def handle_flashcards_due(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent = RevisionGPT()
    due_cards = agent.get_due_cards()
    return {
        "status": "success",
        "count": len(due_cards),
        "cards": [
            {
                "id": c.id,
                "front": c.front,
                "back": c.back,
                "hint": c.hint,
                "concept": c.concept,
                "reps": c.repetition,
                "interval_days": c.interval,
                "easiness": round(c.easiness_factor, 2),
                "next_review": c.next_review_date,
            }
            for c in due_cards[:10]
        ],
    }


def handle_flashcards_review(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent = RevisionGPT()
    card_id = payload.get("card_id", "")
    rating = int(payload.get("rating", 4))
    card = agent.review_card(card_id=card_id, rating=rating)
    if not card:
        return {"status": "error", "message": f"Card {card_id} not found"}
    return {
        "status": "success",
        "card": {
            "id": card.id,
            "reps": card.repetition,
            "interval_days": card.interval,
            "easiness": round(card.easiness_factor, 2),
            "next_review": card.next_review_date,
        },
    }


def handle_quiz_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "Database Two-Phase Locking")
    count = int(payload.get("count", 3))
    diff = payload.get("difficulty", "medium")
    mcqs = generate_mcqs(topic=topic, n=count, difficulty=diff)
    return {
        "status": "success",
        "topic": topic,
        "questions": [
            {
                "question": m.question,
                "options": m.options,
                "answer_index": m.answer_index,
                "answer": m.options[m.answer_index] if 0 <= m.answer_index < len(m.options) else "",
                "explanation": m.explanation,
                "concept": m.concept,
                "difficulty": m.difficulty,
            }
            for m in mcqs
        ],
    }


def handle_code_run(payload: Dict[str, Any]) -> Dict[str, Any]:
    from codementor.agent import run_code
    code = payload.get("code", "print('Hello from CodeLab!')")
    language = payload.get("language", "python").lower()
    res = run_code(code=code, language=language)
    return {
        "status": "success",
        "stdout": res.stdout,
        "stderr": res.stderr,
        "exit_code": res.exit_code,
        "timed_out": res.timed_out,
        "duration_s": round(res.duration_s, 3),
    }


def handle_planner_schedule(payload: Dict[str, Any]) -> Dict[str, Any]:
    hours_per_day = float(payload.get("hours_per_day", 3.0))
    subjects = [
        Subject(name="Database Management Systems", exam_date=date.today() + timedelta(days=14), target_grade="A", priority_weight=1.5),
        Subject(name="Operating Systems", exam_date=date.today() + timedelta(days=21), target_grade="A", priority_weight=1.2),
        Subject(name="Algorithms & Dynamic Programming", exam_date=date.today() + timedelta(days=28), target_grade="A", priority_weight=1.0),
    ]
    req = PlanRequest(
        student_id=str(payload.get("user_id", "asha@studysync.edu")),
        subjects=subjects,
        daily_available_hours=hours_per_day,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=28),
    )
    plan = build_plan(req)
    return {
        "status": "success",
        "plan": {
            "hours_by_subject": plan.hours_by_subject,
            "warnings": plan.warnings,
            "sessions": [
                {
                    "date": s.date.isoformat(),
                    "subject": s.subject,
                    "minutes": s.minutes,
                    "kind": s.kind,
                    "focus": s.focus,
                }
                for s in plan.sessions[:15]
            ],
        },
    }


def handle_analytics_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    analyst = PerformanceAnalyst()
    user_id = payload.get("user_id", "STU001")
    summary = analyst.analyse_student(student=user_id)
    return {
        "status": "success",
        "summary": summary,
    }


HANDLERS = {
    "tutor_ask": handle_tutor_ask,
    "flashcards_due": handle_flashcards_due,
    "flashcards_review": handle_flashcards_review,
    "quiz_generate": handle_quiz_generate,
    "code_run": handle_code_run,
    "planner_schedule": handle_planner_schedule,
    "analytics_summary": handle_analytics_summary,
}


def main():
    parser = argparse.ArgumentParser(description="StudySync Multi-Agent Python Bridge")
    parser.add_argument("action", choices=list(HANDLERS.keys()), help="Action to execute")
    parser.add_argument("--payload", type=str, default="{}", help="JSON payload string")
    args = parser.parse_args()

    try:
        if args.payload.strip():
            payload = json.loads(args.payload)
        else:
            payload = json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON payload: {e}"}))
        sys.exit(1)

    handler = HANDLERS.get(args.action)
    if not handler:
        print(json.dumps({"status": "error", "message": f"Unknown action: {action}"}))
        sys.exit(1)

    try:
        output = handler(payload)
        print(json.dumps(output, default=str))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
