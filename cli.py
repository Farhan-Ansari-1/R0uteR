"""Minimal command-line controller for the authorized security copilot."""

from __future__ import annotations

import argparse
import os

from modules.evidence import EvidenceStore
from modules.llm_adapter import LLMAdapter
from modules.orchestrator import execute_recon_pipeline
from modules.reporting import build_recon_report, export_report_bundle, export_report_pdf, prune_report_bundles


def main() -> None:
    parser = argparse.ArgumentParser(description="R0uteR authorized recon copilot")
    parser.add_argument("--target", required=True, help="Authorized target IP or host")
    parser.add_argument("--task", default="nmap", help="Recon task to run, default: nmap")
    parser.add_argument("--args", default="-sV --top-ports 20", help="Task arguments")
    parser.add_argument("--output-dir", default="reports", help="Directory for report and evidence files")
    args = parser.parse_args()

    result = execute_recon_pipeline(args.target, args.task, args.args)

    if not result["success"]:
        print(result["message"])
        return

    store = EvidenceStore()
    evidence_id = store.save_entry(
        target=args.target,
        task=args.task,
        summary=result["summary"],
        next_steps=result["next_steps"],
        raw_output=result.get("raw_output", ""),
    )
    evidence = store.get_entry(evidence_id)
    if evidence is None:
        evidence = {
            "id": evidence_id,
            "target": args.target,
            "task": args.task,
            "summary": result["summary"],
            "next_steps": result["next_steps"],
            "raw_output": result.get("raw_output", ""),
        }
    report = build_recon_report(
        args.target,
        result["summary"],
        result["next_steps"],
        evidence_id=evidence_id,
    )
    provider = os.getenv("ROUTER_AI_PROVIDER", "").strip().lower()
    llm_summary = None
    if provider in {"ollama", "local", "gemma", "llama"}:
        llm_summary = LLMAdapter(preferred_provider=provider).summarize(result["summary"])
        evidence["llm_summary"] = llm_summary
        report = build_recon_report(
            args.target,
            result["summary"],
            result["next_steps"],
            evidence_id=evidence_id,
            llm_summary=llm_summary,
        )
    paths = export_report_bundle(report, evidence, args.output_dir)
    try:
        paths["pdf"] = export_report_pdf(report, evidence, args.output_dir)
    except RuntimeError as error:
        print(f"PDF export skipped: {error}")
    prune_report_bundles(args.output_dir, max_bundles=20)

    print("\n" + report)
    print("\nSaved output:")
    for label, path in paths.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
