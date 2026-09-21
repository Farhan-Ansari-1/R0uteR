# R0uteR security model

R0uteR is a supervised laptop copilot, not an unrestricted autonomous agent.
The language model can suggest actions, but local Python policy controls whether
an action may happen.

## Safe Mode (current)

- The model can search the web, inspect non-sensitive files and folders, report
  telemetry, and control media.
- Shell commands, arbitrary Python, UI typing/keypresses, clipboard reads,
  window closing, and WhatsApp messages remain blocked. File writes, Recycle
  Bin deletion, approved app launching, website opening, and copying generated
  text require a visible one-time UI approval which expires after 45 seconds.
- Windows folders, credentials, `.env` files, Git repositories, SSH keys, and
  R0uteR internal files are always blocked from model tools.
- Every block and approval request is recorded locally in `.r0uter/audit.jsonl`.
- Mouse-corner fail-safe is enabled for any future PyAutoGUI action.

## Approval workflow

The desktop UI shows the exact action and target. Only its **Approve once**
button can authorize the action. The approval is one-time, expires after 45
seconds, and destructive actions use the Recycle Bin. Model text alone never
counts as approval.
