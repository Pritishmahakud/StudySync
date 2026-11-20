"""
Unit tests for RevisionGPT (Member 6) and SuperMemo SM-2 Algorithm.
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from datetime import date, timedelta
import unittest
from revisiongpt import DeckManager, Flashcard, RevisionGPT, SM2Engine


class TestRevisionGPT(unittest.TestCase):
    def setUp(self):
        self.rev = RevisionGPT()

    def test_flashcard_generation(self):
        cards = self.rev.generate_flashcards("Deadlocks", count=3, difficulty="medium")
        self.assertGreaterEqual(len(cards), 1)
        self.assertIn(cards[0].difficulty, ["easy", "medium", "hard"])
        self.assertTrue(hasattr(cards[0], "front"))
        self.assertTrue(hasattr(cards[0], "back"))

    def test_sm2_first_successful_review(self):
        card = Flashcard(
            id="test_1",
            front="What is 2PL?",
            back="Two Phase Locking",
            repetition=0,
            interval=0,
            easiness_factor=2.5,
            next_review_date=date.today().isoformat()
        )
        # Quality 5 (Perfect recall)
        updated = SM2Engine.process_review(card, quality=5)
        self.assertEqual(updated.repetition, 1)
        self.assertEqual(updated.interval, 1)  # First repetition interval is 1 day
        self.assertGreaterEqual(updated.easiness_factor, 2.5)

    def test_sm2_second_successful_review(self):
        card = Flashcard(
            id="test_2",
            front="What is 2PL?",
            back="Two Phase Locking",
            repetition=1,
            interval=1,
            easiness_factor=2.5,
            next_review_date=date.today().isoformat()
        )
        updated = SM2Engine.process_review(card, quality=4)
        self.assertEqual(updated.repetition, 2)
        self.assertEqual(updated.interval, 6)  # Second repetition interval is 6 days

    def test_sm2_failed_recall_resets_repetition(self):
        card = Flashcard(
            id="test_3",
            front="Complex Theorem",
            back="Deep proof",
            repetition=4,
            interval=25,
            easiness_factor=2.4,
            next_review_date=date.today().isoformat()
        )
        # Quality 1 (Failed recall)
        updated = SM2Engine.process_review(card, quality=1)
        self.assertEqual(updated.repetition, 0)
        self.assertEqual(updated.interval, 1)
        self.assertGreaterEqual(updated.easiness_factor, 1.3)

    def test_sm2_minimum_easiness_factor(self):
        card = Flashcard(
            id="test_4",
            front="Q",
            back="A",
            easiness_factor=1.35
        )
        updated = SM2Engine.process_review(card, quality=0)
        self.assertGreaterEqual(updated.easiness_factor, 1.3)

    def test_concise_revision_notes(self):
        notes = self.rev.generate_revision_notes("Normalization BCNF")
        self.assertEqual(notes.topic, "Normalization BCNF")
        self.assertTrue(len(notes.full_markdown) > 50)

    def test_topic_summary(self):
        summary = self.rev.generate_topic_summary("Process Scheduling")
        self.assertTrue(len(summary.tldr) > 10)
        self.assertGreater(len(summary.core_pillars), 0)

    def test_due_cards_filtering(self):
        today = date.today()
        card_past = Flashcard(id="c1", front="Q1", back="A1", next_review_date=(today - timedelta(days=1)).isoformat())
        card_today = Flashcard(id="c2", front="Q2", back="A2", next_review_date=today.isoformat())
        card_future = Flashcard(id="c3", front="Q3", back="A3", next_review_date=(today + timedelta(days=5)).isoformat())

        mgr = DeckManager([card_past, card_today, card_future])
        due = mgr.get_due_cards(target_date=today)
        self.assertEqual(len(due), 2)
        self.assertEqual({c.id for c in due}, {"c1", "c2"})


if __name__ == "__main__":
    unittest.main()
