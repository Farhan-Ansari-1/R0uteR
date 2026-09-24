"""Subdomain and HTTP discovery helpers for the R0uteR workflow."""

from __future__ import annotations

import re
from typing import Any


def extract_subdomains(raw_output: str) -> list[str]:
    """Extract domains and subdomains from discovery text and URLs."""
    text = (raw_output or "").strip()
    if not text:
        return []

    seen: set[str] = set()
    domain_pattern = re.compile(r"(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/|\s|$|[\],)\]>])", re.IGNORECASE)
    url_pattern = re.compile(r"https?://([^/\s]+)", re.IGNORECASE)

    for match in url_pattern.finditer(text):
        host = match.group(1).strip().rstrip(".")
        if host:
            seen.add(host)

    for match in domain_pattern.finditer(text):
        host = match.group(1).strip().rstrip(".")
        if host and "." in host:
            seen.add(host)

    return sorted(seen)


def rank_live_hosts(raw_output: str) -> list[str]:
    """Return a simple prioritized list of live hosts from raw discovery output."""
    hosts = extract_subdomains(raw_output)
    if not hosts:
        return []
    return hosts[:25]


def build_discovery_summary(raw_output: str) -> dict[str, Any]:
    """Turn raw discovery output into a structured summary for downstream reporting."""
    hosts = rank_live_hosts(raw_output)
    return {
        "live_hosts": hosts,
        "total_hosts": len(hosts),
        "status": "success" if hosts else "no_live_hosts_found",
        "summary": f"Discovered {len(hosts)} candidate live host(s)." if hosts else "No live hosts were identified.",
    }
