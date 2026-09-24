"""Public intelligence correlation helpers for the R0uteR mission flow."""

from __future__ import annotations

from typing import Any


def correlate_cve(service: str, version: str | None = None) -> dict[str, Any]:
    """Return a simple advisory correlation object for likely service versions."""
    normalized = (service or "").strip().lower()
    version_value = (version or "").strip()

    if normalized in {"ssh", "sshd"} and "openssh" in version_value.lower():
        return {
            "cve": "CVE-2024-3094",
            "note": "Openssh version metadata should be reviewed against public advisories before remediation prioritization.",
            "confidence": "medium",
        }

    if normalized in {"http", "nginx", "apache"}:
        return {
            "cve": "NVD advisory review required",
            "note": "Web service stack version should be checked against public NVD or vendor advisories.",
            "confidence": "medium",
        }

    return {
        "cve": "No direct public CVE mapping available",
        "note": "Additional service metadata is required before a public CVE claim is warranted.",
        "confidence": "low",
    }


def enrich_findings_with_intel(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach advisory context to findings where version information is available."""
    enriched: list[dict[str, Any]] = []
    for finding in findings:
        item = dict(finding)
        service = str(item.get("service") or item.get("title", "")).lower()
        service = service.replace(" service exposure", "")
        version = str(item.get("version", "") or "")
        if not version:
            version = str(item.get("description", "") or "")
        intel = correlate_cve(service, version)
        item["intel"] = intel
        enriched.append(item)
    return enriched
