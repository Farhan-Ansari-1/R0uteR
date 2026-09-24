from modules.vuln import correlate_service_to_vuln, map_vuln_findings


def test_correlate_service_to_vuln_ssh_is_high_risk():
    result = correlate_service_to_vuln("ssh", 22)

    assert result["title"] == "SSH access exposure"
    assert result["severity"] == "high"
    assert "SSH auth" in result["recommendation"]


def test_map_vuln_findings_uses_service_metadata():
    findings = [
        {"title": "SSH service exposure", "port": 22},
        {"title": "HTTP service exposure", "port": 80},
    ]

    result = map_vuln_findings(findings)

    assert result[0]["title"] == "SSH access exposure"
    assert result[1]["title"] == "Web service exposure"
