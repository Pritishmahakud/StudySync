"""Thin LLM abstraction for CodeMentor AI, routed via StudySync shared provider."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

from shared.llm_provider import ask, ask_json, get_llm_provider
from .config import Settings, get_settings


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 3000, temperature: float = 0.2) -> str:
        """Return the model's text reply."""


class UniversalAdapterClient(LLMClient):
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def complete(self, system: str, user: str, max_tokens: int = 3000, temperature: float = 0.2) -> str:
        return ask(system=system, user=user, max_tokens=max_tokens, temperature=temperature)


def build_llm(settings: Settings | None = None) -> LLMClient:
    return UniversalAdapterClient(settings)


def extract_json(text: str) -> dict:
    """Robustly parse JSON object from LLM response text."""
    text = text.strip()
    # Strip markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback regex search
        m = re.search(r"(\{.*\})", text, re.DOTALL)
        if m:
            return json.loads(m.group(1))
        raise
