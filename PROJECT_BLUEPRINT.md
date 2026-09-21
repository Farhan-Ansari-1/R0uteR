# R0uteR — Authorized Security Copilot Blueprint

## 1. Purpose

This project is not a general-purpose AI assistant.

It is being built as an ethical, permission-first offensive security copilot designed to work with an authorized Kali VM / lab environment and optionally with a VMware-based target setup.

The system must help a user:
- run reconnaissance against approved targets
- gather OSINT and public information in a limited, authorized scope
- execute safe security commands in a lab or VM-controlled environment
- summarize findings in plain English
- suggest the next investigation steps
- store notes, evidence, and command outputs for later review
- require approval before sensitive or destructive actions

This tool is meant for authorized testing, controlled red-team support, and ethical security research work only.

---

## 2. Core mission

The product must behave like a controlled execution assistant instead of an unrestricted tool API.

The AI is allowed to:
- interpret user intent
- choose safe task flow
- request permissions
- trigger approved commands
- summarize results
- recommend next steps

The AI is not allowed to:
- execute arbitrary commands without validation
- bypass approval gates
- operate outside the allowed scope
- target unauthorized hosts or systems
- perform destructive actions without explicit consent
- act as an uncontrolled shell executor

---

## 3. The actual problem we are solving

Security work is usually fragmented across many tools:
- recon is spread across multiple commands
- output parsing is manual
- follow-up steps are not obvious
- evidence is scattered
- OSINT and technical checks are often disconnected

We want a system that:
- reduces manual effort
- turns raw tool output into structured findings
- recommends the next move intelligently
- keeps all work inside an authorized environment
- stores notes, evidence, and generated summaries

---

## 4. Product direction

This project should become a focused security orchestration assistant with the following behavior:

### High-level capabilities
- receive a request like: “run recon on this IP and summarize the next steps”
- validate target scope
- check whether the user has permission
- run approved commands in the Kali environment
- parse the result
- identify visible services, open ports, and possible issues
- suggest the next phase of testing
- generate notes and summaries
- maintain a history of findings

### Not in scope for the first version
- voice assistant as the main workflow
- camera/screen automation as primary features
- general personal assistant functionality
- unrelated desktop automation
- broad all-in-one agentic chaos

---

## 5. Security principle: permissions, not raw tools

We are not exposing broad “tool APIs” to the AI.

We are exposing controlled capabilities.

The AI must ask for permissions like:
- command execution
- network recon
- OSINT lookup
- file access
- keyboard control
- mouse control
- Kali VM bridge
- destructive actions

Each capability should be bound to:
- allowed target list
- allowed environment
- required approval level
- audit logging
- operation timeout / scope limits

### Example permission model
- recon_permission: allowed only for approved targets
- web_research_permission: allowed only in research mode
- keyboard_control_permission: allowed only on lab VM desktop
- mouse_control_permission: allowed only within approved session
- destructive_action_permission: requires extra confirmation and should be default-denied

---

## 6. Execution model

The system should run in a bounded environment.

### Execution flow
1. User gives a task.
2. System identifies required capabilities.
3. System checks authorization and scope.
4. If a capability is disallowed, the system rejects it.
5. If permitted, the system triggers a safe command wrapper.
6. The command runs in the Kali environment or the lab bridge.
7. Output is captured and normalized.
8. AI summarizes findings.
9. AI suggests the next recommended phase.
10. Findings are saved to memory and notes.

This is a disciplined execution loop, not raw shell access.

---

## 7. Core components to keep

The following existing pieces are valuable foundation blocks:

- [R0uteR_GUI.py](R0uteR_GUI.py) — central app shell
- [modules/brain.py](modules/brain.py) — reasoning and orchestration
- [modules/security.py](modules/security.py) — security rules and validation
- [modules/approval.py](modules/approval.py) — approval gate
- [modules/lab_bridge.py](modules/lab_bridge.py) — Kali/VM bridge
- [modules/memory.py](modules/memory.py) — evidence and notes storage
- [modules/web.py](modules/web.py) — web research access
- [modules/automation.py](modules/automation.py) — automation wrapper layer

These need to be refocused, not discarded wholesale.

---

## 8. Components to reduce or remove from the first build

To keep the project controlled and buildable, we should initially cut or minimize the following:

- voice interaction as core feature
- camera and screen analysis as core feature
- broad general-purpose automation
- non-security desktop behavior
- personal assistant logic
- unnecessary persona system features
- random app-layer extras not needed for security execution

The goal is to produce a strong, targeted system, not a general AI appliance.

---

## 9. LLM strategy

We will start with Gemini for the main orchestration and reasoning layer.

Later, we will add local inference support via Ollama or similar local model runners.

### Why Gemini first
- good reasoning quality
- tool calling compatibility
- easier experimentation
- fast iteration for architecture and flow

### Why local LLM later
- privacy
- offline support
- no dependency on cloud API for every request
- reduce cost and improve resilience

### Final intended pattern
- Gemini for planning and deep reasoning
- local Gemma / Llama / Mistral model for lightweight summarization, extraction, notes, and fallback usage

---

## 10. Recommended project phases

### Phase 1 — Narrow the scope
- remove non-essential modules
- focus on security orchestration
- define strict usage rules
- define allowed environment and targets

### Phase 2 — Permission model
- build capability matrix
- add approval logic
- create safe command wrappers

### Phase 3 — VM integration
- connect to Kali VM securely
- execute approved commands
- capture outputs
- handle failures gracefully

### Phase 4 — Recon workflow
- host discovery
- port scanning
- service enumeration
- lightweight checks

### Phase 5 — OSINT and web research
- external/public intel gathering
- notes and summaries
- target background information

### Phase 6 — Findings summarization and recommendation engine
- parse results
- suggest next-step actions
- prioritize issues
- produce concise review

### Phase 7 — Local LLM support
- install and connect to Ollama models
- route summary/extraction tasks through local model
- maintain Gemini as primary orchestrator

### Phase 8 — Reporting and dashboard
- task logs
- evidence panel
- findings timeline
- report generation

---

## 11. Example user journey

User: “Router, run a recon on 192.168.1.20 and tell me what I should do next.”

System flow:
1. Check if target is allowed.
2. Check if user has recon permission.
3. Ensure environment is approved.
4. Run host discovery and port scan in Kali VM.
5. Parse open ports and services.
6. Run focused web or service checks if appropriate.
7. Pull public intel if approved.
8. Summarize findings.
9. Recommend next steps like web app testing, auth review, or service enumeration.
10. Save all evidence and findings in notes memory.

This kind of task should feel like a guided expert assistant, not a random command executor.

---

## 12. Rule set for the first version

The project must follow these rules:

1. No unrestricted command execution.
2. No unauthorized targets.
3. No dangerous actions without explicit approval.
4. All actions must be logged.
5. High-impact actions must require a separate confirmation.
6. Keyboard and mouse control must be scoped to the approved target/session.
7. The AI should not bypass the security model.
8. The system should be explainable.
9. The system should help the user understand reasoning and next steps.
10. Every finding should be stored with context and evidence.

---

## 13. Final recommendation

We should build a focused ethical pentest assistant using the existing codebase as a base.

The correct path is:
- keep the structure and parts that help with AI orchestration and lab integration
- remove unrelated general-purpose features
- create a robust permission system
- connect the system to a Kali VM
- use Gemini first, local LLM later
- build a controlled but capable offensive-security assistant

This will be stronger and more useful than a loose AI agent with a hundred disconnected capabilities.

---

## 14. First task after this note

The first task will be to clean the project toward a security-first architecture by:
- defining the project scope clearly
- identifying which modules are essential
- removing or minimizing non-essential features
- establishing the permission model
- preparing the base for Kali VM integration and command wrappers

This is the first concrete implementation milestone.
