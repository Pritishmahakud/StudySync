"""
Data models for RevisionGPT (Member 6).
Includes Flashcards, Decks, Spaced Repetition (SM-2) logs, and Summaries.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewLog(BaseModel):
    card_id: str
    rating: int = Field(..., ge=0, le=5, description="SM-2 quality rating (0-5)")
    review_date: str = Field(default_factory=lambda: date.today().isoformat())
    interval_before: int = 0
    interval_after: int = 0
    ef_after: float = 2.5


class Flashcard(BaseModel):
    id: str
    deck_id: str = "default"
    front: str
    back: str
    hint: Optional[str] = None
    concept: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    
    # SuperMemo SM-2 State Variables
    repetition: int = 0
    interval: int = 0  # Interval in days
    easiness_factor: float = 2.5
    next_review_date: str = Field(default_factory=lambda: date.today().isoformat())
    last_reviewed: Optional[str] = None
    history: List[ReviewLog] = Field(default_factory=list)


class Deck(BaseModel):
    id: str
    name: str
    description: str = ""
    cards: List[Flashcard] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RevisionNote(BaseModel):
    topic: str
    summary_table: List[Dict[str, str]] = Field(default_factory=list)
    key_formulas: List[str] = Field(default_factory=list)
    common_pitfalls: List[str] = Field(default_factory=list)
    sixty_second_recap: str = ""
    full_markdown: str = ""


class TopicSummary(BaseModel):
    topic: str
    tldr: str
    core_pillars: List[str] = Field(default_factory=list)
    detailed_takeaways: List[str] = Field(default_factory=list)
    quick_checklist: List[str] = Field(default_factory=list)
    full_markdown: str = ""
