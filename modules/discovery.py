"""Subdomain and HTTP discovery helpers for the R0uteR workflow."""

from __future__ import annotations

import re
from typing import Any


def extract_subdomains(raw_output: str) -> list[str]:
    """Extract domains and subdomains from discovery text and URLs."""
    text = (raw_output or "").strip()
    if not text:
        return []

    def normalize_host(host: str) -> str:
        candidate = host.strip().rstrip(".")
        if not candidate:
            return ""
        candidate = candidate.split("/", 1)[0]
        candidate = candidate.rsplit(":", 1)[0] if candidate.count(":") == 1 else candidate
        if candidate.startswith("[") and "]" in candidate:
            candidate = candidate[1:candidate.index("]")]
        return candidate

    seen: set[str] = set()
    domain_pattern = re.compile(r"(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/|\s|$|[\],)\]>])", re.IGNORECASE)
    url_pattern = re.compile(r"https?://([^/\s]+)", re.IGNORECASE)

    for match in url_pattern.finditer(text):
        host = normalize_host(match.group(1))
        if host and "." in host:
            seen.add(host)

    for match in domain_pattern.finditer(text):
        host = normalize_host(match.group(1))
        if host and "." in host:
            seen.add(host)

    return sorted(seen)


def extract_live_hosts(raw_output: str) -> list[str]:
    """Return valid external HTTP(S) hostnames from discovery output while filtering localhost noise and tool banners."""
    text = (raw_output or "").strip()
    if not text:
        return []

    ignored_hosts = {"nmap.org", "www.nmap.org", "tooling.nmap.org"}
    seen: set[str] = set()
    for match in re.finditer(r"https?://([^\s/]+)", text, flags=re.IGNORECASE):
        host = match.group(1).strip().rstrip(".")
        if not host or host.startswith("127.") or host.startswith("localhost"):
            continue
        host = host.split(":", 1)[0] if host.count(":") == 1 and not host.startswith("[") else host
        if host and "." in host and host.lower() not in ignored_hosts:
            seen.add(host)

    hosts = sorted(seen)
    return hosts


def parse_httpx_output(raw_output: str) -> dict[str, Any]:
    """Parse httpx-like output into live URLs and hosts while filtering local-only targets."""
    text = (raw_output or "").strip()
    if not text:
        return {"status": "no_live_hosts_found", "urls": [], "live_hosts": [], "summary": "No live hosts were identified."}

    ignored_hosts = {"nmap.org", "www.nmap.org", "tooling.nmap.org"}
    urls: list[str] = []
    hosts: set[str] = set()
    for match in re.finditer(r"(?:\[[^\]]+\]\s*)?(https?://[^\s]+)", text, flags=re.IGNORECASE):
        value = match.group(1).strip().rstrip("/")
        if not value:
            continue
        if value.startswith("http://127.") or value.startswith("https://127.") or "localhost" in value:
            continue
        urls.append(value)
        host = re.sub(r"^https?://", "", value, flags=re.IGNORECASE)
        host = host.split("/", 1)[0].split(":", 1)[0]
        if host and "." in host and host.lower() not in ignored_hosts:
            hosts.add(host)

    return {
        "status": "success" if urls else "no_live_hosts_found",
        "urls": sorted(dict.fromkeys(urls)),
        "live_hosts": sorted(hosts),
        "summary": f"Discovered {len(urls)} live URL(s)." if urls else "No live hosts were identified.",
    }


def rank_live_hosts(raw_output: str) -> list[str]:
    """Return a simple prioritized list of live hosts from raw discovery output."""
    hosts = extract_live_hosts(raw_output)
    if not hosts:
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
