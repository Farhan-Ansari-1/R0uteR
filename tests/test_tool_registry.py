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
