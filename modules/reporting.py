"""Report generation for recon findings and recommended next steps."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


def build_recon_report(
    target: str,
    summary: str,
    next_steps: Iterable[str],
    evidence_id: int | None = None,
    osint: dict[str, Any] | None = None,
    llm_summary: str | None = None,
) -> str:
    """Create a readable report from reconnaissance output and suggestions."""
    step_list = list(next_steps or [])
    lines = [
        "=== R0uteR Reconnaissance Report ===",
        f"Target: {target}",
        "",
        "Summary:",
        summary.strip(),
        "",
        "Recommended next steps:",
    ]

    if evidence_id is not None:
        lines.insert(2, f"Evidence ID: {evidence_id}")

    osint_results = list((osint or {}).get("results") or [])
    if osint_results:
        lines.extend(["", "OSINT review prompts:"])
        lines.extend(f"- {item}" for item in osint_results[:5])

    if llm_summary:
        lines.extend(["", "Local model review:", llm_summary.strip()])

    if not step_list:
        lines.append("- No additional actions recommended from the current evidence.")
    else:
        for index, step in enumerate(step_list, start=1):
            lines.append(f"{index}. {step}")

    return "\n".join(lines)


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._") or "target"


def export_report_bundle(
    report: str,
    evidence: dict[str, Any],
    output_dir: str | Path = "reports",
) -> dict[str, str]:
    """Write the readable report, structured evidence, and raw command output."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    prefix = f"{evidence['id']}_{_safe_filename(str(evidence['target']))}"

    report_path = destination / f"{prefix}_report.txt"
    evidence_path = destination / f"{prefix}_evidence.json"
    raw_path = destination / f"{prefix}_raw.txt"
    report_path.write_text(report + "\n", encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    raw_path.write_text(str(evidence.get("raw_output") or ""), encoding="utf-8")
    return {
        "report": str(report_path),
        "evidence": str(evidence_path),
        "raw_output": str(raw_path),
    }


def export_report_pdf(
    report: str,
    evidence: dict[str, Any],
    output_dir: str | Path = "reports",
) -> str:
    """Export the final report as PDF using the optional ReportLab dependency."""
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as error:
        raise RuntimeError("PDF support requires reportlab. Run: pip install reportlab") from error

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    prefix = f"{evidence['id']}_{_safe_filename(str(evidence['target']))}"
    pdf_path = destination / f"{prefix}_report.pdf"
    styles = getSampleStyleSheet()
    story = []
    for index, block in enumerate(report.split("\n\n")):
        text = block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(text.replace("\n", "<br/>"), styles["BodyText"]))
        if index < len(report.split("\n\n")) - 1:
            story.append(Spacer(1, 10))
    SimpleDocTemplate(str(pdf_path), pagesize=LETTER).build(story)
    return str(pdf_path)


def prune_report_bundles(output_dir: str | Path = "reports", max_bundles: int = 20) -> list[str]:
    """Keep the newest report bundles and remove older generated files."""
    if max_bundles < 1:
        raise ValueError("max_bundles must be at least 1")

    destination = Path(output_dir)
    report_files = list(destination.glob("*_report.txt")) if destination.exists() else []
    report_files.sort(key=_report_id, reverse=True)
    removed: list[str] = []

    for report_file in report_files[max_bundles:]:
        prefix = report_file.name.removesuffix("_report.txt")
        for generated_file in destination.glob(f"{prefix}_*"):
            if generated_file.is_file():
                generated_file.unlink()
        removed.append(prefix)
    return removed


def _report_id(path: Path) -> tuple[int, int]:
    match = re.match(r"(\d+)_", path.name)
    if match:
        return int(match.group(1)), 0
    return 0, path.stat().st_mtime_ns
