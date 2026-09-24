from modules.intel import correlate_cve, enrich_findings_with_intel


def test_correlate_cve_returns_advisory_metadata_for_known_service():
    result = correlate_cve("ssh", "OpenSSH 8.0")

    assert result["confidence"] in {"medium", "low"}
    assert "CVE" in result["cve"] or "required" in result["cve"]


def test_enrich_findings_with_intel_adds_intel_block():
    findings = [{"source_tool": "nmap", "version": "OpenSSH 8.0", "title": "SSH service exposure"}]
    result = enrich_findings_with_intel(findings)

    assert "intel" in result[0]
    assert "cve" in result[0]["intel"]
