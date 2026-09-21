"""Configuration for the currently selected R0uteR AI provider."""

import os
import platform

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
AI_PROVIDER = os.getenv("ROUTER_AI_PROVIDER", "gemini").strip().lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
CURRENT_OS = platform.system()

# Security-first project scope defaults.
ROUTER_ALLOWED_TARGETS = os.getenv("ROUTER_ALLOWED_TARGETS", "localhost,127.0.0.1,192.168.56.0/24").strip()
ROUTER_ALLOWED_ACTIONS = os.getenv(
    "ROUTER_ALLOWED_ACTIONS",
    "recon,osint,run_command,collect_notes,summarize_findings,report",
).strip()
ROUTER_PERMISSION_MODE = os.getenv("ROUTER_PERMISSION_MODE", "bounded").strip().lower()

try:
    from .persona import get_persona
    FARX_INSTRUCTION = get_persona(CURRENT_OS)
except ImportError:
    FARX_INSTRUCTION = f"""You are R0uteR, a secure laptop copilot.
Operating system: {CURRENT_OS}. Follow local security rules."""
