from modules.reporting import build_recon_report
from modules.reporting import export_report_bundle, prune_report_bundles


def test_build_recon_report_includes_target_summary_and_steps():
    report = build_recon_report(
        target="127.0.0.1",
        summary="Open ports: 22, 80, 443",
        next_steps=["Review SSH", "Inspect web service"],
    )

    assert "127.0.0.1" in report
    assert "Open ports" in report
    assert "Review SSH" in report
    assert "Inspect web service" in report


def test_build_recon_report_includes_evidence_and_osint_context():
    report = build_recon_report(
        target="example.test",
        summary="Open ports: 443",
        next_steps=["Review TLS"],
        evidence_id=7,
        osint={"results": ["Review certificate information"]},
    )

    assert "Evidence ID: 7" in report
    assert "OSINT review prompts:" in report
    assert "certificate information" in report


def test_build_recon_report_includes_local_model_review():
    report = build_recon_report(
        target="127.0.0.1",
        summary="Open ports: 22",
        next_steps=["Review SSH"],
        llm_summary="SSH is the only confirmed exposed service.",
    )

    assert "Local model review:" in report
    assert "only confirmed exposed service" in report


def test_build_recon_report_includes_prioritized_findings():
    report = build_recon_report(
        target="127.0.0.1",
        summary="Open ports: 22",
        next_steps=["Review SSH"],
        findings=[
            {"title": "Critical SSH exposure", "severity": "critical", "confidence": "high"},
            {"title": "Low confidence web content", "severity": "low", "confidence": "low"},
        ],
    )

    assert "Risk summary:" in report
    assert "Prioritized findings:" in report
    assert "Critical SSH exposure" in report
    assert "risk_score" in report
    assert "Severity:" in report
    assert "Confidence:" in report


def test_build_recon_report_includes_exec_summary_for_human_readers():
    report = build_recon_report(
        target="example.com",
        summary="Open ports: 80, 443",
        next_steps=["Review web service"],
        findings=[
            {"title": "Web service exposure", "severity": "medium", "confidence": "high"},
        ],
    )

    assert "Executive summary:" in report
    assert "Current risk posture:" in report
    assert "Review web service" in report


def test_export_report_bundle_writes_report_evidence_and_raw_output(tmp_path):
    evidence = {
        "id": 4,
        "target": "127.0.0.1",
        "task": "nmap",
        "summary": "Open ports: 22",
        "next_steps": [],
        "raw_output": "22/tcp open ssh",
    }

    paths = export_report_bundle("Test report", evidence, tmp_path)

    assert all(__import__("pathlib").Path(path).exists() for path in paths.values())
    assert (tmp_path / "4_127.0.0.1_report.txt").read_text(encoding="utf-8") == "Test report\n"


def test_prune_report_bundles_keeps_only_newest_twenty(tmp_path):
    for entry_id in range(1, 22):
        evidence = {
            "id": entry_id,
            "target": "127.0.0.1",
            "task": "ping",
            "summary": f"Entry {entry_id}",
            "next_steps": [],
            "raw_output": "reply",
        }
        export_report_bundle(f"Report {entry_id}", evidence, tmp_path)

    removed = prune_report_bundles(tmp_path, max_bundles=20)

    assert len(list(tmp_path.glob("*_report.txt"))) == 20
    assert "1_127.0.0.1" in removed
    assert not (tmp_path / "1_127.0.0.1_evidence.json").exists()
