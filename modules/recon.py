"""Reconnaissance parsing and recommendation utilities for the security-first R0uteR workflow."""

from __future__ import annotations

import re


def summarize_recon_output(raw_output: str, target: str) -> str:
    """Convert raw Nmap-like output into a concise security summary."""
    text = (raw_output or "").strip()
    if not text:
        return f"No reconnaissance output received for target {target}."

    ports = re.findall(r"(\d{1,5})/tcp\s+open\s+(\w+)", text, flags=re.IGNORECASE)
    services = []
    for port, service in ports:
        services.append(f"{port}/tcp -> {service}")

    unique_ports = sorted({port for port, _ in ports})
    unique_services = sorted({service.lower() for _, service in ports})
    open_service_text = " ".join(unique_services)

    summary_lines = [
        f"Target: {target}",
        f"Open ports: {', '.join(unique_ports) if unique_ports else 'none detected'}",
        f"Services: {', '.join(unique_services) if unique_services else 'none detected'}",
    ]

    if services:
        summary_lines.append("Visible services:")
        summary_lines.extend(f"- {item}" for item in services[:10])

    if "ssh" in open_service_text and "22" in unique_ports:
        summary_lines.append("Observation: SSH is exposed, so authentication and credential hygiene should be reviewed.")
    if any(service in {"http", "https", "http-proxy"} for service in unique_services):
        summary_lines.append("Observation: Web services are exposed; HTTP/HTTPS surface should be reviewed next.")

    return "\n".join(summary_lines)


def suggest_next_actions(*ports: str) -> list[str]:
    """Recommend the next security steps based on exposed ports."""
    port_list = {str(port).strip() for port in ports if str(port).strip()}
    actions: list[str] = []

    if "80" in port_list or "443" in port_list:
        actions.append("Review web service exposure on port 80/443 and inspect headers, TLS config, and app responses.")
        actions.append("Test authentication, session management, and default app paths on the exposed web surface.")

    if "22" in port_list:
        actions.append("Review SSH access, account lockout, and key-based authentication configuration on port 22.")

    if "3389" in port_list:
        actions.append("Check RDP exposure, account restrictions, and network controls on port 3389.")

    if not actions:
        actions.append("Inspect the discovered services and determine whether additional enumeration is needed for the exposed ports.")

    return actions
