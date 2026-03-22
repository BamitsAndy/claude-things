# Planning Prompts

---

## 2026-03-20 — Tool Audit Feature

When starting a new Claude Code project, users need to configure `settings.json` permissions (allow/deny lists) to control which tools Claude can use. Currently there's no easy way to discover which tools are available in a session before deciding what to permit or block.

Add a `/tool-audit` command that instructs Claude to enumerate all available tools from its own context and write a structured markdown table + draft `settings.json` to the project. It's a one-time setup activity: run it, review the output, configure permissions, reload Claude Code, then remove the command.
