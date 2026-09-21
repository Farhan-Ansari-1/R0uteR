"""Permission model for the security-first R0uteR architecture.

This is the first step in moving the project away from a generic AI assistant
model and toward a bounded, policy-driven offensive security copilot.
"""

from __future__ import annotations

import ipaddress
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class PermissionPolicy:
    """A small, explicit permission layer for allowed actions and targets."""

    DEFAULT_ALLOWED_ACTIONS = {
        "recon",
        "osint",
        "run_command",
        "collect_notes",
        "summarize_findings",
        "report",
    }

    DEFAULT_BLOCKED_ACTIONS = {
        "destructive_action",
        "delete_system",
        "wipe",
        "shutdown",
        "reboot",
        "format_disk",
        "bypass_security",
        "privilege_escalation",
    }

    def __init__(self, allowed_targets: str | list[str] | None = None, allowed_actions: str | set[str] | None = None):
        target_value = allowed_targets or os.getenv(
            "ROUTER_ALLOWED_TARGETS",
            os.getenv("ROUTER_LAB_TARGETS", "localhost,127.0.0.1,192.168.56.0/24"),
        )
        action_value = allowed_actions or os.getenv("ROUTER_ALLOWED_ACTIONS", "recon,osint,run_command,collect_notes,summarize_findings,report")

        self.allowed_targets = self._parse_targets(target_value)
        self.allowed_actions = {str(item).strip().lower() for item in self._parse_actions(action_value)}
        self.blocked_actions = set(self.DEFAULT_BLOCKED_ACTIONS)

    @staticmethod
    def _parse_targets(value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = list(value)
        return [str(item).strip() for item in items if str(item).strip()]

    @staticmethod
    def _parse_actions(value: str | set[str]) -> list[str]:
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = list(value)
        return [str(item).strip() for item in items if str(item).strip()]

    @staticmethod
    def _normalise_target(target: str) -> str:
        value = (target or "").strip()
        if not value:
            return ""

        parsed = urlparse(value if "://" in value else f"//{value}")
        host = (parsed.hostname or value).strip().lower()
        return host.strip("[]")

    def is_authorized_target(self, target: str) -> bool:
        host = self._normalise_target(target)
        if not host:
            return True

        localhost_values = {"localhost", "127.0.0.1", "::1"}
        if host in localhost_values:
            return True

        for entry in self.allowed_targets:
            entry_value = entry.strip().lower()
            if not entry_value:
                continue
            if entry_value == host:
                return True
            try:
                network = ipaddress.ip_network(entry_value, strict=False)
                target_ip = ipaddress.ip_address(host)
                if target_ip in network:
                    return True
            except ValueError:
                continue
        return False

    def check_permission(self, action: str, target: str = "") -> tuple[bool, str]:
        action_key = str(action or "").strip().lower()

        if not action_key:
            return False, "Action is empty."

        if action_key in self.blocked_actions:
            return False, "Blocked: high-risk action is denied by default."

        if action_key not in self.allowed_actions:
            return False, f"Action '{action}' is not in the current authorized action set."

        if target and not self.is_authorized_target(target):
            return False, f"Target '{target}' is not in authorized scope."

        return True, f"Action '{action}' is authorized for the current scope."

    @classmethod
    def from_env(cls, allowed_targets: str | None = None, allowed_actions: str | None = None) -> "PermissionPolicy":
        return cls(allowed_targets=allowed_targets, allowed_actions=allowed_actions)
