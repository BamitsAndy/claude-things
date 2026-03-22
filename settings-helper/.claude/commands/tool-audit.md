---
description: One-time tool audit. Enumerates all tools in the current session and writes a markdown table + draft settings.json to .claude/. Run once, review outputs, configure permissions, reload Claude Code, then delete this command.
triggers: /tool-audit, "audit tools", "list available tools", "enumerate tools"
---

Perform a complete tool audit for this Claude Code session.

## Instructions

1. **Enumerate every tool** currently available in your context window — built-in Claude Code tools AND any MCP tools. Do not omit any tool, including tools you consider internal or rarely used.

2. **For each tool**, determine:
   - **Tool Name**: exact name as it would appear in a `settings.json` permission rule (e.g. `Read`, `Bash`, `mcp__github__create_issue`)
   - **Category**: one of `core-fs` | `core-shell` | `core-search` | `core-nav` | `agent` | `mcp-[server-name]` | `other`
   - **Type**: `builtin` or `mcp`
   - **Description**: one sentence — what this tool does
   - **Permission Pattern**: the pattern string to use in an allow/deny rule (e.g. `Bash(git *)`, `Read`, `mcp__github__*`)

3. **Write `.claude/TOOL_AUDIT.md`** (do not print to conversation — write the file directly). Use this exact structure:

```
# Tool Audit

Generated: [ISO date]
Session total: [N] tools ([N] builtin, [N] mcp)

## Tool Table

| Tool Name | Category | Type | Description | Permission Pattern |
|-----------|----------|------|-------------|-------------------|
| ... | ... | ... | ... | ... |

## Summary by Category

| Category | Count |
|----------|-------|
| ... | ... |

## How to Disable This Audit Command

When you no longer need to run tool audits, delete the command file:

```bash
rm .claude/commands/tool-audit.md
```

Then reload Claude Code. The `/tool-audit` command will no longer appear in autocomplete.
```

4. **Write `.claude/settings.json.draft`** with this structure, preserving the existing deny rules from the current `settings.json`:

```json
{
  "_comment": "Draft from /tool-audit on [date]. Review TOOL_AUDIT.md, edit this file, then rename to settings.json.",
  "permissions": {
    "deny": [
      "Bash(node *)",
      "Bash(node)",
      "Bash(npm *)",
      "Bash(npm)",
      "Bash(npx *)",
      "Bash(npx)",
      "Bash(bun *)",
      "Bash(bun)",
      "Bash(bunx *)",
      "Bash(bunx)",
      "Bash(pnpm *)",
      "Bash(pnpm)",
      "Bash(yarn *)",
      "Bash(yarn)",
      "Bash(deno *)",
      "Bash(deno)",
      "Bash(tsx *)",
      "Bash(tsx)",
      "Bash(ts-node *)",
      "Bash(ts-node)",
      "Bash(tsc *)",
      "Bash(tsc)",
      "Bash(vite *)",
      "Bash(vite)",
      "Bash(next *)",
      "Bash(next)",
      "Bash(nuxt *)",
      "Bash(nuxt)",
      "Bash(astro *)",
      "Bash(astro)",
      "Bash(wrangler *)",
      "Bash(wrangler)",
      "Bash(corepack *)",
      "Bash(corepack)"
    ],
    "allow": []
  }
}
```

5. After writing both files, respond to the user with a brief confirmation:
   - Paths of the two files written
   - Total tool count
   - How to proceed (review TOOL_AUDIT.md → edit settings.json.draft → rename to settings.json → reload Claude Code)
