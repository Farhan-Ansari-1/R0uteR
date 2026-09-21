"""Local safety policy for R0uteR.

This module is deliberately independent from the LLM. An LLM may suggest an
action, but it cannot weaken this policy by changing tool arguments or by
claiming that the user confirmed an action.
"""

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from .approval import approval_broker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIRECTORY = PROJECT_ROOT / ".r0uter"
AUDIT_LOG = AUDIT_DIRECTORY / "audit.jsonl"

PROTECTED_PATH_PATTERNS = [
    r"^[a-zA-Z]:\\windows(?:\\|$)",
    r"^[a-zA-Z]:\\program files(?:\\|$)",
    r"^[a-zA-Z]:\\program files \(x86\)(?:\\|$)",
    r"^[a-zA-Z]:\\recovery(?:\\|$)",
    r"^[a-zA-Z]:\\\$recycle\.bin(?:\\|$)",
    r"^[a-zA-Z]:\\system volume information(?:\\|$)",
]
PROTECTED_PARTS = {".git", ".ssh", ".gnupg", ".aws", ".azure", ".kube", ".r0uter"}
PROTECTED_FILENAMES = {
    ".env", ".env.local", ".env.production", "id_rsa", "id_ed25519",
    "credentials", "credentials.json", "ntuser.dat",
}
DANGEROUS_COMMAND_PATTERNS = [
    r"\bformat\b", r"\bdiskpart\b", r"\bbcdedit\b", r"\breg\s+delete\b",
    r"\brmdir\b", r"\bdel\b", r"\brm\b", r"\bremove-item\b",
    r"\bshutdown\b", r"\bvssadmin\b", r"\binvoke-expression\b",
]
APPROVAL_REQUIRED_ACTIONS = {
    "write_file", "delete", "run_python_code", "run_project_check",
    "send_whatsapp_message", "automate_typing", "automate_keypress",
    "close_window", "save_contact", "vm_lab_command", "recon_task",
}
AUTO_APPROVED_ACTIONS = {
    "open_application", "open_website", "copy_to_clipboard", "read_clipboard",
    "switch_window", "list_directory", "read_file", "search_files",
    "analyze_project", "security_posture", "project_check",
    "test_vm_connection", "get_lab_status", "lab_target_status",
}

_audit_lock = threading.Lock()


def _normalise(path_str: str) -> str:
    return os.path.normcase(str(Path(path_str).resolve(strict=False)))


def audit_event(action: str, outcome: str, target: str = "", detail: str = "") -> None:
    """Append a local audit record without storing file contents or secrets."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "outcome": outcome,
        "target": target[:500],
        "detail": detail[:500],
    }
    try:
        with _audit_lock:
            AUDIT_DIRECTORY.mkdir(exist_ok=True)
            with AUDIT_LOG.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def is_protected_path(path_str: str) -> bool:
    """Return True for system, credential, repository, and R0uteR-private paths."""
    if not path_str:
        return True
    try:
        resolved = _normalise(path_str)
        if any(re.search(pattern, resolved, re.IGNORECASE) for pattern in PROTECTED_PATH_PATTERNS):
            return True
        path = Path(resolved)
        parts = {part.lower() for part in path.parts}
        return bool(parts & PROTECTED_PARTS) or path.name.lower() in PROTECTED_FILENAMES
    except (OSError, ValueError):
        return True


def require_safe_path(action: str, path_str: str) -> tuple[bool, str]:
    if is_protected_path(path_str):
        audit_event(action, "blocked", path_str, "protected or invalid path")
        return False, "Blocked: protected system, credential, repository, or R0uteR path."
    return True, "Path permitted."


def is_safe_command(command: str) -> tuple[bool, str]:
    """Deny direct shell access until a user-approved command broker exists."""
    command = (command or "").strip()
    if not command:
        return False, "Command is empty."
    detail = "matched dangerous pattern" if any(
        re.search(pattern, command, re.IGNORECASE) for pattern in DANGEROUS_COMMAND_PATTERNS
    ) else "direct shell execution disabled in Safe Mode"
    audit_event("terminal_command", "blocked", command, detail)
    return False, "Direct terminal commands are disabled in Safe Mode. Use an approved task workflow."


def require_user_approval(action: str, target: str = "") -> tuple[bool, str]:
    """Request a visible, expiring approval from the local desktop UI."""
    if action in AUTO_APPROVED_ACTIONS:
        audit_event(action, "auto_approved", target, "low-risk action policy")
        return True, "Auto-approved by the low-risk action policy."
    if action not in APPROVAL_REQUIRED_ACTIONS:
        audit_event(action, "blocked", target, "unknown action is not approved by policy")
        return False, f"Blocked: action '{action}' is not approved by the local safety policy."
    audit_event(action, "approval_requested", target, "waiting for local UI approval")
    approved = approval_broker.request(action, target)
    outcome = "approved" if approved else "denied_or_expired"
    audit_event(action, outcome, target)
    if approved:
        return True, "Approved once by the local R0uteR UI."
    return False, f"{action.replace('_', ' ').title()} was denied or approval expired."


def safe_delete_path(path_str: str) -> tuple[bool, str]:
    """Move an approved non-protected path to the Recycle Bin."""
    permitted, message = require_safe_path("delete", path_str)
    if not permitted:
        return False, message
    approved, message = require_user_approval("delete", path_str)
    if not approved:
        return False, message
    if not os.path.exists(path_str):
        return False, f"Path does not exist: {path_str}"
    try:
        from send2trash import send2trash
        send2trash(path_str)
        audit_event("delete", "recycle_bin", path_str)
        return True, "Moved to the Recycle Bin. It can be restored."
    except OSError as error:
        audit_event("delete", "failed", path_str, str(error))
        return False, f"Could not move the path to Recycle Bin: {error}"
