"""
Spaced Repetition System (SRS) powered by the SuperMemo SM-2 Algorithm.
Calculates memory retention intervals, updates easiness factors,
and maintains due dates for active recall learning.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .models import Flashcard, ReviewLog


class SM2Engine:
    """
    Standard SuperMemo SM-2 Algorithm implementation.
    
    Quality Scale:
      5: Perfect response without hesitation
      4: Correct response after a hesitation
      3: Correct response recalled with serious difficulty
      2: Incorrect response; where the correct one seemed easy to recall
      1: Incorrect response; the correct one remembered
      0: Complete blackout
    """

    MIN_EASINESS_FACTOR = 1.3
    INITIAL_EASINESS_FACTOR = 2.5

    @classmethod
    def process_review(
        cls,
        card: Flashcard,
        quality: int,
        review_date: Optional[date] = None
    ) -> Flashcard:
        """
        Apply SM-2 formula to update repetition count, interval, and easiness factor.
        """
        if not (0 <= quality <= 5):
            raise ValueError(f"Quality rating must be between 0 and 5, got {quality}")

        r_date = review_date or date.today()
        interval_before = card.interval

        # 1. Update Easiness Factor (EF)
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        q = quality
        new_ef = card.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ef = max(cls.MIN_EASINESS_FACTOR, round(new_ef, 4))

        # 2. Update Repetition Count & Interval
        if q < 3:
            # Failed recall: reset repetitions and schedule for tomorrow
            new_rep = 0
            new_interval = 1
        else:
            # Successful recall
            if card.repetition == 0:
                new_interval = 1
            elif card.repetition == 1:
                new_interval = 6
            else:
                new_interval = max(1, int(round(card.interval * new_ef)))
            new_rep = card.repetition + 1

        # 3. Calculate Next Review Date
        next_due = r_date + timedelta(days=new_interval)

        # 4. Record Review History
        log = ReviewLog(
            card_id=card.id,
            rating=quality,
            review_date=r_date.isoformat(),
            interval_before=interval_before,
            interval_after=new_interval,
            ef_after=new_ef
        )

        card.repetition = new_rep
        card.interval = new_interval
        card.easiness_factor = new_ef
        card.last_reviewed = r_date.isoformat()
        card.next_review_date = next_due.isoformat()
        card.history.append(log)

        return card


class DeckManager:
    """Manages collections of flashcards and schedules spaced reviews."""

    def __init__(self, cards: Optional[List[Flashcard]] = None):
        self.cards: Dict[str, Flashcard] = {c.id: c for c in (cards or [])}

    def add_card(self, card: Flashcard):
        self.cards[card.id] = card

    def add_cards(self, cards: List[Flashcard]):
        for c in cards:
            self.cards[c.id] = c

    def get_card(self, card_id: str) -> Optional[Flashcard]:
        return self.cards.get(card_id)

    def get_due_cards(
        self,
        target_date: Optional[date] = None,
        deck_id: Optional[str] = None
    ) -> List[Flashcard]:
        """Return cards scheduled for review on or before target_date."""
        check_date = (target_date or date.today()).isoformat()
        due = []
        for c in self.cards.values():
            if deck_id and c.deck_id != deck_id:
                continue
            if c.next_review_date <= check_date:
                due.append(c)
        # Sort by urgency (earliest due first)
        due.sort(key=lambda x: x.next_review_date)
        return due

    def review_card(self, card_id: str, quality: int, review_date: Optional[date] = None) -> Flashcard:
        """Process review for a specific card."""
        card = self.cards.get(card_id)
        if not card:
            raise KeyError(f"Flashcard with ID '{card_id}' not found.")
        return SM2Engine.process_review(card, quality, review_date)

    def get_deck_stats(self, deck_id: Optional[str] = None) -> Dict[str, Any]:
        """Compute comprehensive spaced repetition retention and mastery metrics."""
        filtered = [c for c in self.cards.values() if not deck_id or c.deck_id == deck_id]
        if not filtered:
            return {
                "total_cards": 0,
                "due_today": 0,
                "mastered": 0,
                "learning": 0,
                "retention_rate": 0.0,
                "avg_easiness_factor": 2.5
            }

        today_str = date.today().isoformat()
        due = [c for c in filtered if c.next_review_date <= today_str]
        mastered = [c for c in filtered if c.repetition >= 4 and c.interval >= 15]
        learning = [c for c in filtered if c.repetition < 4]

        # Calculate retention rate across all logged reviews
        total_reviews = sum(len(c.history) for c in filtered)
        successful_reviews = sum(
            sum(1 for log in c.history if log.rating >= 3)
            for c in filtered
        )
        retention = (successful_reviews / total_reviews * 100) if total_reviews > 0 else 100.0
        avg_ef = sum(c.easiness_factor for c in filtered) / len(filtered)

        return {
            "total_cards": len(filtered),
            "due_today": len(due),
            "mastered": len(mastered),
            "learning": len(learning),
            "retention_rate": round(retention, 1),
            "avg_easiness_factor": round(avg_ef, 2)
        }

    def get_workload_forecast(self, days_ahead: int = 7) -> Dict[str, int]:
        """Forecast card review load per day for upcoming days (used by StudyPlanner)."""
        today = date.today()
        forecast = {}
        for d in range(days_ahead):
            cur = today + timedelta(days=d)
            cur_str = cur.isoformat()
            count = sum(1 for c in self.cards.values() if c.next_review_date == cur_str)
            forecast[cur_str] = count
        return forecast
