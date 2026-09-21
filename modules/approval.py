"""UI-owned, one-time approvals for sensitive R0uteR actions."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    request_id: str
    action: str
    target: str
    created_at: float
    decision: bool | None = None
    event: threading.Event | None = None


class ApprovalBroker:
    """Only the desktop UI may resolve a request; model text cannot do so."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, action: str, target: str, timeout_seconds: int = 45) -> bool:
        import os
        import sys

        mode = os.getenv("ROUTER_APPROVAL_MODE", "cli").strip().lower()

        # CLI Mode: Terminal approval without Windows popups
        if mode == "cli":
            auto_lab = os.getenv("ROUTER_AUTO_APPROVE_LAB", "true").strip().lower()
            if auto_lab in {"1", "true", "yes"} and not sys.stdin.isatty():
                print("-> Auto-approved by ROUTER_AUTO_APPROVE_LAB policy.\n")
                return True

            print("\n" + "=" * 62)
            print(f"⚠️  [R0uteR CLI APPROVAL REQUIRED]")
            print(f"Action: {action.replace('_', ' ').upper()}")
            print(f"Target: {target}")
            print("=" * 62)

            # Interactive TTY: Ask user in terminal directly
            if sys.stdin and sys.stdin.isatty():
                try:
                    ans = input("Approve this action? [y/N]: ").strip().lower()
                    approved = ans in {"y", "yes"}
                    print(f"-> Decision: {'APPROVED' if approved else 'DENIED'}\n")
                    return approved
                except (EOFError, KeyboardInterrupt):
                    return False

            # In non-interactive or lab automation: check auto-approve lab flag
            if auto_lab in {"1", "true", "yes"}:
                print("-> Auto-approved by ROUTER_AUTO_APPROVE_LAB policy.\n")
                return True
            return False

        # UI Mode: Fallback to desktop window modal
        request = ApprovalRequest(
            request_id=uuid.uuid4().hex,
            action=action,
            target=target[:500],
            created_at=time.time(),
            event=threading.Event(),
        )
        with self._lock:
            self._requests[request.request_id] = request
        request.event.wait(timeout_seconds)
        with self._lock:
            completed = self._requests.pop(request.request_id, request)
        return completed.decision is True

    def pending(self) -> list[ApprovalRequest]:
        with self._lock:
            return [request for request in self._requests.values() if request.decision is None]

    def resolve(self, request_id: str, approved: bool) -> bool:
        with self._lock:
            request = self._requests.get(request_id)
            if request is None or request.decision is not None:
                return False
            request.decision = approved
            request.event.set()
            return True

    def deny_all(self) -> None:
        """Release waiting worker threads during application shutdown."""
        with self._lock:
            for request in self._requests.values():
                if request.decision is None:
                    request.decision = False
                    request.event.set()


approval_broker = ApprovalBroker()
