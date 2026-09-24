"""Lightweight vulnerability correlation helpers for the R0uteR mission flow."""

from __future__ import annotations

from typing import Any


def correlate_service_to_vuln(service: str, port: str | int) -> dict[str, Any]:
    """Map discovered services to likely vulnerability themes using safe heuristics."""
    normalized = (service or "").strip().lower()
    port_number = int(port) if str(port).isdigit() else 0

    if normalized in {"ssh", "sshd"} and port_number == 22:
        return {
            "title": "SSH access exposure",
            "severity": "high",
            "confidence": "medium",
            "recommendation": "Review SSH auth, key restrictions, and account lockdown settings.",
        }

    if normalized in {"http", "https", "http-proxy", "nginx", "apache"} and port_number in {80, 443}:
        return {
            "title": "Web service exposure",
            "severity": "medium",
            "confidence": "high",
            "recommendation": "Inspect HTTP headers, TLS posture, and app surfaces for authentication and exposure issues.",
        }

    if normalized in {"ftp", "telnet", "rdp"}:
        return {
            "title": f"{normalized.upper()} service exposure",
            "severity": "medium",
            "confidence": "medium",
            "recommendation": f"Evaluate {normalized.upper()} exposure and restrict access to approved sources only.",
        }

    return {
        "title": f"{normalized.upper() or 'Unknown'} service exposure",
        "severity": "low",
        "confidence": "low",
        "recommendation": "Collect additional service evidence before prioritizing a vulnerability claim.",
    }


def map_vuln_findings(discovered_services: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert service findings into vulnerability correlation results."""
    results: list[dict[str, Any]] = []
    for service in discovered_services:
        title = str(service.get("title", "")).strip()
        service_name = str(service.get("service") or service.get("title", "")).strip().lower()
        service_name = service_name.replace(" service exposure", "").replace("http service exposure", "http")
        port = str(service.get("port") or service.get("service_port") or "0").strip()
        if not port or port == "0":
            port = str(title.rsplit("port ", 1)[-1]).strip().split()[0] if "port " in title.lower() else "0"
        result = correlate_service_to_vuln(service_name or "unknown", port)
        result["source_title"] = title
        result["port"] = port
        results.append(result)
    return results
