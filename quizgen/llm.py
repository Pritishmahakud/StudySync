"""
LLM abstraction for QuizGen AI (Member 2), routed via StudySync shared provider.
"""

from shared.llm_provider import ask, ask_json

__all__ = ["ask", "ask_json"]
