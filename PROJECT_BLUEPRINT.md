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

This project should become a focused, ethical pentest orchestration assistant built around a real-world workflow:

- authorized target intake
- OSINT and public intel collection
- subdomain discovery
- recon and service enumeration
- vulnerability mapping
- AI-assisted finding summarization
- final report generation with evidence

The system should behave like a guided penetration testing assistant, not a general-purpose chatbot or unrestricted automation tool.

### High-level capabilities
- receive a request like: “recon this target, find subdomains, scan for services, and summarize the risk”
- validate scope and target authorization
- check user permission before running any sensitive action
- execute approved commands in the Kali VM / lab environment
- collect raw output from tools like Nmap, Nuclei, Amass, Subfinder, httpx, and OSINT tools
- parse structured results into findings
- summarize the results in plain English
- recommend the next phase of testing
- generate notes, evidence, and a final report

### Not in scope for the first version
- full autonomous “hack everything” behavior
- uncontrolled shell execution
- arbitrary personal device control
- unrestricted browser or desktop automation
- broad non-security assistant features
- keyboard/mouse control outside an explicitly approved lab session

---

## 5. Real pentest workflow we are targeting

The final architecture should follow a real, free-tool pentest pipeline.

### 1) OSINT and public intelligence
- theHarvester for email/domain exposure
- Amass in passive mode for domain and subdomain discovery
- Shodan free tier for public service discovery, where appropriate and allowed
- crt.sh / certificate transparency for certificate and domain history
- limited public web research using approved sources only

### 2) Subdomain enumeration
- Subfinder and Amass for discovery
- HTTPX for live host detection and service confirmation
- filter out dead or non-responsive hosts before deeper checks

### 3) Reconnaissance
- Nmap for port/service discovery
- service version detection and banner checks
- HTTP and TLS-related reconnaissance where relevant

### 4) Vulnerability discovery
- Nuclei with community templates
- output mapping for likely CVEs or vulnerability themes
- Nmap service signatures cross-checked with public CVE references (NVD / advisory feeds)

### 5) Risk prioritization
- severity grouping
- likely exploitability assessment
- exposure / reachability scoring
- next-step recommendations

### 6) Reporting and evidence
- evidence bundles
- JSON output for machine readability
- TXT summary for quick review
- PDF generation for the final human-readable report
- persistent findings log for review and traceability

This is the real product goal: a structured, authorized, intelligence-driven pentest workflow.

---

## 6. Security principle: permissions, not raw tools

We are not exposing broad “tool APIs” to the AI.

We are exposing controlled capabilities.

The AI must ask for permissions like:
- command execution
- network recon
- OSINT lookup
- file access
- Kali VM bridge
- keyboard control
- mouse control
- destructive actions

Each capability should be bound to:
- allowed target list
- approved lab or production scope
- required approval level
- audit logging
- timeout and restriction rules
- default-deny handling for high-risk actions

### Example permission model
- recon_permission: allowed only for approved targets
- osint_permission: allowed only for approved domain/IP scope
- vuln_scan_permission: allowed only in test or lab environment
- keyboard_control_permission: allowed only in the lab VM session and with explicit permission
- mouse_control_permission: allowed only within the controlled desktop session
- destructive_action_permission: must be explicitly confirmed and should remain default-denied

### Important boundary
Keyboard and mouse access are valid only when the target is a lab-controlled environment or explicitly authorized VM session. They are not a general remote-control feature for any system.

---

## 7. Execution model

The system should run in a bounded environment.

### Execution flow
1. User gives a task.
2. System validates target and scope.
3. System checks authorization and environment policy.
4. If a capability is disallowed, the system rejects it.
5. If permitted, the system triggers a safe wrapper around the command.
6. The command runs in the Kali environment or the lab bridge.
7. Output is captured and normalized.
8. AI summarizes the raw findings.
9. AI identifies likely risks and next recommended steps.
10. Findings are saved as evidence, notes, and final report assets.

This is a disciplined execution loop, not raw shell access.

---

## 8. Adaptive investigation loop (Agent Loop)

The most important missing component is the adaptive investigation loop.

The system should not behave like a single static task runner. It should behave like an agent that can decide:
- what evidence is missing
- which tool should run next
- whether the current result is sufficient to escalate
- whether the workflow should continue, stop, or request approval
- what the next high-value investigation step is

### Core idea
Given a target and a request, R0uteR should move through a closed-loop decision cycle:

1. Intake and authorize target scope
2. Select the next objective based on mission type and current evidence
3. Choose the safe tool or workflow for that objective
4. Run the tool through the proper lab/Kali bridge
5. Parse raw output into structured evidence
6. Update findings with severity, confidence, evidence, and status
7. Decide whether to continue, pivot, or stop
8. Recommend the next best action and record the rationale
9. Save evidence and update the report state

### Decision loop behavior
The agent loop should be adaptive, not hardcoded.

Example:
- user asks: “recon this target and identify exposed services”
- system validates the target
- system decides: host discovery → port scan → service detection
- after Nmap result, it may choose: HTTP checks or version checks
- if a high-value service is found, it may pivot to focused vuln discovery
- if a host is dead or filtered, it may stop early and mark it as inconclusive

### Loop contract
Each iteration must answer four questions:
- What is the current state?
- What evidence do we have?
- What missing fact is most valuable next?
- Which approved action is the safest next move?

This is the core of the “agent” behavior. Without this loop, the system only becomes a task wrapper instead of an investigation engine.

### State transitions
The system should track findings and workflow stages using a small finite state model, for example:
- queued
- authorized
- running
- parsed
- evidence_ready
- confirmed
- escalated
- blocked
- completed

This keeps reasoning explainable and prevents silent drift.

---

## 9. Finding model and evidence schema

The blueprint needs a formal finding structure. Severity alone is not enough. We need to distinguish between impact, confidence, proof, and lifecycle status.

### Recommended finding fields

```yaml
finding:
  id: string
  title: string
  category: string
  description: string
  severity: low | medium | high | critical
  confidence: low | medium | high
  evidence:
    - source: tool_or_command
      output_excerpt: string
      timestamp: ISO8601
      target: string
  status: new | confirmed | false_positive | mitigated | needs_review | blocked
  source_tool: string
  recommendation: string
  related_targets: []
  first_seen: ISO8601
  last_updated: ISO8601
```

### Severity vs confidence
These are different dimensions and must not be collapsed into one field.

- severity = how important or harmful the issue is if it is valid
- confidence = how strong the evidence is that the finding is real
- evidence = the source proof that supports the claim
- status = where the finding currently stands in the investigation lifecycle

Example:
- a service banner leak might be high severity but medium confidence if the evidence is weak
- a confirmed open SSH version disclosure may be medium severity but high confidence
- a suspected issue with weak evidence may remain “needs_review” until validated

### Why this matters
This allows the system to:
- separate impact from reliability
- avoid over-reporting low-confidence findings
- explain why a recommendation was made
- generate a trustworthy final report for review

---

## 10. Tool Registry

The architecture needs an explicit Tool Registry so the AI does not decide arbitrarily which command to run.

Each tool should be defined as a controlled capability with clear constraints and metadata.

```yaml
tool_registry:
  - name: theHarvester
    purpose: email, domain, and public exposure discovery
    category: osint
    allowed_targets:
      - domain
      - approved_scope
    risk_level: low
    required_permission: osint
    input_schema:
      target: string
      query: string
    output_schema:
      emails: []
      hosts: []
      metadata: {}
    timeout: 120
    parser: harvest_parser

  - name: amass-passive
    purpose: passive subdomain discovery and domain intelligence
    category: osint
    allowed_targets:
      - approved_domain
    risk_level: low
    required_permission: osint
    input_schema:
      domain: string
    output_schema:
      subdomains: []
      sources: []
    timeout: 180
    parser: amass_parser

  - name: subfinder
    purpose: subdomain enumeration
    category: discovery
    allowed_targets:
      - approved_domain
    risk_level: low
    required_permission: recon
    input_schema:
      domain: string
    output_schema:
      subdomains: []
    timeout: 120
    parser: subfinder_parser

  - name: httpx
    purpose: live host validation and HTTP service discovery
    category: discovery
    allowed_targets:
      - approved_domain
      - approved_ip_range
    risk_level: low
    required_permission: recon
    input_schema:
      targets: []
    output_schema:
      live_hosts: []
      urls: []
      technologies: []
    timeout: 180
    parser: httpx_parser

  - name: nmap
    purpose: network reconnaissance and service discovery
    category: network
    allowed_targets:
      - approved_ip
      - approved_network
    risk_level: medium
    required_permission: recon
    input_schema:
      target: string
      args: string
    output_schema:
      hosts: []
      ports: []
      services: []
      vulnerabilities: []
    timeout: 300
    parser: nmap_parser

  - name: nuclei
    purpose: vulnerability scanning against discovered services
    category: vulnerability
    allowed_targets:
      - approved_ip
      - approved_domain
    risk_level: medium
    required_permission: vuln_scan
    input_schema:
      target: string
      templates: []
    output_schema:
      findings: []
      matched_templates: []
    timeout: 600
    parser: nuclei_parser

  - name: nvd_lookup
    purpose: public CVE and advisory correlation
    category: intelligence
    allowed_targets:
      - approved_scope
    risk_level: low
    required_permission: intel
    input_schema:
      software: string
      versions: []
    output_schema:
      cves: []
      advisories: []
    timeout: 120
    parser: nvd_parser
```

### Registry fields
Each tool entry should include:
- name
- purpose
- category
- allowed_targets
- risk_level
- required_permission
- input_schema
- output_schema
- timeout
- parser

### Why this is necessary
Without a Tool Registry, the system is just a loose set of prompts and shell commands. With a registry, the system becomes policy-aware, auditable, and repeatable.

The registry allows the agent to:
- choose the next tool by objective and risk
- reject dangerous or out-of-scope actions
- parse output consistently across tools
- maintain evidence symmetry and auditability

---

## 11. Core components to keep

The following modules are valuable foundation blocks:

- [R0uteR_GUI.py](R0uteR_GUI.py) — app shell and user flow
- [modules/brain.py](modules/brain.py) — reasoning and orchestration
- [modules/security.py](modules/security.py) — safety gates and validation
- [modules/approval.py](modules/approval.py) — approval workflow
- [modules/lab_bridge.py](modules/lab_bridge.py) — Kali + lab execution bridge
- [modules/memory.py](modules/memory.py) — evidence and notes storage
- [modules/web.py](modules/web.py) — web research access
- [modules/automation.py](modules/automation.py) — automation wrapper layer
- [modules/recon.py](modules/recon.py) — result parsing and summarization
- [modules/reporting.py](modules/reporting.py) — report generation

These need to be expanded and refocused, not discarded.

---

## 12. Free-tool pipeline and AI role

This project should use a free and practical stack.

### Free toolchain
- OSINT: theHarvester, Amass (passive), crt.sh, free-tier Shodan lookup when allowed
- Subdomains: Subfinder, Amass, httpx
- Recon: Nmap
- Vulnerability scanning: Nuclei
- NVD cross-check: NVD API / public advisory matching
- Reporting: local report generation (TXT / JSON / PDF)

### AI usage: where it is useful
AI should not replace the scanner. It should make the scanner output more useful.

The best use of AI here is:
- summarize noisy Nmap/Nuclei output
- extract the most relevant findings
- rank them by severity and impact
- suggest the next action in plain English
- turn raw technical output into a clean final report

### Why this is the right AI role
- raw tool output is noisy and verbose
- many results are low-value unless interpreted
- a human-readable summary is the real product value
- structured parsing is more reliable than prompting the model to directly “hack” a system

### Local LLM strategy
- Gemini or another hosted model can be used for deeper reasoning and planning
- local Ollama models such as Gemma 4:e4b are excellent for summarization, extraction, and fallback usage
- the local model should be treated as a lightweight summary layer, not as a raw command executor

This is realistic, free-friendly, and aligned with the actual workflow of a human pentester.

---

## 13. Recommended project phases

### Phase 1 — Hardening and scope lock
- remove unrelated app features
- keep only the security automation stack
- draw clear boundaries around approved targets and environment

### Phase 2 — Permission system
- build capability matrix
- define approval rules for recon, OSINT, and vuln scanning
- allow keyboard/mouse control only inside a lab-controlled session

### Phase 3 — Kali and lab bridge
- connect securely to Kali VM
- run safe command wrappers
- capture output and errors reliably
- log every execution step

### Phase 4 — OSINT and subdomain flow
- gather domain and public intel
- perform passive discovery
- validate live endpoints
- store raw evidence and notes

### Phase 5 — Reconnaissance workflow
- host discovery
- port scanning
- service enumeration
- version detection

### Phase 6 — Vulnerability workflow
- run Nuclei templates
- resolve service-to-vuln mapping
- cross-check findings with public CVE data
- rank issues by impact and reliability

### Phase 7 — AI summarization and recommendation engine
- summarize raw output
- convert findings into structured evidence
- propose next investigation steps by priority

### Phase 8 — Reporting and evidence bundle
- JSON + TXT + PDF export
- findings timeline and notes
- final human-readable report for review

---

## 14. Example user journey

User: “This target is mine and authorized. Run OSINT, subdomain discovery, recon, vulnerability checks, and give me a clean final report.”

System flow:
1. Validate target is in the allowed list.
2. Check if the user has valid recon and OSINT permissions.
3. Confirm the environment is the approved Kali or lab VM.
4. Run passive OSINT and subdomain discovery.
5. Validate live hosts and analyze open ports.
6. Run Nmap and service enumeration.
7. Run focused Nuclei templates and cross-check results.
8. Extract findings and summarize them with AI.
9. Rank findings by severity and recommended next step.
10. Save evidence and generate the final report bundle.

This should feel like a disciplined pentest workflow guided by a security-aware assistant, not a chaotic autonomous agent.

---

## 15. Final design principle

The product should not attempt to “replace a person.”

It should act like a strong, controlled pentest co-pilot that:
- works with authorized targets only
- operates within a safe execution environment
- uses free open-source tooling
- uses AI for interpretation, summarization, and prioritization
- keeps a full evidence trail
- produces a clean report in plain English

That is the right balance between automation, ethics, usefulness, and real-world practicality.
