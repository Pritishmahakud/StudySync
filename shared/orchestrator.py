"""
StudySync Ecosystem Master Orchestrator.
Coordinates the six independently developed Generative AI agents into an end-to-end
personalized learning pipeline.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from codementor import CodeMentorAgent
from performance_analyst import PerformanceAnalyst
from quizgen import generate_test
from revisiongpt import RevisionGPT
from shared.event_bus import get_event_bus
from studyplanner import AnalyticsFeedback, PlanRequest, Subject, build_plan, replan
from tutorgpt import DifficultyLevel, TutorGPT


class StudySyncOrchestrator:
    """
    Central ecosystem coordinator tying:
    - Member 1: TutorGPT (AI Teaching Agent)
    - Member 2: QuizGen AI (Assessment Agent)
    - Member 3: CodeMentor AI (Programming Agent)
    - Member 4: StudyPlanner AI (Planning Agent)
    - Member 5: PerformanceAnalyst AI (Analytics Agent)
    - Member 6: RevisionGPT (Revision Agent)
    """

    def __init__(self):
        self.tutor = TutorGPT()
        self.quizgen = None  # functions accessed directly from module
        self.codementor = CodeMentorAgent()
        self.analyst = PerformanceAnalyst()
        self.revision = RevisionGPT()
        self.event_bus = get_event_bus()

    def run_collaborative_learning_cycle(
        self,
        student_id: str = "Asha"
    ) -> Dict[str, Any]:
        """
        Executes a complete 6-agent collaborative workflow:
        1. PerformanceAnalyst detects weak areas and progress trends.
        2. StudyPlanner adapts the timetable, prioritizing weak subjects and upcoming deadlines.
        3. TutorGPT generates targeted remedial lessons for the weakest concept.
        4. RevisionGPT automatically generates focused flashcards and schedules SM-2 spaced repetition.
        5. QuizGen generates a calibrated assessment test to verify mastery.
        6. CodeMentor is primed with coding practice for related programming topics.
        """
        # Step 1: Member 5 (PerformanceAnalyst AI)
        analysis = self.analyst.analyse_student(student_id)
        weak_concepts = analysis.get("weak_concepts_list", ["DBMS.Normalization"])
        if not weak_concepts:
            weak_concepts = ["DBMS.Normalization"]
        primary_weak = weak_concepts[0]
        subject_name = primary_weak.split(".")[0] if "." in primary_weak else primary_weak
        concept_name = primary_weak.split(".")[1] if "." in primary_weak else primary_weak

        # Step 2: Member 4 (StudyPlanner AI)
        today = date.today()
        base_request = PlanRequest(
            student_id=student_id,
            start_date=today,
            subjects=[
                Subject(name="DBMS", exam_date=today + timedelta(days=10), difficulty=4, est_hours=18.0),
                Subject(name="Operating Systems", exam_date=today + timedelta(days=14), difficulty=3, est_hours=14.0),
                Subject(name="Maths", exam_date=today + timedelta(days=20), difficulty=5, est_hours=24.0),
            ]
        )
        feedback = AnalyticsFeedback(
            student_id=student_id,
            subject_scores=analysis.get("subject_score_map", {subject_name: 40.0}),
            weak_concepts={subject_name: [primary_weak]}
        )
        adapted_plan = replan(base_request, fb=feedback)

        # Step 3: Member 1 (TutorGPT)
        tutor_lesson = self.tutor.explain_concept(
            concept=concept_name,
            difficulty=DifficultyLevel.INTERMEDIATE,
            additional_context=f"Student scored low in {subject_name} ({concept_name}). Focus on core mechanics and step-by-step intuition.",
            student_id=student_id
        )

        # Step 4: Member 6 (RevisionGPT)
        remedial_cards = self.revision.create_flashcards_from_weak_concepts(
            weak_concepts=[primary_weak],
            student_id=student_id
        )
        concise_notes = self.revision.generate_revision_notes(topic=concept_name)

        # Step 5: Member 2 (QuizGen AI)
        remedial_quiz = generate_test(
            topic=concept_name,
            difficulty="easy",
            n_mcq=3,
            n_desc=1
        )

        # Step 6: Member 3 (CodeMentor AI)
        exercise = self.codementor.generate_exercise(
            topic=f"{subject_name} data structures",
            difficulty="beginner",
            weak_concepts=[concept_name]
        )

        # Record ecosystem integration completion event
        self.event_bus.log_event(
            event_type="ecosystem_collaborative_cycle_complete",
            student_id=student_id,
            payload={
                "weak_concept": primary_weak,
                "sessions_scheduled": len(adapted_plan.sessions),
                "flashcards_created": len(remedial_cards),
                "quiz_questions": len(remedial_quiz.mcqs) + len(remedial_quiz.descriptive)
            },
            source_agent="Orchestrator"
        )

        return {
            "student_id": student_id,
            "target_weak_concept": primary_weak,
            "analyst_report": analysis,
            "adapted_study_plan": adapted_plan.model_dump(mode="json"),
            "tutorgpt_lesson": tutor_lesson.model_dump(),
            "revisiongpt_cards": [c.model_dump(mode="json") for c in remedial_cards],
            "revisiongpt_notes": concise_notes.model_dump(),
            "quizgen_test": remedial_quiz.model_dump(),
            "codementor_exercise": exercise
        }
