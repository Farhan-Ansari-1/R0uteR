from modules.discovery import build_discovery_summary, extract_subdomains


def test_extract_subdomains_handles_basic_output():
    raw = "\nsubfinder found example.com\napi.example.com\nlogin.example.com\n"
    result = extract_subdomains(raw)

    assert "example.com" in result
    assert "api.example.com" in result
    assert "login.example.com" in result


def test_build_discovery_summary_reports_live_hosts():
    raw = "https://example.com\nhttps://api.example.com\nhttps://login.example.com\n"
    result = build_discovery_summary(raw)

    assert result["status"] == "success"
    assert result["total_hosts"] >= 1
    assert "example.com" in result["live_hosts"]
