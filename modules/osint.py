"""Lightweight, permission-gated OSINT wrapper for authorized target research."""

from __future__ import annotations

import re
from urllib.parse import quote_plus

from .permissions import PermissionPolicy


class OSINTAgent:
    """Collects public metadata and notes in a bounded way."""

    def __init__(self, policy: PermissionPolicy | None = None):
        self.policy = policy or PermissionPolicy()

    def collect(self, target: str) -> dict:
        allowed, reason = self.policy.check_permission("osint", target)
        if not allowed:
            return {
                "success": False,
                "reason": reason,
                "results": [],
            }

        # This is intentionally lightweight and offline-safe.
        # It does not do invasive scraping; it just creates a bounded discovery list.
        host = target.strip().lower().replace("http://", "").replace("https://", "")
        normalized = host.split("/")[0]
        hints = [
            f"Search public records and WHOIS metadata for {normalized}",
            f"Inspect public DNS and certificate information for {normalized}",
            f"Review public web footprint and service naming for {normalized}",
            f"Look for associated aliases, technologies, and admin contact data for {normalized}",
        ]

        return {
            "success": True,
            "target": normalized,
            "results": hints,
        }


def gather_osint(target: str) -> dict:
    return OSINTAgent().collect(target)


def extract_target_domain(target: str) -> str:
    value = (target or "").strip().lower()
    match = re.search(r"(?:https?://)?([a-z0-9.-]+\.[a-z]{2,})", value)
    if match:
        return match.group(1)
    return value
