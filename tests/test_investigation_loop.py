from modules.investigation_loop import InvestigationLoop


def test_investigation_loop_decides_osint_for_domain_target():
    loop = InvestigationLoop("example.com", goal="osint")
    tool = loop.decide_next_step()

    assert tool.name == "amass-passive"


def test_investigation_loop_decides_nmap_for_ip_target():
    loop = InvestigationLoop("192.168.56.10", goal="recon")
    tool = loop.decide_next_step()

    assert tool.name == "nmap"


def test_investigation_loop_tracks_state():
    loop = InvestigationLoop("example.com")
    assert loop.evaluate_progress() == "queued"

    loop.add_evidence({"source": "nmap", "ports": ["80", "443"]})
    assert loop.evaluate_progress() == "running"

    loop.add_finding({"title": "HTTP exposed", "severity": "medium"})
    assert loop.evaluate_progress() == "evidence_ready"


def test_investigation_loop_chooses_vuln_scan_for_web_exposure():
    loop = InvestigationLoop("192.168.56.10", goal="recon")
    loop.add_finding({"title": "HTTP service exposure", "severity": "medium", "confidence": "high", "port": "80"})

    tool = loop.decide_next_step()

    assert tool.name == "nuclei"
