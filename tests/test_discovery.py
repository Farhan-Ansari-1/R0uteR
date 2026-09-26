from modules.discovery import build_discovery_summary, extract_live_hosts, extract_subdomains, parse_httpx_output


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


def test_extract_subdomains_strips_ports_and_keeps_domain_names_only():
    raw = "subfinder found example.com\nhttps://api.example.com:443\nhttps://login.example.com:8443\n127.0.0.1\n"
    result = extract_subdomains(raw)

    assert "example.com" in result
    assert "api.example.com" in result
    assert "login.example.com" in result
    assert any(":" not in host for host in result)


def test_extract_live_hosts_keeps_http_urls_and_filters_local_ips():
    raw = "https://example.com\nhttps://api.example.com:443\nhttp://127.0.0.1:8080\n"
    result = extract_live_hosts(raw)

    assert "example.com" in result
    assert "api.example.com" in result
    assert all("127.0.0.1" not in host for host in result)


def test_extract_live_hosts_handles_httpx_status_output():
    raw = "[200] https://example.com/\n[301] https://api.example.com/login\n[403] http://127.0.0.1:8080\n"
    result = extract_live_hosts(raw)

    assert "example.com" in result
    assert "api.example.com" in result
    assert all("127.0.0.1" not in host for host in result)


def test_parse_httpx_output_extracts_live_urls_and_hosts():
    raw = "[200] https://example.com/\n[301] https://api.example.com/login\n[403] http://127.0.0.1:8080\n"
    result = parse_httpx_output(raw)

    assert result["status"] == "success"
    assert "https://example.com" in result["urls"]
    assert "https://api.example.com/login" in result["urls"]
    assert "example.com" in result["live_hosts"]
    assert "api.example.com" in result["live_hosts"]
    assert all("127.0.0.1" not in host for host in result["live_hosts"])


def test_extract_live_hosts_ignores_nmap_tool_banner_urls():
    raw = "Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-26\nhttps://example.com\n"
    result = extract_live_hosts(raw)

    assert "example.com" in result
    assert "nmap.org" not in result
