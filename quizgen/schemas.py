"""
Pydantic Schemas for QuizGen AI (Member 2).
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

Difficulty = Literal["easy", "medium", "hard"]


class MCQ(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str
    concept: str = ""          # sub-concept tested (useful for PerformanceAnalyst)
    difficulty: Difficulty = "medium"

    @model_validator(mode="after")
    def options_distinct(self):
        if len({o.strip().lower() for o in self.options}) != 4:
            # If options are slightly duplicate in LLM output, ensure uniqueness gracefully
            seen = set()
            new_opts = []
            for idx, opt in enumerate(self.options):
                cleaned = opt.strip()
                if cleaned.lower() in seen:
                    cleaned = f"{cleaned} (Option {idx+1})"
                seen.add(cleaned.lower())
                new_opts.append(cleaned)
            self.options = new_opts
        return self


class DescriptiveQ(BaseModel):
    question: str
    model_answer: str
    key_points: List[str] = Field(min_length=2)   # rubric used for grading
    max_marks: int = 10
    concept: str = ""
    difficulty: Difficulty = "medium"


class Test(BaseModel):
    topic: str
    topic_id: str
    difficulty: Difficulty
    mcqs: List[MCQ] = []
    descriptive: List[DescriptiveQ] = []


class DescriptiveResult(BaseModel):
    score: float
    max_marks: int
    covered_points: List[str]
    missing_points: List[str]
    feedback: str
