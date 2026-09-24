"""Local + cloud LLM adapter for the R0uteR security copilot.

This module intentionally keeps the provider selection explicit and bounded.
Gemini remains the default reasoning backend, while local models can be used
for lightweight summaries or fallback operations.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any


class LLMAdapter:
    """Simple provider abstraction for Gemini and local Ollama-style models."""

    def __init__(self, preferred_provider: str | None = None):
        self.preferred_provider = (preferred_provider or os.getenv("ROUTER_AI_PROVIDER", "gemini")).strip().lower()

    def summarize(self, text: str, provider: str | None = None) -> str:
        chosen = (provider or self.preferred_provider).strip().lower()
        if chosen == "hybrid":
            return self._hybrid_summary(text)
        if chosen == "gemini":
            return self._gemini_summary(text)
        if chosen in {"ollama", "local", "gemma", "llama"}:
            return self._local_summary(text)
        return self._gemini_summary(text)

    def _hybrid_summary(self, text: str) -> str:
        gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if gemini_key:
            try:
                return self._gemini_summary(text)
            except Exception:
                pass
        try:
            return self._local_summary(text)
        except Exception:
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
        endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat").strip()
        model = os.getenv("OLLAMA_MODEL", "gemma4:e4b").strip()
        timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are R0uteR's local reporting assistant. Summarize only the supplied "
                        "authorized security evidence. Do not invent findings and do not execute commands."
                    ),
                },
                {"role": "user", "content": cleaned},
            ],
            "stream": False,
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
            content = result.get("message", {}).get("content", "").strip()
            return content or "Local model returned an empty summary."
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            return f"Local model unavailable ({error}); raw evidence retained: {cleaned[:300]}"

    def build_prompt(self, task: str, context: dict[str, Any]) -> str:
        payload = json.dumps(context, ensure_ascii=False, indent=2)
        return f"Task: {task}\n\nContext:\n{payload}"
