"""Adaptive investigation loop for the R0uteR security copilot."""

from __future__ import annotations

from typing import Any

from .tool_registry import ToolDefinition, choose_next_tool


class InvestigationLoop:
    """Select the next safe step based on mission goal and current evidence."""

    def __init__(self, target: str, goal: str = "recon") -> None:
        self.target = target
        self.goal = goal
        self.evidence: list[dict[str, Any]] = []
        self.findings: list[dict[str, Any]] = []

    def add_evidence(self, evidence: dict[str, Any]) -> None:
        self.evidence.append(evidence)

    def add_finding(self, finding: dict[str, Any]) -> None:
        self.findings.append(finding)

    def decide_next_step(self) -> ToolDefinition:
        context = {"target": self.target, "evidence": self.evidence, "findings": self.findings}
        return choose_next_tool(self.goal, context)

    def evaluate_progress(self) -> str:
        if not self.evidence:
            return "queued"
        if self.findings:
            return "evidence_ready"
        return "running"
