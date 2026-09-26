"""Mission orchestration for the R0uteR security copilot.

A mission is a bounded sequence of steps such as: recon -> osint -> summarize -> report.
This keeps the project aligned to the controlled, permission-first workflow.
"""

from __future__ import annotations

from modules.discovery import build_discovery_summary
from modules.evidence import EvidenceStore
from modules.finding import create_finding
from modules.investigation_loop import InvestigationLoop
from modules.intel import enrich_findings_with_intel
from modules.osint import gather_osint
from modules.orchestrator import execute_recon_pipeline
from modules.recon import parse_nmap_findings
from modules.reporting import build_recon_report
from modules.vuln import map_vuln_findings


class MissionPlan:
    """A simple mission plan with a sequence of security tasks."""

    def __init__(
        self,
        target: str,
        task: str = "nmap",
        extra_args: str = "-sV --top-ports 20",
        include_osint: bool = True,
    ):
        self.target = target
        self.task = task
        self.extra_args = extra_args
        self.include_osint = include_osint

    def run(self) -> dict:
        agent = InvestigationLoop(self.target, goal="recon")
        recon = execute_recon_pipeline(self.target, self.task, self.extra_args)
        if not recon["success"]:
            next_step = agent.decide_next_step()
            return {
                "success": False,
                "message": recon["message"],
                "target": self.target,
                "phase": "recon",
                "next_phase": "service_validation",
                "agent": {
                    "goal": "recon",
                    "phase": "recon",
                    "next_phase": "service_validation",
                    "status": "blocked",
                    "next_tool": next_step.name,
                    "next_tool_purpose": next_step.purpose,
                },
            }

        osint = gather_osint(self.target) if self.include_osint else {
            "success": True,
            "skipped": True,
            "target": self.target,
            "results": [],
        }
        if self.target and any(ch.isdigit() for ch in self.target) and "." in self.target and not any(letter.isalpha() for letter in self.target):
            discovery = {
                "live_hosts": [],
                "total_hosts": 0,
                "status": "no_live_hosts_found",
                "summary": "Discovery is not applicable to direct IP targets; Nmap recon is the active phase.",
            }
        else:
            discovery = build_discovery_summary(recon.get("raw_output", ""))
        raw_findings = parse_nmap_findings(recon.get("raw_output", ""), self.target)
        mapped = map_vuln_findings(raw_findings)
        enriched = enrich_findings_with_intel(raw_findings)
        findings = []
        for index, item in enumerate(enriched):
            merged = dict(item)
            if index < len(mapped):
                merged.update({
                    "vuln": mapped[index],
                    "severity": mapped[index].get("severity", item.get("severity", "medium")),
                    "confidence": mapped[index].get("confidence", item.get("confidence", "medium")),
                    "recommendation": mapped[index].get("recommendation", item.get("recommendation", "Review evidence and continue with targeted verification.")),
                })
            findings.append(merged)

        structured_findings = []
        for finding in findings:
            if not finding.get("recommendation"):
                finding["recommendation"] = "Review evidence and continue with targeted verification."
            structured_findings.append(
                create_finding(
                    title=finding.get("title", "Service exposure"),
                    category=finding.get("category", "network_service"),
                    description=finding.get("description", "Discovered service exposure."),
                    source_tool=finding.get("source_tool", "nmap"),
                    severity=finding.get("severity", "medium"),
                    confidence=finding.get("confidence", "medium"),
                    recommendation=finding.get("recommendation", "Review evidence and continue with targeted verification."),
                    target=finding.get("target", self.target),
                    evidence_excerpt=finding.get("description", ""),
                    status="new",
                ).to_dict()
            )

        agent = InvestigationLoop(self.target, goal="recon")
        agent.add_evidence({
            "source": "recon",
            "summary": recon.get("summary", ""),
            "raw_output": recon.get("raw_output", ""),
            "next_steps": recon.get("next_steps", []),
        })
        for finding in raw_findings:
            agent.add_finding(finding)

        next_step = agent.decide_next_step()
        agent_state = agent.evaluate_progress()
        mission_next_tool = "nmap"
        next_phase = "service_validation"
        if next_step.name == "nuclei":
            mission_next_tool = "nmap"
            next_phase = "service_validation"

        store = EvidenceStore()
        evidence_id = store.save_entry(
            target=self.target,
            task=self.task,
            summary=recon["summary"],
            next_steps=recon["next_steps"],
            raw_output=recon.get("raw_output", ""),
        )
        report = build_recon_report(
            self.target,
            recon["summary"],
            recon["next_steps"],
            evidence_id=evidence_id,
            osint=osint,
            findings=structured_findings,
        )

        return {
            "success": True,
            "target": self.target,
            "phase": "recon",
            "next_phase": next_phase,
            "recon": recon,
            "osint": osint,
            "discovery": discovery,
            "findings": structured_findings,
            "agent": {
                "goal": "recon",
                "phase": "recon",
                "next_phase": next_phase,
                "status": agent_state,
                "next_tool": mission_next_tool,
                "next_tool_purpose": "Service validation and live target review after recon results.",
            },
            "report": report,
        }


def run_mission(
    target: str,
    task: str = "nmap",
    extra_args: str = "-sV --top-ports 20",
    include_osint: bool = True,
) -> dict:
    return MissionPlan(target, task, extra_args, include_osint=include_osint).run()
