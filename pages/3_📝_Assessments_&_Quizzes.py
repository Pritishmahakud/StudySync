"""
StudySync – Assessments, Quizzes & Exam Practice.
Generates structured MCQs and descriptive questions, provides rubric-based evaluations,
and explains conceptual mistakes.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from quizgen import evaluate_descriptive, explain_wrong_answer, generate_test, log_event
from shared.auth import require_auth
from shared.styles import apply_theme, render_header

st.set_page_config(page_title="Assessments & Quizzes – StudySync", page_icon="📝", layout="wide")
apply_theme()
current_user = require_auth()

render_header(
    title="Assessments & Knowledge Checks",
    subtitle="Test your mastery with AI-generated multiple-choice and descriptive questions with rubric grading.",
    badge="Assessment Engine"
)

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    quiz_topic = st.text_input("Enter Topic for Assessment:", "Database Normalization (BCNF)")
with c2:
    quiz_diff = st.selectbox("Difficulty Level:", ["easy", "medium", "hard"], index=1)
with c3:
    num_mcq = st.number_input("Number of MCQs:", min_value=1, max_value=6, value=3)

if st.button("Generate Assessment Test", type="primary"):
    with st.spinner("Compiling assessment questions with rubrics..."):
        test_obj = generate_test(topic=quiz_topic, difficulty=quiz_diff, n_mcq=num_mcq, n_desc=1)
        st.session_state.active_assessment = test_obj

if "active_assessment" in st.session_state:
    test = st.session_state.active_assessment
    st.write("")
    st.markdown(f"### 📋 Test: {test.topic} ({test.difficulty.upper()})")

    st.markdown("#### Part 1: Multiple-Choice Questions")
    for i, mcq in enumerate(test.mcqs):
        with st.container():
            st.markdown(
                f"""
                <div class="study-card">
                    <span class="badge-blue">Question {i+1}</span>
                    <span class="badge-green">{mcq.difficulty.title()}</span>
                    <h4 style="color: #1B4D3E; margin-top: 6px;">{mcq.question}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            choice = st.radio(f"Select your answer for Q{i+1}:", mcq.options, key=f"asm_mcq_{i}")
            if st.button(f"Submit Q{i+1} Answer", key=f"btn_asm_sub_{i}"):
                chosen_idx = mcq.options.index(choice)
                if chosen_idx == mcq.answer_index:
                    st.success("✅ Correct! Excellent understanding.")
                    log_event("Asha", test.topic_id, 1.0, test.difficulty, concept=mcq.concept, question_type="mcq")
                else:
                    st.error("❌ Incorrect Answer.")
                    explanation = explain_wrong_answer(mcq, chosen_idx)
                    st.info(f"**Tutor Diagnostic**: {explanation}")
                    log_event("Asha", test.topic_id, 0.0, test.difficulty, concept=mcq.concept, question_type="mcq")

    if test.descriptive:
        st.write("")
        st.markdown("#### Part 2: Descriptive Problem (Rubric Graded)")
        dq = test.descriptive[0]
        st.markdown(
            f"""
            <div class="study-card">
                <span class="badge-blue">Descriptive Question</span>
                <span class="badge-green">Max Marks: {dq.max_marks}</span>
                <h4 style="color: #1B4D3E; margin-top: 6px;">{dq.question}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        student_resp = st.text_area("Write your answer below:", height=150, key="asm_desc_resp")
        if st.button("Submit Descriptive Answer for Rubric Evaluation", type="primary"):
            with st.spinner("Examiner is evaluating answer against strict rubric criteria..."):
                res = evaluate_descriptive(dq, student_resp)
                st.markdown("### 📊 Evaluation Result")
                st.write(f"**Score Awarded**: `{res.score}` / `{res.max_marks}`")
                c_cov, c_miss = st.columns(2)
                with c_cov:
                    st.success(f"**Points Covered**: {', '.join(res.covered_points) if res.covered_points else 'None'}")
                with c_miss:
                    st.warning(f"**Points Missing**: {', '.join(res.missing_points) if res.missing_points else 'None'}")
                st.info(f"**Examiner Feedback**: {res.feedback}")
