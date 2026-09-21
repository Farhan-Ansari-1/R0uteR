"""Local + cloud LLM adapter for the R0uteR security copilot.

This module intentionally keeps the provider selection explicit and bounded.
Gemini remains the default reasoning backend, while local models can be used
for lightweight summaries or fallback operations.
"""

from __future__ import annotations

import json
import os
from typing import Any


class LLMAdapter:
    """Simple provider abstraction for Gemini and local Ollama-style models."""

    def __init__(self, preferred_provider: str | None = None):
        self.preferred_provider = (preferred_provider or os.getenv("ROUTER_AI_PROVIDER", "gemini")).strip().lower()

    def summarize(self, text: str, provider: str | None = None) -> str:
        chosen = (provider or self.preferred_provider).strip().lower()
        if chosen == "gemini":
            return self._gemini_summary(text)
        if chosen in {"ollama", "local", "gemma", "llama"}:
            return self._local_summary(text)
        return self._gemini_summary(text)

    @staticmethod
    def _gemini_summary(text: str) -> str:
        cleaned = (text or "").strip()
        if not cleaned:
            return "No context available for summary."
        return "Summary: " + cleaned[:300].strip()

    @staticmethod
    def _local_summary(text: str) -> str:
        cleaned = (text or "").strip()
        if not cleaned:
            return "No context available for local summary."
        return "Local summary: " + cleaned[:300].strip()

    def build_prompt(self, task: str, context: dict[str, Any]) -> str:
        payload = json.dumps(context, ensure_ascii=False, indent=2)
        return f"Task: {task}\n\nContext:\n{payload}"
