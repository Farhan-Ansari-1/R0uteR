"""Tool registry for the R0uteR security investigation workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDefinition:
    name: str
    purpose: str
    category: str
    allowed_targets: list[str] = field(default_factory=list)
    risk_level: str = "low"
    required_permission: str = "recon"
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    timeout: int = 180
    parser: str = "generic_parser"


class ToolRegistry:
    """Static registry of approved investigation tools."""

    def __init__(self) -> None:
        self.tools = [
            ToolDefinition(
                name="theHarvester",
                purpose="Gather public email and domain exposure",
                category="osint",
                allowed_targets=["domain", "approved_scope"],
                risk_level="low",
                required_permission="osint",
                input_schema={"target": "string", "query": "string"},
                output_schema={"emails": [], "hosts": [], "metadata": {}},
                timeout=120,
                parser="harvest_parser",
            ),
            ToolDefinition(
                name="amass-passive",
                purpose="Passive subdomain discovery and domain intelligence",
                category="osint",
                allowed_targets=["approved_domain"],
                risk_level="low",
                required_permission="osint",
                input_schema={"domain": "string"},
                output_schema={"subdomains": [], "sources": []},
                timeout=180,
                parser="amass_parser",
            ),
            ToolDefinition(
                name="subfinder",
                purpose="Subdomain enumeration",
                category="discovery",
                allowed_targets=["approved_domain"],
                risk_level="low",
                required_permission="recon",
                input_schema={"domain": "string"},
                output_schema={"subdomains": []},
                timeout=120,
                parser="subfinder_parser",
            ),
            ToolDefinition(
                name="httpx",
                purpose="Live host validation and HTTP service discovery",
                category="discovery",
                allowed_targets=["approved_domain", "approved_ip_range"],
                risk_level="low",
                required_permission="recon",
                input_schema={"targets": ["string"]},
                output_schema={"live_hosts": [], "urls": [], "technologies": []},
                timeout=180,
                parser="httpx_parser",
            ),
            ToolDefinition(
                name="nmap",
                purpose="Network reconnaissance and service discovery",
                category="network",
                allowed_targets=["approved_ip", "approved_network"],
                risk_level="medium",
                required_permission="recon",
                input_schema={"target": "string", "args": "string"},
                output_schema={"hosts": [], "ports": [], "services": [], "vulnerabilities": []},
                timeout=300,
                parser="nmap_parser",
            ),
            ToolDefinition(
                name="nuclei",
                purpose="Focused vulnerability scanning against discovered services",
                category="vulnerability",
                allowed_targets=["approved_ip", "approved_domain"],
                risk_level="medium",
                required_permission="vuln_scan",
                input_schema={"target": "string", "templates": ["string"]},
                output_schema={"findings": [], "matched_templates": []},
                timeout=600,
                parser="nuclei_parser",
            ),
            ToolDefinition(
                name="nvd_lookup",
                purpose="Public CVE and advisory correlation",
                category="intelligence",
                allowed_targets=["approved_scope"],
                risk_level="low",
                required_permission="intel",
                input_schema={"software": "string", "versions": ["string"]},
                output_schema={"cves": [], "advisories": []},
                timeout=120,
                parser="nvd_parser",
            ),
        ]

    def get_tool(self, name: str) -> ToolDefinition | None:
        for tool in self.tools:
            if tool.name.lower() == name.lower():
                return tool
        return None

    def by_category(self, category: str) -> list[ToolDefinition]:
        return [tool for tool in self.tools if tool.category.lower() == category.lower()]


def choose_next_tool(goal: str, context: dict[str, Any]) -> ToolDefinition:
    """Pick the next safe tool based on mission goal and available evidence."""
    target = str(context.get("target", "")).strip()
    findings = context.get("findings") or []
    registry = ToolRegistry()

    if findings:
        finding_text = " ".join(
            str(item).lower() for item in findings if isinstance(item, (str, dict))
        )
        if any(keyword in finding_text for keyword in ["http", "web", "service exposure", "apache", "nginx", "ssl", "login", "dashboard"]):
            return registry.get_tool("nuclei") or registry.tools[0]

    if goal.lower() == "osint":
        if target and any(ch.isdigit() for ch in target):
            return registry.get_tool("nmap") or registry.tools[0]
        return registry.get_tool("amass-passive") or registry.tools[0]

    if goal.lower() in {"recon", "discovery", "network"}:
        return registry.get_tool("nmap") or registry.tools[0]

    if goal.lower() in {"vuln", "vulnerability"}:
        return registry.get_tool("nuclei") or registry.tools[0]

    return registry.tools[0]
