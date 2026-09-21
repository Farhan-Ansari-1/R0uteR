from modules.recon import summarize_recon_output, suggest_next_actions


def test_summarize_recon_output_extracts_ports_and_services():
    sample = """
    Starting Nmap 7.94 ( https://nmap.org ) at 2025-01-01 12:00 UTC
    Nmap scan report for 192.168.56.10
    Host is up (0.010s latency).
    PORT     STATE SERVICE VERSION
    22/tcp   open  ssh     OpenSSH 8.9p1
    80/tcp   open  http    nginx 1.18
    443/tcp  open  https   nginx 1.18
    MAC Address: 00:11:22:33:44:55 (Test Device)
    """

    summary = summarize_recon_output(sample, "192.168.56.10")

    assert "192.168.56.10" in summary
    assert "22" in summary
    assert "80" in summary
    assert "443" in summary
    assert "ssh" in summary.lower()
    assert "http" in summary.lower()


def test_suggest_next_actions_prioritizes_web_and_auth():
    actions = suggest_next_actions("80", "443", "22")

    assert "web" in actions[0].lower() or "auth" in actions[0].lower() or "service" in actions[0].lower()
    assert any("80" in item or "443" in item for item in actions)


def test_summary_ignores_filtered_web_services():
    sample = """
    Starting Nmap 7.99 ( https://nmap.org )
    PORT     STATE    SERVICE
    22/tcp   open     ssh
    80/tcp   filtered http
    443/tcp  filtered https
    """

    summary = summarize_recon_output(sample, "192.168.44.129")

    assert "SSH is exposed" in summary
    assert "Web services are exposed" not in summary
