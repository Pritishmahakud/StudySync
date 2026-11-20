"""
StudySync – Interactive Course & Study Material Reader.
Coursera / Udemy style lecture view with reading material, media,
and embedded grounded AI tutoring and flashcard generation.
Supports PDF, Word (DOCX/DOC), PowerPoint (PPTX/PPT), and Markdown/Text.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from quizgen import generate_test
from revisiongpt import RevisionGPT
from shared.auth import require_auth
from shared.document_parser import parse_uploaded_file
from shared.sample_materials import SAMPLE_MATERIALS
from shared.styles import apply_theme, render_header
from tutorgpt import TutorGPT

st.set_page_config(page_title="Courses & Study Materials – StudySync", page_icon="📚", layout="wide")
apply_theme()
current_user = require_auth()

if "tutor" not in st.session_state:
    st.session_state.tutor = TutorGPT()
if "revision" not in st.session_state:
    st.session_state.revision = RevisionGPT()
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

COURSE_METADATA = {
    "dbms_transactions.txt": {
        "title": "Database Management Systems: Transactions & Concurrency Control",
        "category": "Computer Science",
        "level": "Intermediate",
        "read_time": "15 min read",
        "summary": "Covers ACID properties, write-ahead logging, conflict serializability, 2PL protocol, and relational normal forms (1NF to BCNF).",
        "video_title": "Lecture 04: ACID Guarantees and Two-Phase Locking (2PL)",
        "instructor": "Dr. Sarah Chen, Dept of Computer Science"
    },
    "os_process_synchronization.txt": {
        "title": "Operating Systems: Process Synchronization & Deadlocks",
        "category": "Systems Engineering",
        "level": "Intermediate",
        "read_time": "18 min read",
        "summary": "Covers race conditions, semaphores, Coffman deadlock conditions, Banker's algorithm, and CPU scheduling algorithms (SJF, Round Robin).",
        "video_title": "Lecture 07: Critical Sections, Mutex Semaphores & Deadlock Coffman Conditions",
        "instructor": "Prof. David Miller, Systems Architecture"
    },
    "dsa_dynamic_programming.txt": {
        "title": "Algorithms: Dynamic Programming & Graph Traversal",
        "category": "Algorithms",
        "level": "Advanced",
        "read_time": "20 min read",
        "summary": "Covers optimal substructure, overlapping subproblems, memoization vs tabulation, knapsack, LCS, Dijkstra's and Bellman-Ford algorithms.",
        "video_title": "Lecture 12: Dynamic Programming Patterns & Shortest Paths",
        "instructor": "Prof. Alan Turing Institute"
    }
}

# =============================================================================
# VIEW 1: DEDICATED STUDY MATERIAL READER (When a material is opened)
# =============================================================================
if st.session_state.selected_course is not None:
    course_key = st.session_state.selected_course
    meta = COURSE_METADATA.get(course_key, {
        "title": course_key.replace(".txt", "").replace("_", " ").title(),
        "category": "Curriculum Material",
        "level": "All Levels",
        "read_time": "12 min read",
        "summary": "Uploaded academic notes and lecture transcript.",
        "video_title": "Course Lecture & Audio Visual Breakdown",
        "instructor": "Course Faculty"
    })
    content = SAMPLE_MATERIALS.get(course_key, "No study material found.")

    # Top Breadcrumb & Back Navigation
    col_nav1, col_nav2 = st.columns([2, 8])
    with col_nav1:
        if st.button("← Back to Course Library", key="btn_back_lib", type="secondary"):
            st.session_state.selected_course = None
            st.rerun()

    st.markdown(
        f"""
        <div style="margin-top: 10px; margin-bottom: 20px;">
            <span class="badge-blue">{meta['category']}</span>
            <span class="badge-green">{meta['level']}</span>
            <span style="color: #64748B; font-size: 0.85rem; font-weight: 600;">⏱️ {meta['read_time']} • 👤 {meta['instructor']}</span>
            <h1 style="color: #14382C; margin-top: 8px; margin-bottom: 4px; font-size: 2.2rem; font-weight: 800;">{meta['title']}</h1>
            <p style="color: #475569; font-size: 1.05rem;">{meta['summary']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2-Column Coursera / Udemy Layout
    left_col, right_col = st.columns([7, 4])

    with left_col:
        # Video Simulation Player Theater
        st.markdown(
            f"""
            <div class="video-theater">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; color: #FFFFFF;">
                        ▶️ VIDEO LECTURE STREAM
                    </span>
                    <span style="font-size: 0.8rem; color: #94A3B8;">1080p Full HD • Audio Synced</span>
                </div>
                <h3 style="color: #FFFFFF; margin-top: 0; margin-bottom: 8px;">{meta['video_title']}</h3>
                <div style="background: #1E293B; border-radius: 8px; height: 160px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 4px;">▶️</div>
                        <div style="font-size: 0.85rem; color: #94A3B8;">Click to simulate video playback • 14:28 / 22:50</div>
                    </div>
                </div>
                <div style="background: #334155; border-radius: 4px; height: 5px; width: 100%; overflow: hidden;">
                    <div style="background: #38BDF8; height: 100%; width: 62%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tabbed Workspace
        tab_notes, tab_qna, tab_fc = st.tabs(["📄 Full Lecture Notes", "🤖 Ask AI Tutor (Grounded)", "🧠 Active Flashcards"])

        with tab_notes:
            st.markdown('<div class="reader-container">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_qna:
            st.markdown("### 🤖 Ask AI Tutor About This Lecture")
            st.caption("Answers are strictly grounded in this lecture with verified source citations.")
            q_in = st.text_input("Ask a question about this material:", "Explain the key rules or properties mentioned here.", key="tab_q_in")
            if st.button("Submit Question", type="primary", key="btn_tab_q_sub"):
                with st.spinner("AI Tutor is analyzing this lecture..."):
                    resp = st.session_state.tutor.answer_with_rag(q_in, top_k=2)
                    st.info(resp.answer)
                    if resp.citations:
                        st.caption(f"Cited from: {resp.citations[0].source_name} (Chunk #{resp.citations[0].chunk_id})")

        with tab_fc:
            st.markdown("### 🧠 Instant Flashcard Generator")
            st.caption("Generate high-yield cards from this reading material and add them to your SM-2 deck.")
            if st.button("Generate Cards from This Lecture", type="primary", key="btn_tab_fc"):
                with st.spinner("Extracting atomic concepts..."):
                    cards = st.session_state.revision.generate_flashcards(meta['title'], context=content[:4000], count=3)
                    st.success(f"Added {len(cards)} flashcards to your active Spaced Repetition deck!")
                    for c in cards:
                        with st.expander(f"Q: {c.front}"):
                            st.write(f"**A**: {c.back}")
                            if c.hint:
                                st.caption(f"Hint: {c.hint}")

    with right_col:
        # Interactive Study Sidebar Actions
        st.markdown(
            """
            <div class="study-card">
                <span class="badge-green">Lecture Actions</span>
                <h4 style="color: #14382C; margin-top: 8px;">Study Tools</h4>
                <p style="font-size: 0.88rem; color: #64748B;">Access quick learning checks and active recall tools for this lecture.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Knowledge Check Quiz Card
        st.markdown("#### 📝 Knowledge Check")
        st.caption("Take a quick 2-minute quiz to verify understanding.")
        if st.button("Generate Lecture Quiz", key="btn_gen_quiz", type="primary", use_container_width=True):
            with st.spinner("Compiling test questions..."):
                test = generate_test(topic=meta['title'][:40], difficulty="medium", n_mcq=2, n_desc=0, context=content[:4000])
                st.session_state.lecture_test = test

        if "lecture_test" in st.session_state:
            lt = st.session_state.lecture_test
            for i, q in enumerate(lt.mcqs):
                st.write(f"**Q{i+1}: {q.question}**")
                choice = st.radio(f"Select option {i+1}:", q.options, key=f"lt_q_{i}")
                if st.button(f"Submit Answer {i+1}", key=f"btn_lt_{i}"):
                    if q.options.index(choice) == q.answer_index:
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect.")
                        st.info(f"Explanation: {q.explanation}")

# =============================================================================
# VIEW 2: COURSE & STUDY MATERIAL CATALOG (Grid View)
# =============================================================================
else:
    render_header(
        title="Courses & Study Materials",
        subtitle="Explore your curriculum, lecture slides, and notes. Click any material to open the interactive lecture view.",
        badge="Curriculum Library"
    )

    st.markdown("### 📖 Available Course Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">DBMS</span>
                <span class="badge-green">Core Module</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Transactions & Concurrency Control</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 60px;">
                    ACID Properties, Conflict Serializability, Precedence Graphs, Two-Phase Locking, and Normalization (1NF, 2NF, 3NF, BCNF).
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⏱️ 15 min read • 📹 Video Stream • 12 Topics
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Lecture Material", key="cat_btn_dbms", type="primary", use_container_width=True):
            st.session_state.selected_course = "dbms_transactions.txt"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">OS</span>
                <span class="badge-green">Core Module</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Process Synchronization & Deadlocks</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 60px;">
                    Critical-Section Problem, Counting/Binary Semaphores, Coffman Deadlock Conditions, Banker's Algorithm, and CPU Scheduling.
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⏱️ 18 min read • 📹 Video Stream • 10 Topics
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Lecture Material", key="cat_btn_os", type="primary", use_container_width=True):
            st.session_state.selected_course = "os_process_synchronization.txt"
            st.rerun()

    with col3:
        st.markdown(
            """
            <div class="course-card">
                <div class="card-strip"></div>
                <span class="badge-blue">Algorithms</span>
                <span class="badge-green">Advanced Module</span>
                <h3 style="color: #14382C; margin-top: 12px; margin-bottom: 6px;">Dynamic Programming & Graphs</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; min-height: 60px;">
                    Optimal Substructure, Memoization vs Tabulation, 0/1 Knapsack, Longest Common Subsequence, Dijkstra's & Bellman-Ford.
                </p>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 12px;">
                    ⏱️ 20 min read • 📹 Video Stream • 14 Topics
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Lecture Material", key="cat_btn_dsa", type="primary", use_container_width=True):
            st.session_state.selected_course = "dsa_dynamic_programming.txt"
            st.rerun()

    # Dynamic Section for Any User-Uploaded Files
    user_courses = [k for k in SAMPLE_MATERIALS.keys() if k not in COURSE_METADATA]
    if user_courses:
        st.write("")
        st.markdown("### 📁 Your Uploaded Documents & Notes")
        cols_uc = st.columns(3)
        for idx, uckey in enumerate(user_courses):
            with cols_uc[idx % 3]:
                st.markdown(
                    f"""
                    <div class="course-card">
                        <div class="card-strip"></div>
                        <span class="badge-blue">Uploaded Note</span>
                        <span class="badge-green">Custom</span>
                        <h4 style="color: #14382C; margin-top: 10px;">{uckey}</h4>
                        <p style="color: #64748B; font-size: 0.85rem;">Indexed into your personal AI knowledge base.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"Read {uckey}", key=f"btn_uc_{idx}", type="secondary", use_container_width=True):
                    st.session_state.selected_course = uckey
                    st.rerun()

    st.write("")
    st.markdown("### 📤 Upload Your Own Notes & Slides")
    st.caption("Supported formats: PDF (.pdf), Word (.docx, .doc), PowerPoint (.pptx, .ppt), Markdown (.md), and Text (.txt).")

    with st.expander("Upload Study Materials (PDF, DOCX, PPTX, MD, TXT)", expanded=False):
        uploaded_files = st.file_uploader(
            "Select files from your device:",
            type=["pdf", "docx", "doc", "pptx", "ppt", "txt", "md"],
            accept_multiple_files=True,
            key="cat_multi_uploader"
        )
        if uploaded_files:
            for uf in uploaded_files:
                file_bytes = uf.read()
                try:
                    extracted_text = parse_uploaded_file(uf.name, file_bytes)
                    chunks = st.session_state.tutor.ingest_material(extracted_text, uf.name)
                    SAMPLE_MATERIALS[uf.name] = extracted_text
                    st.success(f"✅ Successfully ingested **{uf.name}**: Extracted {len(extracted_text.split())} words and indexed {chunks} semantic chunks!")
                except Exception as e:
                    st.error(f"❌ Failed to parse {uf.name}: {e}")
