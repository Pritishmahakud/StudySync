"""
PerformanceAnalyst AI (Member 5).
Data Analysis, ML Linear Regression Progress Tracking,
and Personalized Recommendations linked to TutorGPT, QuizGen, and RevisionGPT.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from sklearn.linear_model import LinearRegression

from shared.event_bus import get_event_bus
from shared.llm_provider import ask

DEFAULT_CSV = Path(__file__).parent.parent / "data" / "quiz_results.csv"

WEAK_BELOW = 50.0       # below 50%  -> Weak
AVERAGE_BELOW = 70.0    # 50-70%     -> Average, >70% -> Strong


def create_sample_dataset(csv_path: Optional[Path] = None) -> Path:
    """Generate representative student test history for testing."""
    target = csv_path or DEFAULT_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        # student, date, subject, concept, score, max_score
        ("Asha", "2026-10-01", "Maths", "Algebra", 8, 10),
        ("Asha", "2026-10-01", "Maths", "Calculus", 4, 10),
        ("Asha", "2026-10-08", "Maths", "Calculus", 5, 10),
        ("Asha", "2026-10-15", "Maths", "Calculus", 6, 10),
        ("Asha", "2026-10-05", "Physics", "Motion", 9, 10),
        ("Asha", "2026-10-12", "Physics", "Motion", 8, 10),
        ("Asha", "2026-10-12", "Physics", "Thermodynamics", 3, 10),
        ("Asha", "2026-10-19", "Physics", "Thermodynamics", 3, 10),
        ("Asha", "2026-10-07", "Chemistry", "Bonding", 7, 10),
        ("Asha", "2026-10-21", "Chemistry", "Bonding", 6, 10),
        ("Asha", "2026-10-28", "Chemistry", "Bonding", 4, 10),
        # DBMS
        ("Asha", "2026-11-01", "DBMS", "Transactions", 8, 10),
        ("Asha", "2026-11-05", "DBMS", "Normalization", 4, 10),
        ("Asha", "2026-11-12", "DBMS", "Normalization", 3, 10),
        # OS
        ("Asha", "2026-11-02", "Operating Systems", "Semaphores", 7, 10),
        ("Asha", "2026-11-09", "Operating Systems", "Deadlocks", 4, 10),
    ]
    df = pd.DataFrame(rows, columns=["student", "date", "subject", "concept", "score", "max_score"])
    df.to_csv(target, index=False)
    return target


def level(p: float) -> str:
    if p < WEAK_BELOW:
        return "Weak"
    if p < AVERAGE_BELOW:
        return "Average"
    return "Strong"


class PerformanceAnalyst:
    """
    Member 5: Analytics Agent
    - Analyzes student test and coding performance
    - Detects weak subjects and concepts
    - Tracks progress trends over time with Linear Regression ML
    - Feeds weak concept IDs into StudyPlanner (Member 4) and RevisionGPT (Member 6)
    """

    def __init__(self, csv_path: Optional[Path] = None):
        self.csv_path = csv_path or DEFAULT_CSV
        if not self.csv_path.exists():
            create_sample_dataset(self.csv_path)
        self.event_bus = get_event_bus()

    def load_data(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            create_sample_dataset(self.csv_path)
        df = pd.read_csv(self.csv_path, parse_dates=["date"])
        df["percent"] = df["score"] / df["max_score"] * 100
        return df.sort_values("date")

    def subject_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        s = df.groupby("subject")["percent"].mean().round(1).reset_index()
        s["level"] = s["percent"].apply(level)
        return s.sort_values("percent")

    def concept_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        c = df.groupby(["subject", "concept"])["percent"].mean().round(1).reset_index()
        c["level"] = c["percent"].apply(level)
        return c.sort_values("percent")

    def trend_for_concept(self, group: pd.DataFrame) -> str:
        """Estimate student learning trajectory using scikit-learn LinearRegression."""
        if len(group) < 2:
            return "Stable"
        x = (group["date"] - group["date"].min()).dt.days.values.reshape(-1, 1)
        y = group["percent"].values
        slope = LinearRegression().fit(x, y).coef_[0]  # % change per day
        per_week = slope * 7
        if per_week > 1.0:
            return "Improving"
        if per_week < -1.0:
            return "Declining"
        return "Stable"

    def progress_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for (subject, concept), g in df.groupby(["subject", "concept"]):
            rows.append({"subject": subject, "concept": concept, "trend": self.trend_for_concept(g)})
        return pd.DataFrame(rows)

    def rule_based_recommendations(self, concepts: pd.DataFrame, progress: pd.DataFrame) -> List[str]:
        merged = concepts.merge(progress, on=["subject", "concept"])
        recs = []
        for _, r in merged.iterrows():
            if r["level"] == "Weak" and r["trend"] != "Improving":
                recs.append(f"🚨 HIGH priority: {r['subject']} - {r['concept']} "
                            f"({r['percent']}%, {r['trend']}). Re-learn basics with TutorGPT, "
                            f"then practice with QuizGen.")
            elif r["level"] == "Weak":
                recs.append(f"⚠️ MEDIUM priority: {r['subject']} - {r['concept']} is weak but improving. "
                            f"Keep practicing.")
            elif r["trend"] == "Declining":
                recs.append(f"🔍 WATCH: {r['subject']} - {r['concept']} is declining "
                            f"({r['percent']}%). Revise soon with RevisionGPT.")
        return recs or ["🎉 Great work! No weak areas found."]

    def llm_insights(self, student: str, subjects: pd.DataFrame, concepts: pd.DataFrame, progress: pd.DataFrame) -> str:
        data = {
            "subjects": subjects.to_dict("records"),
            "concepts": concepts.to_dict("records"),
            "trends": progress.to_dict("records"),
        }
        system = "You are a supportive, insightful learning analytics coach in the StudySync ecosystem."
        prompt = (
            f"Student: {student}\n"
            f"Performance data:\n{json.dumps(data)}\n\n"
            "Provide: (1) A 2-line performance diagnostic, (2) Top 3 weak concepts that require immediate focus, "
            "(3) Specific action items using TutorGPT, QuizGen, and RevisionGPT."
        )
        return ask(system=system, user=prompt)

    def analyse_student(self, student: str = "Asha") -> Dict[str, Any]:
        df = self.load_data()
        student_df = df[df["student"].str.lower() == student.lower()]
        if student_df.empty:
            # Fall back to all data if specific name not found
            student_df = df

        subjects = self.subject_summary(student_df)
        concepts = self.concept_summary(student_df)
        progress = self.progress_summary(student_df)

        recs = self.rule_based_recommendations(concepts, progress)
        insights = self.llm_insights(student, subjects, concepts, progress)

        # Extract weak concepts list for other agents
        weak_df = concepts[concepts["level"] == "Weak"]
        weak_list = [f"{r['subject']}.{r['concept']}" for _, r in weak_df.iterrows()]

        # Subject score map for StudyPlanner
        score_map = {r["subject"]: float(r["percent"]) for _, r in subjects.iterrows()}

        return {
            "student": student,
            "subjects": subjects,
            "concepts": concepts,
            "progress": progress,
            "recommendations": recs,
            "llm_insights": insights,
            "weak_concepts_list": weak_list,
            "subject_score_map": score_map
        }

    def record_quiz_score(self, student: str, subject: str, concept: str, score: float, max_score: float = 10.0):
        """Append a newly completed quiz score to the CSV and log event."""
        today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
        new_row = pd.DataFrame([{
            "student": student,
            "date": today_str,
            "subject": subject,
            "concept": concept,
            "score": score,
            "max_score": max_score
        }])
        new_row.to_csv(self.csv_path, mode="a", header=not self.csv_path.exists(), index=False)
