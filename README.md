# R0uteR — Authorized Security Copilot

## Overview

R0uteR is being built as an ethical, permission-first offensive security assistant for controlled environments.

The project is designed around one key principle:

- no raw tool API access
- no unrestricted shell execution
- only scoped, approved actions
- target and task validation before execution
- structured findings, evidence, and next-step guidance

This is not a general-purpose assistant. It is a security copilot focused on authorized reconnaissance, evidence capture, and guided next-step recommendations.

---

## Core idea

The system is meant to work like this:

1. User provides a target and a task
2. The system validates scope and permission
3. Only approved tasks are allowed
4. The task is executed in the authorized Kali/VM environment
5. Results are parsed and summarized
6. Recommended next steps are generated
7. Findings are saved as evidence
8. A final report is produced

---

## Mission

R0uteR aims to become a safe, bounded security workflow assistant that can:

- run recon tasks against authorized targets
- summarize open ports and visible services
- generate next-step recommendations
- store findings as structured evidence
- support local and cloud LLM usage
- keep all execution under approval and scope enforcement

---

## Current architecture

The project currently includes these working layers:

- permission gateway: [modules/permissions.py](modules/permissions.py)
- safety policy: [modules/security.py](modules/security.py)
- approval layer: [modules/approval.py](modules/approval.py)
- VM bridge: [modules/lab_bridge.py](modules/lab_bridge.py)
- recon parsing: [modules/recon.py](modules/recon.py)
- orchestration flow: [modules/orchestrator.py](modules/orchestrator.py)
- evidence storage: [modules/evidence.py](modules/evidence.py)
- reporting: [modules/reporting.py](modules/reporting.py)
- OSINT wrapper: [modules/osint.py](modules/osint.py)
- LLM abstraction: [modules/llm_adapter.py](modules/llm_adapter.py)
- CLI entrypoint: [cli.py](cli.py)
- interactive menu: [modules/menu.py](modules/menu.py)
- mission workflow: [modules/missions.py](modules/missions.py)

---

## Security model

The system intentionally follows a permission-first design.

Allowed behavior:

- narrow recon on approved targets
- bounded OSINT research in approved scope
- evidence capture and report generation
- safe command wrappers
- explicit human approval for sensitive tasks

Blocked by design:

- unrestricted terminal execution
- destructive actions without approval
- unauthorized target execution
- broad system-level automation outside scope

---

## Example usage

### CLI mode

```bash
python cli.py --target 127.0.0.1 --task nmap --args "-sV --top-ports 20"
```

Each successful CLI mission prints the report in the terminal and writes an output bundle to `reports/`:

- `*_report.pdf` — final shareable report
- `*_report.txt` — plain-text version
- `*_evidence.json` — structured finding and metadata
- `*_raw.txt` — raw Kali command output

The searchable history is also stored in `r0uter_evidence.db`. Use the interactive menu to review saved evidence.

### Interactive mode

```bash
python -c "from modules.menu import show_menu; show_menu()"
```

### Local Ollama review

Ollama is optional and is used only to review the deterministic recon summary.
It cannot select targets, bypass permissions, or execute Kali commands.

```env
ROUTER_AI_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434/api/chat
OLLAMA_MODEL=gemma4:e4b
OLLAMA_TIMEOUT_SECONDS=120
```

With these settings, the CLI adds a `Local model review` section to the report.
If Ollama is unavailable, the original deterministic evidence remains available.

---

## Ethical usage

This project is intended only for:

- authorized lab use
- training and controlled testing
- internal security review
- approved engagement environments

It must not be used on systems or targets outside explicit permission.

---

## Current status

This project is in a focused MVP/core development stage.

It is not a generic AI assistant and not a full exploit framework. It is a structured, rule-based security copilot foundation built for authorized reconnaissance and guided testing work.

---

## Future roadmap

Planned next steps:

- richer task registry for additional recon actions
- stronger OSINT integration
- real local LLM provider integration such as Ollama
- mission templates and more guided workflows
- dashboard or TUI polish

---

## Note

The project intentionally keeps its scope narrow and controlled to remain safe, explainable, and useful. The emphasis is on governance, evidence, and guidance rather than unrestricted automation.
