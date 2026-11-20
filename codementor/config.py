"""Runtime configuration for CodeMentor AI."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5-5",
    "openai": "gpt-4o-mini",
}


@dataclass
class Settings:
    provider: str
    model: str
    api_key: str | None
    exec_timeout: float
    max_output_chars: int
    max_tokens: int


def get_settings() -> Settings:
    provider = os.getenv("CODEMENTOR_PROVIDER", "").lower()
    if not provider:
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "offline"

    key_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
    return Settings(
        provider=provider,
        model=os.getenv("CODEMENTOR_MODEL") or DEFAULT_MODELS.get(provider, "intelligent-offline-v1"),
        api_key=os.getenv(key_var),
        exec_timeout=float(os.getenv("CODEMENTOR_EXEC_TIMEOUT", "5")),
        max_output_chars=int(os.getenv("CODEMENTOR_MAX_OUTPUT_CHARS", "10000")),
        max_tokens=int(os.getenv("CODEMENTOR_MAX_TOKENS", "3000")),
    )
