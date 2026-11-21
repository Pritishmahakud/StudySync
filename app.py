"""
StudySync – Modern Multi-Page Learning Ecosystem.
Main Student Dashboard & Course Hub.
Palette: Creme White, Forest Green, and subtle Sky Blue accents.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from performance_analyst import PerformanceAnalyst
from revisiongpt import RevisionGPT
from shared.auth import require_auth
from shared.document_parser import parse_uploaded_file
from shared.llm_provider import get_llm_provider
from shared.orchestrator import StudySyncOrchestrator
from shared.sample_materials import SAMPLE_MATERIALS
from shared.styles import apply_theme, render_header
from tutorgpt import TutorGPT


# =========================================================================
# Hosting Deployment Compatibility: Top-Level WSGI / ASGI Export
# Ensures cloud platforms (Render, Vercel, Gunicorn, Uvicorn, AWS) find 'app'
# =========================================================================
def wsgi_application(environ, start_response):
    """WSGI standard entry point for deployment platforms."""
    status = "200 OK"
    headers = [("Content-Type", "application/json; charset=utf-8")]
    start_response(status, headers)
    return [b'{"status": "ok", "service": "StudySync", "mode": "active"}']


# Top-level exports expected by cloud hosting runtimes
app = wsgi_application
application = wsgi_application
handler = wsgi_application


def _is_running_in_streamlit() -> bool:
    """Detect whether script is running inside active Streamlit server runtime."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_context
        return get_script_run_context() is not None
    except Exception:
        return False


def run_dashboard():
    """Streamlit Interactive Dashboard."""
    # Streamlit Page Setup
    st.set_page_config(
        page_title="StudySync – Modern Learning Platform",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply Theme
    apply_theme()

    # Enforce Security & Authentication
    current_user = require_auth()
    student_id = current_user["name"] if current_user else "Student"

    # Initialize Persistent Session State
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = StudySyncOrchestrator()
    if "tutor" not in st.session_state:
        st.session_state.tutor = TutorGPT()
    if "revision" not in st.session_state:
        st.session_state.revision = RevisionGPT()
    if "analyst" not in st.session_state:
        st.session_state.analyst = PerformanceAnalyst()
    if "rag_loaded" not in st.session_state:
        for filename, content in SAMPLE_MATERIALS.items():
            st.session_state.tutor.ingest_material(content, filename)
        st.session_state.rag_loaded = True
    if "selected_course" not in st.session_state:
        st.session_state.selected_course = None

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎓 StudySync")
        st.caption("Personalized Adaptive Learning Platform")
        st.divider()

        llm = get_llm_provider()
        st.markdown("##### ⚙️ AI Engine Status")
        if llm.provider in ("anthropic", "openai"):
            st.success(f"**Connected API**: `{llm.provider.upper()}`\n\nModel: `{llm.model}`")
        else:
            st.info(f"**Engine**: `Intelligent Offline AI`\n\n*(Ready out of the box. Add `ANTHROPIC_API_KEY` to .env for Claude)*")

        st.divider()
        stats = st.session_state.revision.get_deck_stats()
        st.markdown("##### 📌 Daily Quick Stats")
        st.write(f"- **Flashcards Due**: `{stats['due_today']}` cards")
        st.write(f"- **Retention Rate**: `{stats['retention_rate']}%`")
        st.write(f"- **Total Cards Mastered**: `{stats['mastered']}`")

    # Premium Hero Banner
    user_first_name = current_user['name'].split()[0] if current_user and 'name' in current_user else "Student"
    st.markdown(
        f"""
        <div class="hero-banner">
            <span class="badge-blue" style="background: rgba(255,255,255,0.15) !important; color: #FFFFFF !important; border: 1px solid rgba(255,255,255,0.3) !important;">
                ACTIVE TERM: SEMESTER 7
            </span>
            <h1 style="color: #FFFFFF !important; font-size: 2.3rem; margin-top: 10px; margin-bottom: 6px;">
                Welcome back, {user_first_name}! 👋
            </h1>
            <p style="color: #E2E8F0 !important; font-size: 1.05rem; max-width: 720px; line-height: 1.6; margin-bottom: 0;">
                Continue your curriculum, review daily SuperMemo SM-2 flashcards, or practice coding exercises.
                Your AI Tutor and Study Planner are synchronized with your upcoming exam milestones.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # KPI Metric Row
    k1, k2, k3, k4 = st.columns(4)
    analysis = st.session_state.analyst.analyse_student(student_id)
    weak_count = len(analysis.get("weak_concepts_list", []))

    with k1:
        st.markdown(
            """<div class="metric-box">
                <div class="metric-val">3</div>
                <div class="metric-lbl">ACTIVE COURSES</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""<div class="metric-box">
                <div class="metric-val">{stats['due_today']}</div>
                <div class="metric-lbl">FLASHCARDS DUE TODAY</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""<div class="metric-box">
                <div class="metric-val">{stats['retention_rate']}%</div>
                <div class="metric-lbl">MEMORY RETENTION (SM-2)</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""<div class="metric-box">
                <div class="metric-val" style="color: {'#DC2626' if weak_count > 0 else '#14382C'};">{weak_count}</div>
                <div class="metric-lbl">PRIORITY FOCUS AREAS</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.write("")

    # Enrolled Courses Section
    st.markdown("### 📚 My Enrolled Courses & Study Materials")
    st.caption("Click 'Open Course Material' on any course to open the interactive lecture reader, video player, and embedded AI tutoring.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">Computer Science</span>
                <span class="badge-green">Core Course</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Database Management Systems</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 55px;">
                    ACID Transactions, Serializability, Two-Phase Locking (2PL), and Relational Normalization (1NF to BCNF).
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⭐ 4.9 (1,420 students) • 12 Topics • ⏱️ 15 min read
                </div>
                <div style="background: #F1F5F9; border-radius: 6px; height: 6px; width: 100%; margin-bottom: 14px; overflow: hidden;">
                    <div style="background: #1B4D3E; height: 100%; width: 65%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Course Material", key="btn_dbms_main", type="primary", use_container_width=True):
            st.session_state.selected_course = "dbms_transactions.txt"
            st.switch_page("pages/1_📚_Course_Catalog.py")

    with c2:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">Systems</span>
                <span class="badge-green">Undergraduate</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Operating Systems</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 55px;">
                    Process Synchronization, Counting Semaphores, Coffman Deadlock Conditions, Banker's Algorithm, and CPU Scheduling.
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⭐ 4.8 (980 students) • 10 Topics • ⏱️ 18 min read
                </div>
                <div style="background: #F1F5F9; border-radius: 6px; height: 6px; width: 100%; margin-bottom: 14px; overflow: hidden;">
                    <div style="background: #1B4D3E; height: 100%; width: 80%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Course Material", key="btn_os_main", type="primary", use_container_width=True):
            st.session_state.selected_course = "os_process_synchronization.txt"
            st.switch_page("pages/1_📚_Course_Catalog.py")

    with c3:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">Algorithms</span>
                <span class="badge-green">Advanced</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Dynamic Programming & Graphs</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 55px;">
                    Memoization vs Tabulation, 0/1 Knapsack, Longest Common Subsequence, Dijkstra's and Bellman-Ford Shortest Path.
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⭐ 5.0 (2,100 students) • 14 Topics • ⏱️ 20 min read
                </div>
                <div style="background: #F1F5F9; border-radius: 6px; height: 6px; width: 100%; margin-bottom: 14px; overflow: hidden;">
                    <div style="background: #1B4D3E; height: 100%; width: 45%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Course Material", key="btn_dsa_main", type="primary", use_container_width=True):
            st.session_state.selected_course = "dsa_dynamic_programming.txt"
            st.switch_page("pages/1_📚_Course_Catalog.py")

    st.divider()

    # MULTI-FORMAT DOCUMENT UPLOAD HUB
    st.markdown("### 📤 Upload Your Own Notes & Lectures")
    st.caption("Upload lecture slides, course PDFs, Word documents, or notes. The system extracts the text and connects it directly to your AI Tutor for grounded Q&A, flashcard creation, and quizzes.")

    up_col1, up_col2 = st.columns([7, 3])

    with up_col1:
        uploaded_files = st.file_uploader(
            "Upload files (PDF, Word DOCX/DOC, PowerPoint PPTX/PPT, Markdown, or Text):",
            type=["pdf", "docx", "doc", "pptx", "ppt", "txt", "md"],
            accept_multiple_files=True,
            key="multi_file_uploader"
        )

        if uploaded_files:
            for uf in uploaded_files:
                file_bytes = uf.read()
                try:
                    extracted_text = parse_uploaded_file(uf.name, file_bytes)
                    chunks_added = st.session_state.tutor.ingest_material(extracted_text, uf.name)
                    SAMPLE_MATERIALS[uf.name] = extracted_text
                    st.success(f"✅ Successfully ingested **{uf.name}**: Extracted {len(extracted_text.split())} words and indexed {chunks_added} semantic chunks into your AI Tutor knowledge base!")
                except Exception as e:
                    st.error(f"❌ Error processing {uf.name}: {e}")

    with up_col2:
        st.markdown(
            """
            <div class="study-card" style="background: #F8FAFC; border: 1px solid #E2E8F0;">
                <h4 style="color: #14382C; margin-top: 0;">Supported Formats</h4>
                <ul style="padding-left: 20px; font-size: 0.88rem; line-height: 1.8; color: #475569;">
                    <li><strong>📄 PDF (.pdf)</strong>: Course textbooks & slides</li>
                    <li><strong>📝 Word (.docx, .doc)</strong>: Lecture transcripts & notes</li>
                    <li><strong>📊 PowerPoint (.pptx, .ppt)</strong>: Slide decks</li>
                    <li><strong>📑 Markdown (.md, .txt)</strong>: Raw notes</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Automated Collaborative Learning Cycle Trigger
    st.markdown("### ⚡ AI-Powered Automated Learning Remediation")
    if analysis.get("weak_concepts_list"):
        target_weak = analysis["weak_concepts_list"][0]
    elif analysis.get("concepts") is not None and not analysis["concepts"].empty:
        target_weak = f"{analysis['concepts'].iloc[0]['subject']}.{analysis['concepts'].iloc[0]['concept']}"
    else:
        target_weak = "Computer Science.Core Invariants"

    st.info(
        f"""
        **Focus Alert**: Your recent learning trajectory shows that **{target_weak}** needs reinforcement.
        Click below to trigger the collaborative multi-agent intervention: it re-balances your schedule,
        prepares a remedial lesson, creates targeted SM-2 flashcards, and generates verification tests!
        """
    )

    if st.button("Run Collaborative Remediation Cycle", type="primary"):
        with st.spinner("AI agents are collaborating across scheduling, teaching, flashcards, and assessment..."):
            report = st.session_state.orchestrator.run_collaborative_learning_cycle(student_id)
            st.balloons()
            st.success(f"🎯 Collaborative cycle completed for **{report['target_weak_concept']}**!")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Study Schedule Updated**:", f"{len(report['adapted_study_plan']['sessions'])} sessions balanced.")
                st.write("**Remedial Lesson**:", report["tutorgpt_lesson"]["concept"])
            with col_b:
                st.write("**SM-2 Flashcards Created**:", f"{len(report['revisiongpt_cards'])} cards added to active deck.")
                st.write("**Follow-up Assessment**:", f"{len(report['quizgen_test']['mcqs'])} MCQs ready.")


# Run Streamlit only when called via Streamlit runtime
if _is_running_in_streamlit():
    run_dashboard()
