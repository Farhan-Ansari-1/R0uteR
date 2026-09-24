"""Structured finding models for the R0uteR security investigation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EvidenceItem:
    source: str
    output_excerpt: str
    timestamp: str = field(default_factory=utc_now_iso)
    target: str = ""


@dataclass
class Finding:
    id: str
    title: str
    category: str
    description: str
    severity: str = "medium"
    confidence: str = "medium"
    evidence: list[EvidenceItem] = field(default_factory=list)
    status: str = "new"
    source_tool: str = "unknown"
    recommendation: str = ""
    related_targets: list[str] = field(default_factory=list)
    first_seen: str = field(default_factory=utc_now_iso)
    last_updated: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "confidence": self.confidence,
            "evidence": [
                {
                    "source": item.source,
                    "output_excerpt": item.output_excerpt,
                    "timestamp": item.timestamp,
                    "target": item.target,
                }
                for item in self.evidence
            ],
            "status": self.status,
            "source_tool": self.source_tool,
            "recommendation": self.recommendation,
            "related_targets": self.related_targets,
            "first_seen": self.first_seen,
            "last_updated": self.last_updated,
        }


def create_finding(
    title: str,
    category: str,
    description: str,
    source_tool: str,
    severity: str = "medium",
    confidence: str = "medium",
    recommendation: str = "",
    target: str = "",
    evidence_excerpt: str = "",
    status: str = "new",
) -> Finding:
    """Convenience constructor for a structured investigation finding."""
    return Finding(
        id=f"finding-{abs(hash(f'{title}:{source_tool}:{utc_now_iso()}'))}",
        title=title,
        category=category,
        description=description,
        severity=severity,
        confidence=confidence,
        evidence=[EvidenceItem(source=source_tool, output_excerpt=evidence_excerpt or description, target=target)] if evidence_excerpt or description else [],
        status=status,
        source_tool=source_tool,
        recommendation=recommendation,
        related_targets=[target] if target else [],
    )
