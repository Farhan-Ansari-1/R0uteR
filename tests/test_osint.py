from modules.osint import extract_target_domain, gather_osint


def test_extract_target_domain_handles_url_and_hostname():
    assert extract_target_domain("https://example.com") == "example.com"
    assert extract_target_domain("10.0.0.5") == "10.0.0.5"


def test_gather_osint_requires_authorized_target():
    result = gather_osint("8.8.8.8")

    assert result["success"] is False
    assert "authorized" in result["reason"].lower()
