"""
StudySync – Smart Study Planner & Scheduling Engine.
Generates personalized, deadline-prioritized daily timetables and adapts dynamically
to student quiz scores and learning velocity.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from shared.auth import require_auth
from shared.styles import apply_theme, render_header
from studyplanner import Availability, PlanRequest, Subject, build_plan

st.set_page_config(page_title="Study Planner – StudySync", page_icon="📅", layout="wide")
apply_theme()
current_user = require_auth()

render_header(
    title="Smart Study Planner",
    subtitle="Personalized, deadline-aware, self-adjusting daily study schedules based on your exam dates.",
    badge="Schedule Engine"
)

today = date.today()
default_subjects = pd.DataFrame([
    {"name": "DBMS", "exam_date": today + timedelta(days=10), "difficulty": 4, "est_hours": 18.0, "weakness": 0.4},
    {"name": "Operating Systems", "exam_date": today + timedelta(days=14), "difficulty": 3, "est_hours": 14.0, "weakness": 0.1},
    {"name": "Maths & Algorithms", "exam_date": today + timedelta(days=20), "difficulty": 5, "est_hours": 24.0, "weakness": 0.3},
])

st.markdown("### 1. Your Subjects & Target Exams")
st.caption("Edit exam dates, estimated hours, and difficulty to generate an optimized daily plan.")
df_edited = st.data_editor(default_subjects, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    wd_hours = st.slider("Available Weekday Study Hours:", 1.0, 8.0, 3.0, 0.5)
with c2:
    we_hours = st.slider("Available Weekend Study Hours:", 1.0, 10.0, 5.0, 0.5)

if st.button("Generate Optimized Timetable", type="primary"):
    subjects_list = [
        Subject(
            name=r.name,
            exam_date=r.exam_date,
            difficulty=int(r.difficulty),
            est_hours=float(r.est_hours),
            weakness=float(r.weakness)
        )
        for r in df_edited.itertuples()
    ]
    req = PlanRequest(
        student_id="Asha",
        start_date=today,
        subjects=subjects_list,
        availability=Availability(weekday_hours=wd_hours, weekend_hours=we_hours)
    )
    plan = build_plan(req)
    st.session_state.current_schedule = plan

if "current_schedule" in st.session_state:
    plan = st.session_state.current_schedule
    st.write("")
    st.markdown("### 🗓️ Generated Daily Study Schedule")

    sessions_data = [s.model_dump() for s in plan.sessions]
    if sessions_data:
        sdf = pd.DataFrame(sessions_data)
        col_tbl, col_cht = st.columns([6, 5])
        with col_tbl:
            st.dataframe(sdf[["date", "subject", "kind", "minutes", "focus"]], use_container_width=True, height=400)
        with col_cht:
            st.markdown("**Hours Scheduled per Subject**")
            hours_map = plan.hours_by_subject
            st.bar_chart(pd.Series(hours_map))

    for w in plan.warnings:
        st.warning(f"⚠️ {w}")
