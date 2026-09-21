"""Interactive menu for the R0uteR security copilot."""

from __future__ import annotations

from modules.evidence import EvidenceStore
from modules.orchestrator import execute_recon_pipeline
from modules.reporting import build_recon_report


def show_menu() -> None:
    print("\nR0uteR Security Copilot")
    print("1. Run recon on a target")
    print("2. Show saved evidence")
    print("3. Exit")

    choice = input("Select an option: ").strip()

    if choice == "1":
        target = input("Target IP or hostname: ").strip()
        task = input("Recon task [nmap]: ").strip() or "nmap"
        args = input("Extra args [ -sV --top-ports 20 ]: ").strip() or "-sV --top-ports 20"

        result = execute_recon_pipeline(target, task, args)
        if not result["success"]:
            print(result["message"])
            return

        report = build_recon_report(target, result["summary"], result["next_steps"])
        store = EvidenceStore()
        store.save_entry(
            target=target,
            task=task,
            summary=result["summary"],
            next_steps=result["next_steps"],
            raw_output=result.get("raw_output", ""),
        )
        print("\n" + report)
        return

    if choice == "2":
        store = EvidenceStore()
        entries = store.list_entries()
        if not entries:
            print("No saved evidence yet.")
            return
        for entry in entries[:5]:
            print(f"\n[{entry['id']}] {entry['target']} | {entry['task']}\n{entry['summary']}\nNext: {', '.join(entry['next_steps'])}")
        return

    if choice == "3":
        print("Exiting.")
        return

    print("Invalid choice.")


if __name__ == "__main__":
    show_menu()
