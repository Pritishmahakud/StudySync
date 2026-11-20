"""
Unit tests for TutorGPT (Member 1).
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import unittest
from tutorgpt import DifficultyLevel, RAGEngine, TutorGPT


class TestTutorGPT(unittest.TestCase):
    def setUp(self):
        self.tutor = TutorGPT()

    def test_explain_concept_beginner(self):
        res = self.tutor.explain_concept("Binary Search", difficulty=DifficultyLevel.BEGINNER)
        self.assertEqual(res.concept, "Binary Search")
        self.assertEqual(res.difficulty, DifficultyLevel.BEGINNER)
        self.assertTrue(len(res.full_markdown) > 50)

    def test_explain_concept_advanced(self):
        res = self.tutor.explain_concept("Two-Phase Locking", difficulty=DifficultyLevel.ADVANCED)
        self.assertEqual(res.difficulty, DifficultyLevel.ADVANCED)
        self.assertIn("Two-Phase Locking", res.full_markdown)

    def test_rag_ingest_and_retrieve(self):
        rag = RAGEngine(chunk_size=200, chunk_overlap=40)
        sample_doc = (
            "Dijkstra's algorithm finds the shortest path between nodes in a graph with non-negative edge weights. "
            "It uses a priority queue to greedily select the unvisited vertex with smallest tentative distance. "
            "The time complexity is O((V + E) log V) using a binary heap."
        )
        count = rag.ingest_text(sample_doc, "dijkstra.txt")
        self.assertGreater(count, 0)

        chunks = rag.retrieve("shortest path priority queue", top_k=2)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0].source_name, "dijkstra.txt")
        self.assertGreater(chunks[0].score, 0.0)

    def test_rag_answering_with_citations(self):
        self.tutor.ingest_material(
            "ACID transactions require Atomicity, Consistency, Isolation, and Durability.",
            "acid_notes.txt"
        )
        res = self.tutor.answer_with_rag("What does ACID stand for?", top_k=2)
        self.assertTrue(res.grounded_in_material)
        self.assertGreater(len(res.citations), 0)
        self.assertEqual(res.citations[0].source_name, "acid_notes.txt")

    def test_socratic_mode(self):
        res = self.tutor.socratic_guide(
            concept="Recursion Base Case",
            student_message="I understand recursion calls itself, but why does my code crash?"
        )
        self.assertIsNotNone(res.probing_question)
        self.assertIsNotNone(res.tutor_feedback)


if __name__ == "__main__":
    unittest.main()
