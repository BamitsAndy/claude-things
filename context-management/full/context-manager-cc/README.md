# context-manager-cc

Context reduction for Claude Code via `permissions.deny`.

Advanced tools (`WebFetch`, `WebSearch`, MCP tools) are removed from Claude's
context by default. Claude can ask the user to approve them mid-session; they
become available on the next restart after running `--sync`.

---

## How it works

`settings.json → permissions.deny` removes tool schemas entirely from the
model's context window — unlike `permissions.ask`, which gates execution but
still sends the schemas. Fewer schemas = fewer tokens every turn.

A CLAUDE.md block tells Claude which tools exist but are currently unavailable,
so it can recognise when it needs one and request approval.

---

## Quickstart

```bash
# Install into a project
cd my-project
python /path/to/context-manager-cc/install.py --target .

# Install globally (all projects)
python /path/to/context-manager-cc/install.py --global
```

Then open the project in Claude Code. Advanced tools will be absent from context.

---

## Approval workflow

1. Claude needs WebFetch for a task.
2. Claude tells you: "I need WebFetch — may I use it?"
3. You say yes.
4. Claude writes `WebFetch` into `.claude/context-manager-cc/memory.json`.
5. You run:
   ```bash
   python install.py --sync --target .
   ```
6. Restart Claude Code. `WebFetch` is now in `permissions.allow` and in context.

---

## Commands

| Command | Description |
|---------|-------------|
| `python install.py` | First-time setup in current directory |
| `python install.py --target /path` | First-time setup for a specific project |
| `python install.py --global` | Install to `~/.claude/` for all projects |
| `python install.py --sync` | Re-sync settings from memory.json (run after approvals) |
| `python install.py --sync --target /path` | Sync for a specific project |

---

## Files created in target project

```
<project>/
├── CLAUDE.md                          ← tool catalogue block appended
└── .claude/
    ├── settings.json                  ← deny list written here
    └── context-manager-cc/
        ├── tools.json                 ← tier registry (copy of config/tools.json)
        └── memory.json                ← {"approved_tools": [...]}
```

---

## Tool tiers (config/tools.json)

| Tier | Default behaviour | Tools |
|------|------------------|-------|
| `simple` | Always available | Read, Write, Glob, Grep, Edit, Bash, AskUserQuestion, ExitPlanMode, Task* |
| `advanced` | Denied by default | WebFetch, WebSearch |

Add `mcp__*` tool names as `"tier": "advanced"` entries to deny them too.

---

## Overriding tiers per-project

Edit `.claude/context-manager-cc/tools.json` in the target project to change a
tool's tier, then run `--sync`. The installer never overwrites an existing
`tools.json` after initial setup (only `memory.json` is preserved; `tools.json`
is always refreshed on install but kept on `--sync`).

---

## Running tests

```bash
cd context-manager-cc
python -m pytest tests/test_settings_manager.py -v
```

---

## Comparison with context-manager-api

| Aspect | context-manager-api | context-manager-cc |
|--------|--------------------|--------------------|
| Mechanism | Controls `tools` array per request | `permissions.deny` removes schemas |
| Token savings | ~70% per turn (measured) | Proportional to denied tool count |
| Entry point | `python claude_chat.py` (chat loop) | `python install.py` (one-time setup) |
| Approval activates | Same turn | Next session (after `--sync`) |
| Approval UX | Interactive y/n prompt | Claude asks → writes memory.json |
