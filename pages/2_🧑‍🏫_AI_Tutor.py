"""
StudySync – AI Academic Tutor & Professor.
Provides step-by-step concept explanations, difficulty calibration,
grounded RAG answering over course materials, and Socratic dialogues.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from shared.auth import require_auth
from shared.styles import apply_theme, render_header
from tutorgpt import DifficultyLevel, TutorGPT

st.set_page_config(page_title="AI Tutor – StudySync", page_icon="🧑‍🏫", layout="wide")
apply_theme()
current_user = require_auth()

if "tutor" not in st.session_state:
    st.session_state.tutor = TutorGPT()

render_header(
    title="AI Academic Tutor",
    subtitle="Personalized, step-by-step concept instruction calibrated to your level, backed by grounded textbook retrieval.",
    badge="Smart Teaching Assistant"
)

tutor_mode = st.radio(
    "Choose Learning Mode:",
    ["Concept Explainer & Deep Dive", "RAG Q&A (Ask Uploaded Materials)", "Socratic Inquiry Practice"],
    horizontal=True
)

st.write("")

# Mode 1: Concept Explainer
if tutor_mode == "Concept Explainer & Deep Dive":
    c1, c2 = st.columns([3, 1])
    with c1:
        concept_input = st.text_input("Enter academic concept or topic to learn:", "Two-Phase Locking (2PL)")
    with c2:
        diff_level = st.selectbox(
            "Difficulty Calibration:",
            ["Beginner", "Intermediate", "Advanced"],
            index=1,
            help="Beginner = analogies & intuition. Intermediate = university textbook rigor. Advanced = formal proofs & system trade-offs."
        )

    level_map = {
        "Beginner": DifficultyLevel.BEGINNER,
        "Intermediate": DifficultyLevel.INTERMEDIATE,
        "Advanced": DifficultyLevel.ADVANCED
    }

    if st.button("Generate Explanation", type="primary"):
        with st.spinner("AI Tutor is preparing structured, step-by-step breakdown..."):
            exp = st.session_state.tutor.explain_concept(concept_input, difficulty=level_map[diff_level])
            st.markdown('<div class="reader-container">', unsafe_allow_html=True)
            st.markdown(exp.full_markdown)
            st.markdown('</div>', unsafe_allow_html=True)

# Mode 2: RAG Q&A over materials
elif tutor_mode == "RAG Q&A (Ask Uploaded Materials)":
    sources = st.session_state.tutor.get_indexed_sources()
    st.info(f"📚 **Indexed Knowledge Base**: {sources['sources_count']} active documents | {sources['total_chunks']} indexed chunks")

    query = st.text_input("Ask a question about the course materials:", "What are the four Coffman conditions for a deadlock?")
    top_k = st.slider("Context chunks to retrieve:", 1, 5, 3)

    if st.button("Search & Answer with Sources", type="primary"):
        with st.spinner("Retrieving semantic passages and formulating grounded answer..."):
            ans = st.session_state.tutor.answer_with_rag(query, top_k=top_k)
            st.markdown('<div class="reader-container">', unsafe_allow_html=True)
            st.markdown("### Answer")
            st.markdown(ans.answer)
            st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🔍 Verified Source Citations")
            if ans.citations:
                for c in ans.citations:
                    with st.expander(f"📌 {c.source_name} (Chunk #{c.chunk_id} • Similarity: {c.score:.2f})"):
                        st.write(c.text)
            else:
                st.warning("No relevant passages found in the uploaded documents.")

# Mode 3: Socratic Dialogue
else:
    st.markdown("### 🤔 Socratic Discovery Mode")
    st.caption("The AI Tutor asks guided questions and offers hints instead of immediately revealing the answer.")

    socr_concept = st.text_input("Concept to practice:", "Dynamic Programming Memoization vs Tabulation")
    user_thought = st.text_area("Your response or current reasoning:", "I know memoization is recursive, but why does tabulation use less call stack memory?")

    if st.button("Submit to Tutor", type="primary"):
        with st.spinner("Evaluating your reasoning..."):
            socr = st.session_state.tutor.socratic_guide(socr_concept, user_thought)
            st.markdown(
                f"""
                <div class="study-card">
                    <h4 style="color: #1B4D3E;">Tutor Evaluation</h4>
                    <p style="color: #1E293B;">{socr.tutor_feedback}</p>
                    {f'<div style="background: #FFFBEB; border-left: 4px solid #F59E0B; padding: 10px; margin: 10px 0;"><strong>💡 Hint:</strong> {socr.hint}</div>' if socr.hint else ''}
                    <div style="background: #EAF3EE; border-left: 4px solid #1B4D3E; padding: 10px; margin: 10px 0;">
                        <strong>❓ Question for you:</strong> {socr.probing_question}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
