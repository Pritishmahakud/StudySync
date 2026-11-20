"""
TutorGPT Agent Core (Member 1).
Full AI Teaching Agent supporting multi-level concept explanations,
RAG retrieval with source citations, and Socratic dialogues.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared.event_bus import get_event_bus
from shared.llm_provider import ask, get_llm_provider

from .models import (
    DifficultyLevel,
    DocumentChunk,
    RAGResponse,
    SocraticResponse,
    TutorExplanation,
)
from .prompts import (
    DIFFICULTY_INSTRUCTIONS,
    RAG_SYSTEM,
    SOCRATIC_SYSTEM,
    TUTOR_SYSTEM,
)
from .rag import RAGEngine


class TutorGPT:
    """
    Member 1: AI Teaching Agent
    - Explains complex academic concepts
    - Provides step-by-step explanations
    - Supports Beginner, Intermediate, and Advanced difficulty levels
    - Uses RAG to answer from uploaded study materials with strict source citations
    - Features Socratic guided learning mode
    """

    def __init__(self, rag_engine: Optional[RAGEngine] = None):
        self.rag = rag_engine or RAGEngine()
        self.event_bus = get_event_bus()

    # -------------------------------------------------------------------------
    # 1. Academic Concept Explainer with Difficulty Levels
    # -------------------------------------------------------------------------
    def explain_concept(
        self,
        concept: str,
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        additional_context: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> TutorExplanation:
        """
        Generate a comprehensive, pedagogically scaffolded explanation
        tailored to the requested difficulty level.
        """
        system = TUTOR_SYSTEM + "\n" + DIFFICULTY_INSTRUCTIONS.get(
            difficulty, DIFFICULTY_INSTRUCTIONS[DifficultyLevel.INTERMEDIATE]
        )

        user_prompt = f"Please explain the academic concept: '{concept}' in detail."
        if additional_context:
            user_prompt += f"\n\nAdditional Context / Focus Area:\n{additional_context}"

        response_text = ask(system=system, user=user_prompt)

        # Parse structured components from the response
        explanation = self._parse_explanation(concept, difficulty, response_text)

        # Log event if student_id is provided
        if student_id:
            self.event_bus.log_event(
                event_type="concept_explained",
                student_id=student_id,
                payload={"concept": concept, "difficulty": difficulty.value},
                source_agent="TutorGPT"
            )

        return explanation

    def _parse_explanation(
        self,
        concept: str,
        difficulty: DifficultyLevel,
        text: str
    ) -> TutorExplanation:
        """Extract structured sections from generated markdown."""
        analogy = None
        example = None
        check_q = None
        steps = []
        misconceptions = []

        # Find analogy
        m_analogy = re.search(r"(?:Analogy|Intuition)[^\n]*\n([\s\S]*?)(?=\n[#*]|Step|$)", text, re.I)
        if m_analogy:
            analogy = m_analogy.group(1).strip()

        # Find steps
        m_steps = re.findall(r"(?:Step\s*\d+|^\d+\.)[:\s]+([^\n]+)", text, re.M)
        if m_steps:
            steps = [s.strip() for s in m_steps]

        # Find example
        m_ex = re.search(r"(?:Example|Practical Example)[^\n]*\n([\s\S]*?)(?=\n[#*]|Common|$)", text, re.I)
        if m_ex:
            example = m_ex.group(1).strip()

        # Find check question
        m_check = re.search(r"(?:Quick Check|Self-Check|Question for You)[^\n]*\n?([^\n]+)", text, re.I)
        if m_check:
            check_q = m_check.group(1).strip()

        return TutorExplanation(
            concept=concept,
            difficulty=difficulty,
            analogy=analogy,
            core_definition=text.split("\n\n")[0],
            step_by_step=steps,
            practical_example=example,
            common_misconceptions=misconceptions,
            socratic_check_question=check_q,
            full_markdown=text
        )

    # -------------------------------------------------------------------------
    # 2. RAG Answering from Uploaded Study Materials
    # -------------------------------------------------------------------------
    def answer_with_rag(
        self,
        query: str,
        top_k: int = 3,
        strict_grounding: bool = False,
        student_id: Optional[str] = None
    ) -> RAGResponse:
        """
        Search uploaded study materials and answer using grounded context and citations.
        """
        # Retrieve relevant chunks from the RAG vector index
        chunks = self.rag.retrieve(query, top_k=top_k)
        has_citations = len(chunks) > 0

        if not has_citations and strict_grounding:
            return RAGResponse(
                query=query,
                answer="No relevant content found in the uploaded study materials. Please upload matching notes or textbooks to enable grounded RAG answering.",
                citations=[],
                grounded_in_material=False,
                confidence_score=0.0
            )

        context_block = self.rag.format_context_for_prompt(chunks)

        user_prompt = (
            f"STUDENT QUESTION: {query}\n\n"
            f"STUDY MATERIAL EXCERPTS:\n{context_block}\n\n"
            f"Please answer the student's question thoroughly, citing the exact sources using [Source: filename, Chunk #id]."
        )

        answer_text = ask(system=RAG_SYSTEM, user=user_prompt)

        avg_score = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0

        if student_id:
            self.event_bus.log_event(
                event_type="rag_query",
                student_id=student_id,
                payload={"query": query, "chunks_found": len(chunks), "avg_relevance": avg_score},
                source_agent="TutorGPT"
            )

        return RAGResponse(
            query=query,
            answer=answer_text,
            citations=chunks,
            grounded_in_material=has_citations,
            confidence_score=round(avg_score, 3)
        )

    # -------------------------------------------------------------------------
    # 3. Socratic Dialogue Mode
    # -------------------------------------------------------------------------
    def socratic_guide(
        self,
        concept: str,
        student_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        student_id: Optional[str] = None
    ) -> SocraticResponse:
        """
        Guide a student to understand a concept through hints and questions.
        """
        history_text = ""
        if conversation_history:
            history_text = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in conversation_history])

        prompt = (
            f"TARGET CONCEPT: {concept}\n"
            f"CONVERSATION SO FAR:\n{history_text}\n\n"
            f"STUDENT LATEST MESSAGE:\n\"{student_message}\"\n\n"
            f"Provide your response formatted as:\n"
            f"FEEDBACK: <warm recognition of what is right or wrong>\n"
            f"HINT: <conceptual clue or analogy>\n"
            f"QUESTION: <one probing question to lead them forward>\n"
            f"MASTERY: <YES if student demonstrated solid understanding, otherwise NO>"
        )

        reply = ask(system=SOCRATIC_SYSTEM, user=prompt)

        # Parse reply
        feedback = "Good attempt! Let's examine the next piece."
        hint = None
        question = "What happens next in this scenario?"
        mastery = False

        m_fb = re.search(r"FEEDBACK:\s*([^\n]+)", reply)
        if m_fb:
            feedback = m_fb.group(1).strip()
        m_hint = re.search(r"HINT:\s*([^\n]+)", reply)
        if m_hint:
            hint = m_hint.group(1).strip()
        m_q = re.search(r"QUESTION:\s*([^\n]+)", reply)
        if m_q:
            question = m_q.group(1).strip()
        if "MASTERY: YES" in reply.upper():
            mastery = True

        if student_id:
            self.event_bus.log_event(
                event_type="socratic_interaction",
                student_id=student_id,
                payload={"concept": concept, "mastery": mastery},
                source_agent="TutorGPT"
            )

        return SocraticResponse(
            student_message=student_message,
            tutor_feedback=feedback,
            probing_question=question,
            hint=hint,
            mastery_achieved=mastery
        )

    # -------------------------------------------------------------------------
    # 4. Knowledge Ingestion Helpers
    # -------------------------------------------------------------------------
    def ingest_material(self, text: str, source_name: str) -> int:
        return self.rag.ingest_text(text, source_name)

    def ingest_file(self, file_path: str | Path) -> int:
        return self.rag.ingest_file(file_path)

    def ingest_directory(self, dir_path: str | Path) -> int:
        return self.rag.ingest_directory(dir_path)

    def get_indexed_sources(self) -> Dict[str, Any]:
        return {
            "sources": self.rag.sources,
            "total_chunks": len(self.rag.chunks),
            "sources_count": len(self.rag.sources)
        }
