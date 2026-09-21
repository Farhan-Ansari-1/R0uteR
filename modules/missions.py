"""Mission orchestration for the R0uteR security copilot.

A mission is a bounded sequence of steps such as: recon -> osint -> summarize -> report.
This keeps the project aligned to the controlled, permission-first workflow.
"""

from __future__ import annotations

from modules.evidence import EvidenceStore
from modules.osint import gather_osint
from modules.orchestrator import execute_recon_pipeline
from modules.reporting import build_recon_report


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
        recon = execute_recon_pipeline(self.target, self.task, self.extra_args)
        if not recon["success"]:
            return {
                "success": False,
                "message": recon["message"],
            }

        osint = gather_osint(self.target) if self.include_osint else {
            "success": True,
            "skipped": True,
            "target": self.target,
            "results": [],
        }

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
        )

        return {
            "success": True,
            "target": self.target,
            "recon": recon,
            "osint": osint,
            "report": report,
        }


def run_mission(
    target: str,
    task: str = "nmap",
    extra_args: str = "-sV --top-ports 20",
    include_osint: bool = True,
) -> dict:
    return MissionPlan(target, task, extra_args, include_osint=include_osint).run()
