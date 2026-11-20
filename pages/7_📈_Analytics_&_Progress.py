"""
StudySync – Performance Analytics, ML Progress Trends & Insights.
Tracks test scores across concepts, computes linear regression trajectory slopes,
and flags high-priority weak areas for remediation.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from performance_analyst import PerformanceAnalyst
from shared.auth import require_auth
from shared.styles import apply_theme, render_header

st.set_page_config(page_title="Performance Analytics – StudySync", page_icon="📈", layout="wide")
apply_theme()
current_user = require_auth()

if "analyst" not in st.session_state:
    st.session_state.analyst = PerformanceAnalyst()

render_header(
    title="Performance Analytics & Progress",
    subtitle="Machine learning-powered learning trajectory analysis, concept mastery tracking, and personalized insights.",
    badge="Analytics Engine"
)

student = st.text_input("Active Student:", "Asha")
report = st.session_state.analyst.analyse_student(student)

c_s1, c_s2 = st.columns(2)
with c_s1:
    st.markdown("### 📊 Subject Mastery Overview")
    st.dataframe(report["subjects"], use_container_width=True)
with c_s2:
    st.markdown("### 🎯 Concept-by-Concept Performance")
    st.dataframe(report["concepts"], use_container_width=True)

st.write("")
st.markdown("### 📈 ML Learning Trajectory (Linear Regression Slopes)")
st.caption("Linear regression calculated on score percentage over time to detect whether understanding is Improving, Stable, or Declining.")
st.dataframe(report["progress"], use_container_width=True)

st.write("")
st.markdown("### 🚨 High-Priority Focus & Remedial Actions")
for rec in report["recommendations"]:
    if "HIGH" in rec:
        st.error(rec)
    elif "MEDIUM" in rec:
        st.warning(rec)
    else:
        st.info(rec)

st.write("")
st.markdown("### 💡 AI Academic Diagnostic")
st.info(report["llm_insights"])
