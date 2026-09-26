from modules.tool_registry import ToolRegistry, choose_next_tool


def test_tool_registry_contains_core_security_tools():
    registry = ToolRegistry()
    names = {tool.name for tool in registry.tools}

    required = {
        "theHarvester",
        "amass-passive",
        "subfinder",
        "httpx",
        "nmap",
        "nuclei",
        "nvd_lookup",
    }

    assert required.issubset(names)


def test_tool_registry_selects_osint_for_domain_target():
    tool = choose_next_tool("osint", {"target": "example.com"})

    assert tool.name == "amass-passive"


def test_tool_registry_selects_nmap_for_ip_target():
    tool = choose_next_tool("recon", {"target": "192.168.56.10"})

    assert tool.name == "nmap"


def test_tool_registry_selects_subfinder_for_domain_discovery_target():
    tool = choose_next_tool("discovery", {"target": "example.com"})

    assert tool.name == "subfinder"


def test_tool_registry_prioritizes_domain_discovery_before_recon():
    tool = choose_next_tool("recon", {"target": "example.com"})

    assert tool.name == "subfinder"


def test_tool_registry_selects_httpx_after_subdomain_discovery():
    tool = choose_next_tool(
        "discovery",
        {
            "target": "example.com",
            "evidence": [{"source": "subfinder", "subdomains": ["api.example.com", "login.example.com"]}],
        },
    )

    assert tool.name == "httpx"


def test_tool_registry_selects_nmap_after_httpx_live_host_validation():
    tool = choose_next_tool(
        "discovery",
        {
            "target": "example.com",
            "evidence": [{"source": "httpx", "live_hosts": ["example.com", "api.example.com"], "urls": ["https://example.com", "https://api.example.com"]}],
        },
    )

    assert tool.name == "nmap"
