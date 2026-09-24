from modules.recon import parse_nmap_findings, summarize_recon_output


def test_parse_nmap_findings_extracts_service_risks():
    raw = """
Nmap scan report for 192.168.56.10
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.0
80/tcp   open  http    Apache httpd 2.4
443/tcp  open  https   nginx
"""

    findings = parse_nmap_findings(raw, "192.168.56.10")

    assert any(f["title"] == "SSH service exposure" for f in findings)
    assert any(f["title"] == "HTTP service exposure" for f in findings)
    assert all(f["severity"] in {"low", "medium", "high", "critical"} for f in findings)


def test_summarize_recon_output_still_keeps_basic_summary():
    raw = "PORT 22 open ssh\nPORT 80 open http\n"
    summary = summarize_recon_output(raw, "127.0.0.1")

    assert "Target: 127.0.0.1" in summary
    assert "Open ports: 22, 80" in summary
