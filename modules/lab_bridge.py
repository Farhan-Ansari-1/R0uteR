"""Secure SSH Bridge to the Kali Linux VM for authorized lab security operations."""

from __future__ import annotations

import ipaddress
import os
import re
import shlex
from pathlib import Path
from urllib.parse import urlparse
import paramiko
from dotenv import load_dotenv

from .security import audit_event, require_user_approval

load_dotenv()

RECON_TASKS = {
    "nmap": {"description": "Custom bounded Nmap scan", "binary": "nmap"},
    "masscan": {"description": "Custom bounded Masscan scan", "binary": "masscan"},
    "ping": {"description": "Single ICMP reachability check", "binary": "ping"},
    "nmap_top_ports": {"description": "Nmap fast top-port scan", "binary": "nmap"},
    "service_scan": {"description": "Nmap service and default-script scan", "binary": "nmap"},
}
ALLOWED_RECON_TASKS = set(RECON_TASKS)

_SAFE_ARGUMENT = re.compile(r"^[A-Za-z0-9_./:+=-]+$")
_NMAP_FLAGS_WITH_VALUES = {"--top-ports", "-p", "--min-rate", "--max-rate", "-T"}
_MASSCAN_FLAGS_WITH_VALUES = {"--ports", "-p", "--rate"}


def _validate_extra_args(task_name: str, extra_args: str) -> tuple[bool, str]:
    """Allow only option-shaped arguments with simple scalar values."""
    value = (extra_args or "").strip()
    if not value:
        return True, ""
    if any(character in value for character in ";|&>$`\n\r"):
        return False, "Extra arguments contain blocked shell syntax."

    try:
        tokens = shlex.split(value, posix=True)
    except ValueError:
        return False, "Extra arguments contain invalid quoting."

    expects_value = False
    allowed_value_flags = (
        _MASSCAN_FLAGS_WITH_VALUES if task_name == "masscan" else _NMAP_FLAGS_WITH_VALUES
    )
    for token in tokens:
        if not _SAFE_ARGUMENT.fullmatch(token):
            return False, f"Extra argument '{token}' contains unsupported characters."
        if expects_value:
            if token.startswith("-"):
                return False, "An option value is missing or malformed."
            expects_value = False
            continue
        if not token.startswith("-"):
            return False, "Extra arguments may contain options only, not extra targets."
        if token in allowed_value_flags:
            expects_value = True
    if expects_value:
        return False, "An option value is missing."
    return True, ""


def _build_recon_command(task_name: str, target: str, extra_args: str = "") -> tuple[bool, str]:
    task_key = task_name.lower()
    valid_args, reason = _validate_extra_args(task_key, extra_args)
    if not valid_args:
        return False, reason

    if task_key == "nmap":
        return True, f"nmap {extra_args} {target}".strip()
    if task_key == "nmap_top_ports":
        return True, f"nmap -F {target}".strip()
    if task_key == "ping":
        return True, f"ping -c 1 {target}".strip()
    if task_key == "service_scan":
        return True, f"nmap -sV -sC {target}".strip()
    if task_key == "masscan":
        return True, f"masscan {extra_args} {target}".strip()
    return False, f"Task '{task_name}' is recognized but not mapped to an execution command."


def _validate_allowed_task(task_name: str) -> tuple[bool, str]:
    cleaned = (task_name or "").strip().lower()
    if not cleaned:
        return False, "Task name cannot be empty."
    if cleaned not in ALLOWED_RECON_TASKS:
        return False, (
            f"Unsupported task '{task_name}'. Allowed tasks: {', '.join(sorted(ALLOWED_RECON_TASKS))}."
        )
    return True, cleaned

# Destructive or forkbomb commands strictly blocked inside VM bridge
DANGEROUS_VM_PATTERNS = [
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+/(?:$|\s|\*)",
    r"\bmkfs\b",
    r"\bdd\s+if=.*of=/dev/[sh]d[a-z]",
    r":\(\)\s*\{\s*:\|:&\s*\};:",
    r"\bchmod\s+-R\s+777\s+/(?:$|\s)",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+0\b",
]


def _get_vm_config() -> dict[str, str | int]:
    return {
        "host": os.getenv("KALI_VM_HOST", "127.0.0.1").strip(),
        "port": int(os.getenv("KALI_VM_PORT", "22").strip()),
        "user": os.getenv("KALI_VM_USER", "kali").strip(),
        "password": os.getenv("KALI_VM_PASSWORD", "kali").strip(),
        "key_path": os.getenv("KALI_VM_KEY_PATH", "").strip(),
    }


def _get_authorized_targets() -> list[str]:
    raw = os.getenv("ROUTER_LAB_TARGETS", "localhost,127.0.0.1,::1,192.168.1.0/24,192.168.56.0/24")
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def is_authorized_target(target: str) -> bool:
    """Checks whether the specified target IP or hostname is inside authorized lab scope."""
    target = (target or "").strip()
    if not target:
        return True  # Local commands on Kali itself

    parsed = urlparse(target if "://" in target else f"//{target}")
    host = (parsed.hostname or target).lower().strip("[]")

    # Local loopback check
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True

    allowed_entries = _get_authorized_targets()
    for entry in allowed_entries:
        if entry == host:
            return True
        # Check if entry is a CIDR network (e.g. 192.168.56.0/24)
        if "/" in entry:
            try:
                network = ipaddress.ip_network(entry, strict=False)
                target_ip = ipaddress.ip_address(host)
                if target_ip in network:
                    return True
            except ValueError:
                continue

    return False


def _create_ssh_client() -> paramiko.SSHClient:
    cfg = _get_vm_config()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs = {
        "hostname": cfg["host"],
        "port": cfg["port"],
        "username": cfg["user"],
        "timeout": 10,
    }

    if cfg["key_path"] and os.path.isfile(cfg["key_path"]):
        connect_kwargs["key_filename"] = cfg["key_path"]
    elif cfg["password"]:
        connect_kwargs["password"] = cfg["password"]

    client.connect(**connect_kwargs)
    return client


def test_vm_connection() -> str:
    """
    Tests the SSH connection to the configured Kali Linux VM.
    Returns hostname, kernel version, and IP addresses.
    """
    cfg = _get_vm_config()
    try:
        client = _create_ssh_client()
        _, stdout, stderr = client.exec_command("whoami && uname -sr && hostname -I", timeout=10)
        output = stdout.read().decode("utf-8", errors="replace").strip()
        client.close()
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        user = lines[0] if len(lines) > 0 else "unknown"
        kernel = lines[1] if len(lines) > 1 else "unknown"
        ips = lines[2] if len(lines) > 2 else "unknown"

        audit_event("vm_connection_test", "success", str(cfg["host"]))
        return (
            f"✅ KALI VM LINK ONLINE\n"
            f"- Host: {cfg['host']}:{cfg['port']}\n"
            f"- User: {user}\n"
            f"- Kernel: {kernel}\n"
            f"- VM IP(s): {ips}\n"
            f"- Lab Targets: {', '.join(_get_authorized_targets())}"
        )
    except Exception as error:
        audit_event("vm_connection_test", "failed", str(cfg["host"]), str(error))
        return (
            f"❌ KALI VM LINK FAILED\n"
            f"Could not connect to {cfg['user']}@{cfg['host']}:{cfg['port']}\n"
            f"Error: {error}\n\n"
            "Please check:\n"
            "1. VMware / VirtualBox Kali VM is powered on.\n"
            "2. OpenSSH server is running on Kali ('sudo systemctl start ssh').\n"
            "3. Host and credentials match in your local .env file."
        )


def execute_lab_command(command: str, target: str = "") -> str:
    """
    Executes an authorized security or reconnaissance command inside the Kali Linux VM.
    Args:
        command (str): The bash command to execute (e.g., 'nmap -sV 192.168.56.101').
        target (str): Target IP or hostname (must be in authorized lab scope).
    """
    command = (command or "").strip()
    if not command:
        return "Command cannot be empty."

    # 1. Target scope validation
    if target and not is_authorized_target(target):
        audit_event("vm_lab_command", "blocked_out_of_scope", target, command)
        return (
            f"⛔ TARGET OUT OF LAB SCOPE: '{target}' is not in authorized ROUTER_LAB_TARGETS.\n"
            "Only local lab networks and authorized test targets are permitted."
        )

    # 2. Check for destructive command patterns
    for pattern in DANGEROUS_VM_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            audit_event("vm_lab_command", "blocked_dangerous", target, command)
            return "⛔ BLOCKED: Destructive or system-crashing command pattern detected."

    # 3. User approval required via desktop UI
    preview = f"[Kali VM] {command[:100]}"
    approved, message = require_user_approval("vm_lab_command", preview)
    if not approved:
        return message

    # 4. Execute via Paramiko SSH
    cfg = _get_vm_config()
    try:
        client = _create_ssh_client()
        audit_event("vm_lab_command", "executing", target, command)
        _, stdout, stderr = client.exec_command(command, timeout=90)
        out_text = stdout.read().decode("utf-8", errors="replace")
        err_text = stderr.read().decode("utf-8", errors="replace")
        client.close()

        output = (out_text + err_text).strip()
        output = output[-12000:] if output else "Command completed with no output."
        audit_event("vm_lab_command", "success", target, command)
        return f"=== KALI LAB EXECUTION ===\n$ {command}\n\n{output}"
    except paramiko.SSHException as error:
        audit_event("vm_lab_command", "ssh_error", target, str(error))
        return f"SSH Execution Error: {error}"
    except Exception as error:
        audit_event("vm_lab_command", "error", target, str(error))
        return f"Lab Command Error: {error}"


def get_lab_status() -> str:
    """Returns the current Kali VM lab configuration and authorized target scope."""
    cfg = _get_vm_config()
    targets = ", ".join(_get_authorized_targets())
    return (
        f"LAB STATUS CONFIGURATION:\n"
        f"- Target VM: {cfg['user']}@{cfg['host']}:{cfg['port']}\n"
        f"- Authorized Targets Scope: {targets}\n"
        f"- Bridge Auth: {'Key-based' if cfg['key_path'] else 'Password'}"
    )


def run_recon_task(task_name: str, target: str, extra_args: str = "") -> str:
    """Execute a bounded reconnaissance command inside the Kali VM."""
    task_ok, task_msg = _validate_allowed_task(task_name)
    if not task_ok:
        return task_msg

    if target and not is_authorized_target(target):
        audit_event("recon_task", "blocked_out_of_scope", target, task_name)
        return f"Target '{target}' is not in authorized scope for this task."

    approved, message = require_user_approval("recon_task", f"{task_name}:{target}")
    if not approved:
        return message

    command_ok, cmd_or_reason = _build_recon_command(task_name.lower(), target, extra_args)
    if not command_ok:
        audit_event("recon_task", "blocked_invalid_arguments", target, cmd_or_reason)
        return cmd_or_reason
    cmd = cmd_or_reason

    try:
        client = _create_ssh_client()
        _, stdout, stderr = client.exec_command(cmd, timeout=120)
        output = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        client.close()
        combined = (output + err).strip()
        if not combined:
            combined = "Command completed with no output."
        return f"=== RECON TASK: {task_name.upper()} ===\nTarget: {target}\nCommand: {cmd}\n\n{combined}"
    except Exception as error:
        audit_event("recon_task", "error", target, str(error))
        return f"Recon task execution failed: {error}"
