"""Execution orchestration for the security-first R0uteR workflow."""

from __future__ import annotations

from modules import lab_bridge
from .permissions import PermissionPolicy
from .recon import summarize_recon_output, suggest_next_actions


class SafeReconOrchestrator:
    """Coordinates permission checks, task execution, and summary generation."""

    def __init__(self, policy: PermissionPolicy | None = None):
        self.policy = policy or PermissionPolicy()

    def execute(self, target: str, task_name: str, extra_args: str = "") -> dict:
        allowed, reason = self.policy.check_permission("recon", target)
        if not allowed:
            return {
                "success": False,
                "target": target,
                "message": reason,
                "summary": "",
                "next_steps": [],
            }

        raw_output = lab_bridge.run_recon_task(task_name, target, extra_args=extra_args)
        if self._is_failed_execution(raw_output):
            return {
                "success": False,
                "target": target,
                "message": raw_output,
                "summary": "",
                "next_steps": [],
                "raw_output": raw_output,
            }
        summary = summarize_recon_output(raw_output, target)
        next_steps = suggest_next_actions(*self._extract_ports(raw_output))

        return {
            "success": True,
            "target": target,
            "message": f"Recon task '{task_name}' completed successfully.",
            "summary": summary,
            "next_steps": next_steps,
            "raw_output": raw_output,
        }

    @staticmethod
    def _extract_ports(raw_output: str) -> list[str]:
        ports = []
        for match in __import__("re").findall(
            r"(\d{1,5})/tcp\s+open\b", raw_output or "", flags=__import__("re").IGNORECASE
        ):
            ports.append(match)
        return ports

    @staticmethod
    def _is_failed_execution(raw_output: str) -> bool:
        first_line = (raw_output or "").splitlines()[0].lower() if raw_output else ""
        return any(
            marker in first_line
            for marker in (
                "unsupported task",
                "target '",
                "was denied",
                "blocked:",
                "execution failed",
                "ssh execution error",
                "lab command error",
            )
        )


def execute_recon_pipeline(target: str, task_name: str, extra_args: str = "") -> dict:
    """Convenience function for the app to trigger a recon workflow with policy enforcement."""
    orchestrator = SafeReconOrchestrator()
    return orchestrator.execute(target, task_name, extra_args=extra_args)
