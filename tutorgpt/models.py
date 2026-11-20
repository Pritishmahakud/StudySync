"""
Data models for TutorGPT (Member 1).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TutorMode(str, Enum):
    EXPLANATION = "explanation"
    SOCRATIC = "socratic"
    STEP_BY_STEP = "step_by_step"


class DocumentChunk(BaseModel):
    chunk_id: int
    source_name: str
    text: str
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TutorExplanation(BaseModel):
    concept: str
    difficulty: DifficultyLevel
    analogy: Optional[str] = None
    core_definition: str
    step_by_step: List[str] = Field(default_factory=list)
    practical_example: Optional[str] = None
    common_misconceptions: List[str] = Field(default_factory=list)
    socratic_check_question: Optional[str] = None
    full_markdown: str


class RAGResponse(BaseModel):
    query: str
    answer: str
    citations: List[DocumentChunk]
    grounded_in_material: bool
    confidence_score: float = 1.0


class SocraticResponse(BaseModel):
    student_message: str
    tutor_feedback: str
    probing_question: str
    hint: Optional[str] = None
    mastery_achieved: bool = False
