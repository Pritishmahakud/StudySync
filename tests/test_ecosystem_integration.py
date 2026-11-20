"""
End-to-End Collaborative Integration Test for all six StudySync agents.
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import unittest
from shared.orchestrator import StudySyncOrchestrator


class TestEcosystemIntegration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StudySyncOrchestrator()

    def test_end_to_end_collaborative_learning_cycle(self):
        report = self.orchestrator.run_collaborative_learning_cycle("Asha")

        # 1. Verification of Student and Target Focus
        self.assertEqual(report["student_id"], "Asha")
        self.assertIsNotNone(report["target_weak_concept"])

        # 2. PerformanceAnalyst AI report
        self.assertIn("subjects", report["analyst_report"])
        self.assertIn("concepts", report["analyst_report"])
        self.assertIn("progress", report["analyst_report"])

        # 3. StudyPlanner AI plan
        plan = report["adapted_study_plan"]
        self.assertGreater(len(plan["sessions"]), 0)

        # 4. TutorGPT lesson
        lesson = report["tutorgpt_lesson"]
        self.assertTrue(len(lesson["full_markdown"]) > 50)

        # 5. RevisionGPT flashcards & notes
        cards = report["revisiongpt_cards"]
        self.assertGreaterEqual(len(cards), 1)
        self.assertTrue(len(report["revisiongpt_notes"]["full_markdown"]) > 50)

        # 6. QuizGen AI test
        test = report["quizgen_test"]
        self.assertGreater(len(test["mcqs"]), 0)

        # 7. CodeMentor exercise
        exercise = report["codementor_exercise"]
        self.assertIn("title", exercise)


if __name__ == "__main__":
    unittest.main()
