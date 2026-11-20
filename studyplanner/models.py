"""Data contracts for StudyPlanner AI (Member 4)."""

from datetime import date
from pydantic import BaseModel, Field


class Subject(BaseModel):
    name: str
    exam_date: date
    difficulty: int = Field(3, ge=1, le=5)          # 1 easy .. 5 hard
    est_hours: float | None = None                  # total hours needed; default = difficulty * 5
    weakness: float = Field(0.0, ge=0, le=1)        # 0 = strong, 1 = very weak (from PerformanceAnalyst)
    weak_concepts: list[str] = []                   # concept IDs, e.g. "dbms.normalization.bcnf"
    done_hours: float = 0.0                         # hours already studied


class Availability(BaseModel):
    weekday_hours: float = 3.0
    weekend_hours: float = 5.0
    days_off: list[date] = []


class PlanRequest(BaseModel):
    student_id: str
    start_date: date
    subjects: list[Subject]
    availability: Availability = Availability()
    block_minutes: int = 30          # scheduling granularity
    revision_window: int = 3         # last N days before an exam are revision-heavy


class Session(BaseModel):
    date: date
    subject: str
    minutes: int
    kind: str                        # "study" | "revise"
    focus: str | None = None         # weak concept to focus on


class Plan(BaseModel):
    student_id: str
    sessions: list[Session]
    warnings: list[str] = []
    hours_by_subject: dict[str, float] = {}


class AnalyticsFeedback(BaseModel):
    """What PerformanceAnalyst AI (Member 5) sends us."""
    student_id: str
    subject_scores: dict[str, float]                 # subject -> avg score 0..100
    weak_concepts: dict[str, list[str]] = {}         # subject -> concept IDs
