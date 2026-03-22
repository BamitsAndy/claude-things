# Tool Audit — Usage Guide

## Why

Claude Code's `settings.json` permissions (allow/deny lists) control which tools Claude can invoke. Before configuring these, you need to know what tools are actually available in your session — built-in tools, MCP servers, and any deferred tools.

The `/tool-audit` command solves this: it asks Claude to enumerate every tool in its context window and write a structured audit file. You review the output, decide your allow/deny strategy, apply it to `settings.json`, then remove the command.

---

## Workflow

### 1. Run the audit

In a Claude Code session, type:

```
/tool-audit
```

Claude will write two files and confirm when done:

| File | Contents |
|------|----------|
| `.claude/TOOL_AUDIT.md` | Markdown table of all tools + category summary |
| `.claude/settings.json.draft` | Draft permissions with existing denials preserved |

### 2. Review `.claude/TOOL_AUDIT.md`

Open the file and scan the table. For each tool, you'll see:

- **Tool Name** — exact identifier
- **Category** — `core-fs`, `core-shell`, `core-search`, `core-nav`, `agent`, `mcp-[server]`, `other`
- **Type** — `builtin` or `mcp`
- **Description** — what the tool does
- **Permission Pattern** — the string to use in a deny/allow rule

Decide which tools you want to restrict. Common strategies:
- **Deny by runtime**: block `Bash(node *)`, `Bash(python *)` etc. if you don't want Claude executing those
- **Deny by tool**: block `Bash(*)` entirely and only allow specific patterns
- **Allow MCP only**: use `--allow-mcp` with the Python script (see below)

### 3. Edit `.claude/settings.json.draft`

Open `.claude/settings.json.draft` and add your deny/allow rules based on what you found in the audit. The draft already contains the project's existing denials.

Example additions:

```json
{
  "permissions": {
    "deny": [
      "Bash(node *)",
      "mcp__github__delete_repo"
    ],
    "allow": [
      "mcp__github__create_issue",
      "mcp__github__list_prs"
    ]
  }
}
```

### 4. Apply the configuration

When satisfied with the draft, rename it to replace (or merge into) `settings.json`:

```bash
# Replace entirely
mv .claude/settings.json.draft .claude/settings.json

# Or merge manually if settings.json has other fields you want to keep
```

### 5. Reload Claude Code

Close and reopen the Claude Code session. The new permissions take effect immediately on reload.

### 6. Disable the audit command

The `/tool-audit` command is only needed once. Remove it to keep your command list clean:

```bash
rm .claude/commands/tool-audit.md
```

Reload Claude Code again. `/tool-audit` will no longer appear in autocomplete.

---

## Python Post-Processor (Offline)

If you want to process the audit file programmatically — without running a new Claude session — use the companion script:

```bash
python scripts/process_audit.py --input .claude/TOOL_AUDIT.md [MODE]
```

### Modes

| Mode | Output |
|------|--------|
| `--summary` | Tool count by category |
| `--emit-json` | Full draft `settings.json` (deny/allow both empty — you fill in) |
| `--deny-all` | settings.json with every tool in the deny list |
| `--allow-mcp` | settings.json with only MCP tools in the allow list |

### Examples

```bash
# See what categories of tools were found
python scripts/process_audit.py --summary

# Generate a draft to stdout (pipe through json.tool to validate)
python scripts/process_audit.py --emit-json | python -m json.tool

# Build an allow-list for MCP tools only, save to file
python scripts/process_audit.py --allow-mcp > .claude/settings.json.draft
```

### Running tests

```bash
pytest tests/test_process_audit.py -v
```

---

## File Reference

| File | Purpose |
|------|---------|
| `.claude/commands/tool-audit.md` | The slash command (delete when done) |
| `.claude/TOOL_AUDIT.md` | Generated audit — tool table + category summary |
| `.claude/settings.json.draft` | Generated draft permissions |
| `.claude/settings.json` | Live permissions (you manage this manually) |
| `scripts/process_audit.py` | Offline parser/emitter |
| `tests/test_process_audit.py` | Tests for the Python script |
