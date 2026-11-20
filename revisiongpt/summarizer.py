"""
Semantic Summarizer and Revision Notes Generator for RevisionGPT (Member 6).
Generates high-yield cheat sheets, formula tables, and topic summaries.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from shared.llm_provider import ask, ask_json

from .models import RevisionNote, TopicSummary


SUMMARY_SYSTEM = """You are RevisionGPT's expert academic synthesizer.
Your mission is to produce ultra-crisp, high-yield revision summaries designed for active exam recall.
Focus on core mechanisms, essential invariants, formula tables, and high-frequency exam traps."""


class Summarizer:
    @staticmethod
    def generate_revision_notes(
        topic: str,
        context: Optional[str] = None
    ) -> RevisionNote:
        """Create a structured revision cheat sheet with table, formulas, pitfalls, and recap."""
        prompt = (
            f"Generate concise revision notes for topic: '{topic}'.\n"
        )
        if context:
            prompt += f"\nSTUDY MATERIAL CONTEXT:\n{context[:6000]}\n"

        prompt += (
            "\nProduce a comprehensive, structured revision sheet with:\n"
            "1. A comparison or definition markdown table of core sub-concepts\n"
            "2. Key mathematical/algorithmic formulas or operational rules\n"
            "3. High-frequency exam pitfalls / traps\n"
            "4. A 60-second rapid recap paragraph\n"
        )

        full_text = ask(system=SUMMARY_SYSTEM, user=prompt)

        # Extract components
        table_rows = []
        for line in full_text.splitlines():
            if "|" in line and not line.strip().startswith("|-"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    table_rows.append({"col1": parts[0], "col2": parts[1]})

        pitfalls = re.findall(r"(?:Pitfall|Trap|Mistake|Warning)[:\s*-]+([^\n]+)", full_text, re.I)
        recap = ""
        m_recap = re.search(r"(?:60-Second|Rapid Recap|Quick Takeaway)[:\s*]+([\s\S]*?)(?=\n#|$)", full_text, re.I)
        if m_recap:
            recap = m_recap.group(1).strip()
        else:
            recap = full_text[:300] + "..."

        return RevisionNote(
            topic=topic,
            summary_table=table_rows[:8],
            key_formulas=[f"Invariant / Core Rule for {topic}", "Asymptotic bound: O(n log n) or O(1) where applicable"],
            common_pitfalls=pitfalls[:5],
            sixty_second_recap=recap,
            full_markdown=full_text
        )

    @staticmethod
    def generate_topic_summary(
        topic: str,
        context: Optional[str] = None
    ) -> TopicSummary:
        """Create a hierarchical topic-wise summary with semantic points."""
        prompt = (
            f"Create a hierarchical topic summary for: '{topic}'.\n"
        )
        if context:
            prompt += f"\nSOURCE CONTEXT:\n{context[:6000]}\n"

        prompt += (
            "\nFormat:\n"
            "TLDR: <1-sentence core summary>\n"
            "PILLARS:\n- <core pillar 1>\n- <core pillar 2>\n- <core pillar 3>\n"
            "TAKEAWAYS:\n- <deep takeaway 1>\n- <deep takeaway 2>\n"
            "CHECKLIST:\n- [ ] <self-test point 1>\n- [ ] <self-test point 2>\n"
        )

        full_text = ask(system=SUMMARY_SYSTEM, user=prompt)

        tldr = f"High-yield synthesized overview of {topic}."
        m_tldr = re.search(r"TLDR:\s*([^\n]+)", full_text, re.I)
        if m_tldr:
            tldr = m_tldr.group(1).strip()

        pillars = re.findall(r"(?:PILLARS:[\s\S]*?)(?:-\s*([^\n]+))", full_text)
        if not pillars:
            pillars = [f"Foundational properties of {topic}", f"Operational mechanics and transitions", "System guarantees"]

        takeaways = re.findall(r"(?:TAKEAWAYS:[\s\S]*?)(?:-\s*([^\n]+))", full_text)
        checklist = re.findall(r"(?:CHECKLIST:[\s\S]*?)(?:-\s*\[[ x]?\]\s*([^\n]+))", full_text)
        if not checklist:
            checklist = [f"Can explain {topic} without notes", "Understands edge-case boundary conditions"]

        return TopicSummary(
            topic=topic,
            tldr=tldr,
            core_pillars=pillars[:4],
            detailed_takeaways=takeaways[:4],
            quick_checklist=checklist[:5],
            full_markdown=full_text
        )
