"""Risk and prioritization logic for structured findings."""

from __future__ import annotations

from typing import Any


SEVERITY_WEIGHT = {
    "informational": 10,
    "low": 25,
    "medium": 45,
    "high": 70,
    "critical": 90,
}

CONFIDENCE_WEIGHT = {
    "low": 0.5,
    "medium": 0.75,
    "high": 1.0,
}


def score_finding(finding: dict[str, Any]) -> float:
    """Compute an overall risk score using severity and confidence separately."""
    severity = str(finding.get("severity", "medium")).lower()
    confidence = str(finding.get("confidence", "medium")).lower()

    base = SEVERITY_WEIGHT.get(severity, 45)
    confidence_factor = CONFIDENCE_WEIGHT.get(confidence, 0.75)
    score = base * confidence_factor
    return round(score, 2)


def rank_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return findings ordered by a combined priority score."""
    ranked = []
    for finding in findings:
        item = dict(finding)
        item["risk_score"] = score_finding(item)
        ranked.append(item)

    ranked.sort(key=lambda item: item["risk_score"], reverse=True)
    return ranked
