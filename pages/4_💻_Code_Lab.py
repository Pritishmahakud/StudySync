"""
StudySync – Interactive Code Lab & Programming Mentor.
Explains source code, detects syntax and logical bugs with sandboxed execution,
and provides auto-gradable programming exercises.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from codementor import CodeMentorAgent
from shared.auth import require_auth
from shared.styles import apply_theme, render_header

st.set_page_config(page_title="Code Lab – StudySync", page_icon="💻", layout="wide")
apply_theme()
current_user = require_auth()

if "codementor" not in st.session_state:
    st.session_state.codementor = CodeMentorAgent()

render_header(
    title="Interactive Code Lab",
    subtitle="AI-powered code analysis, sandboxed execution, and automated test-case evaluation.",
    badge="Programming Studio"
)

lab_mode = st.radio("Select Mode:", ["Code Explainer & Complexity", "Error Detector & Sandbox", "Coding Challenge & Review"], horizontal=True)

st.write("")

if lab_mode == "Code Explainer & Complexity":
    code_input = st.text_area(
        "Enter Code to Analyze:",
        "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)",
        height=180
    )
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        lang = st.selectbox("Language:", ["python", "javascript"], index=0)
    with col_l2:
        level = st.selectbox("Explanation Level:", ["beginner", "intermediate", "advanced"], index=0)

    if st.button("Analyze Code", type="primary"):
        with st.spinner("Analyzing AST, algorithmic patterns, and complexity..."):
            res = st.session_state.codementor.explain_code(code_input, language=lang, level=level)
            st.markdown(
                f"""
                <div class="study-card">
                    <span class="badge-blue">Time: {res.get('time_complexity')}</span>
                    <span class="badge-green">Space: {res.get('space_complexity')}</span>
                    <h3 style="color: #1B4D3E; margin-top: 8px;">{res.get('summary')}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("#### Line-by-Line Breakdown")
            for step in res.get("step_by_step", []):
                st.write(f"- **Lines {step.get('lines')}**: {step.get('explanation')}")

elif lab_mode == "Error Detector & Sandbox":
    buggy_code = st.text_area(
        "Paste Code to Debug & Run in Sandbox:",
        "def calculate_average(grades):\n    total = 0\n    for i in range(len(grades) + 1):\n        total += grades[i]\n    return total / len(grades)\n\nprint(calculate_average([85, 90, 78]))",
        height=180
    )
    if st.button("Execute & Detect Bugs", type="primary"):
        with st.spinner("Running in sandboxed subprocess and checking logic invariants..."):
            res = st.session_state.codementor.detect_errors(buggy_code, run=True)
            if res.get("execution"):
                exec_data = res["execution"]
                st.markdown("#### ⚙️ Execution Sandbox Output")
                if exec_data.get("stdout"):
                    st.code(exec_data["stdout"], language="text")
                if exec_data.get("stderr"):
                    st.error(exec_data["stderr"])

            st.write("")
            st.markdown("#### 🔍 Static & Logical Error Analysis")
            if not res.get("has_errors"):
                st.success("No syntax or logical errors detected! Code ran smoothly.")
            else:
                for err in res.get("errors", []):
                    st.markdown(
                        f"""
                        <div class="study-card" style="border-left: 4px solid #DC2626;">
                            <span class="badge-blue">Line {err.get('line') or 'N/A'}</span>
                            <span class="badge-green">{err.get('severity', 'Error').upper()}</span>
                            <h4 style="color: #DC2626; margin-top: 6px;">{err.get('description')}</h4>
                            <p><strong>Why it happens:</strong> {err.get('why_it_happens')}</p>
                            <p style="background: #F8FAFC; padding: 8px; border-radius: 6px;"><code>{err.get('fix')}</code></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

else:
    st.markdown("### 🏆 Auto-Graded Coding Challenge")
    c_t, c_d = st.columns([3, 1])
    with c_t:
        topic_ex = st.text_input("Challenge Topic:", "Two Sum or Array Search")
    with c_d:
        diff_ex = st.selectbox("Difficulty:", ["beginner", "intermediate", "advanced"], index=0)

    if st.button("Generate Coding Challenge", type="primary"):
        with st.spinner("Creating auto-gradable challenge with hidden tests..."):
            ex = st.session_state.codementor.generate_exercise(topic_ex, difficulty=diff_ex)
            st.session_state.active_ex = ex

    if "active_ex" in st.session_state:
        ex = st.session_state.active_ex
        st.markdown(
            f"""
            <div class="study-card">
                <span class="badge-blue">{ex.get('difficulty', '').upper()}</span>
                <span class="badge-green">Auto-Graded</span>
                <h3 style="color: #1B4D3E; margin-top: 6px;">{ex.get('title')}</h3>
                <p>{ex.get('statement')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        student_code = st.text_area("Your Solution Code:", ex.get("starter_code", "# Write your solution\n"), height=200)
        if st.button("Submit & Run Against Test Cases", type="primary"):
            with st.spinner("Running tests in sandbox and computing code quality score..."):
                review = st.session_state.codementor.review_solution(student_code, exercise=ex, student_id="Asha")
                st.markdown(
                    f"""
                    <div class="study-card">
                        <span class="badge-blue">Score: {review.get('score')} / 100</span>
                        <span class="badge-green">Tests: {review.get('tests_passed')}/{review.get('tests_total')} Passed</span>
                        <h4 style="color: #1B4D3E; margin-top: 6px;">Verdict: {review.get('verdict', '').title()}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("#### Test Case Execution")
                for t in review.get("test_results", []):
                    st.write(f"- Test #{t['test']}: {'✅ PASSED' if t['passed'] else '❌ FAILED'}")
