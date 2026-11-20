"""
StudySync – Active Recall & Spaced Repetition (SuperMemo SM-2).
Generates high-yield flashcards, manages daily review schedules with the SM-2 algorithm,
and synthesizes concise revision notes and cheat sheets.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from revisiongpt import RevisionGPT
from shared.auth import require_auth
from shared.styles import apply_theme, render_header

st.set_page_config(page_title="Flashcards & Revision – StudySync", page_icon="🧠", layout="wide")
apply_theme()
current_user = require_auth()

if "revision" not in st.session_state:
    st.session_state.revision = RevisionGPT()

render_header(
    title="Active Recall & Spaced Repetition",
    subtitle="Optimize memory retention using the scientifically validated SuperMemo SM-2 algorithm and concise revision cheat-sheets.",
    badge="Retention Engine"
)

sub_mode = st.radio(
    "Choose Revision Tool:",
    ["Daily SM-2 Spaced Repetition Session", "Generate New Flashcards", "Concise Revision Cheat Sheets", "Hierarchical Topic Summaries"],
    horizontal=True
)

st.write("")

# Tool 1: Daily SM-2 Flashcard Session
if sub_mode == "Daily SM-2 Spaced Repetition Session":
    stats = st.session_state.revision.get_deck_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{stats["total_cards"]}</div><div class="metric-lbl">TOTAL FLASHCARDS</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{stats["due_today"]}</div><div class="metric-lbl">CARDS DUE TODAY</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{stats["retention_rate"]}%</div><div class="metric-lbl">RETENTION RATE</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{stats["avg_easiness_factor"]}</div><div class="metric-lbl">AVG EASINESS FACTOR</div></div>', unsafe_allow_html=True)

    st.write("")
    due_cards = st.session_state.revision.get_due_cards()

    if not due_cards:
        st.success("🎉 You are completely caught up! No cards currently due for review today.")
    else:
        st.markdown(f"### 🗂️ Active Review: Card 1 of {len(due_cards)}")
        current_card = due_cards[0]

        st.markdown(
            f"""
            <div class="study-card" style="border-left: 6px solid #1B4D3E; min-height: 140px;">
                <span class="badge-blue">{current_card.difficulty.upper()}</span>
                <span class="badge-green">Repetitions: {current_card.repetition}</span>
                <h3 style="color: #1B4D3E; margin-top: 10px;">{current_card.front}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if current_card.hint:
            with st.expander("💡 Show Recall Hint"):
                st.info(f"Hint: {current_card.hint}")

        show_back = st.checkbox("Flip Card (Show Answer)")
        if show_back:
            st.markdown(
                f"""
                <div class="study-card" style="background: #F8FAFC; border: 1px solid #CBD5E1;">
                    <span class="badge-green">Authoritative Answer</span>
                    <h4 style="color: #0F172A; margin-top: 8px;">{current_card.back}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### Rate your recall quality:")
            st.caption("SM-2 uses this rating to calculate the next optimal review interval in days.")
            col_rates = st.columns(6)
            ratings = [
                ("0: Blackout", 0),
                ("1: Wrong", 1),
                ("2: Near Miss", 2),
                ("3: Hard", 3),
                ("4: Good", 4),
                ("5: Perfect", 5)
            ]
            for idx, (label, val) in enumerate(ratings):
                if col_rates[idx].button(label, key=f"btn_rate_{val}"):
                    updated = st.session_state.revision.review_card(current_card.id, val, student_id="Asha")
                    st.toast(f"SM-2 Updated: Next review in {updated.interval} day(s) (EF: {updated.easiness_factor:.2f})")
                    st.rerun()

# Tool 2: Generate Flashcards
elif sub_mode == "Generate New Flashcards":
    c_top, c_cnt = st.columns([3, 1])
    with c_top:
        topic_input = st.text_input("Enter Topic for Flashcard Deck:", "ACID Database Transactions")
    with c_cnt:
        count_input = st.number_input("Number of Cards:", min_value=1, max_value=8, value=3)

    if st.button("Generate Flashcard Deck", type="primary"):
        with st.spinner("Extracting atomic definitions, formulas, and contrast pairs..."):
            cards = st.session_state.revision.generate_flashcards(topic_input, count=count_input, student_id="Asha")
            st.success(f"Generated {len(cards)} cards! Added to your active review deck.")
            for c in cards:
                with st.expander(f"📌 {c.front}"):
                    st.write(f"**Answer**: {c.back}")
                    if c.hint:
                        st.caption(f"Hint: {c.hint}")

# Tool 3: Concise Revision Cheat Sheets
elif sub_mode == "Concise Revision Cheat Sheets":
    sheet_topic = st.text_input("Enter Topic for Cheat Sheet:", "Two-Phase Locking (2PL)")
    if st.button("Synthesize High-Yield Notes", type="primary"):
        with st.spinner("Synthesizing comparison tables, invariant rules, and pitfalls..."):
            notes = st.session_state.revision.generate_revision_notes(sheet_topic)
            st.markdown('<div class="reader-container">', unsafe_allow_html=True)
            st.markdown(notes.full_markdown)
            st.markdown('</div>', unsafe_allow_html=True)

# Tool 4: Topic Summaries
else:
    sum_topic = st.text_input("Enter Topic for Hierarchical Summary:", "Coffman Deadlock Conditions")
    if st.button("Generate Topic Summary", type="primary"):
        with st.spinner("Generating multi-level hierarchical overview..."):
            sm = st.session_state.revision.generate_topic_summary(sum_topic)
            st.markdown(
                f"""
                <div class="study-card">
                    <span class="badge-blue">1-Sentence TL;DR</span>
                    <h3 style="color: #1B4D3E; margin-top: 8px;">{sm.tldr}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("#### Core Pillars")
            for p in sm.core_pillars:
                st.write(f"- **{p}**")
            st.markdown("#### Self-Check Recall Checklist")
            for cl in sm.quick_checklist:
                st.checkbox(cl, key=f"chk_{cl[:20]}")
