# Plan: context-manager-cc — Context Reduction for Claude Code

## Context

`context-manager-api` reduces token usage by controlling the `tools` array sent per API request — only approved tool schemas are included. The user now wants a **parallel tool for Claude Code** (the CLI/VS Code IDE), using Claude Code's native mechanisms to achieve the same goal.

**Key insight:** `settings.json → permissions.deny` removes tool schemas from Claude Code's context entirely — the model never receives their token-expensive definitions. `permissions.ask` gates execution but does NOT save tokens (schemas still sent). So `deny` is the correct lever for context reduction.

**The gap:** A tool in `deny` is invisible to the model mid-conversation (not in the tools array). CLAUDE.md bridges this: a compact tool catalogue tells Claude which tools exist but are currently denied, so Claude can recognise when it needs one and ask the user.

**Approval workflow:** User approves → Claude writes to `memory.json` → user runs `install.py --sync` (or restarts) → settings.json is regenerated with the tool moved from `deny` to `allow`. The tool is available next session with full context saved in the meantime.

**Primary value:** Token savings via deny list.
**Bonus value:** Explicit user consent before advanced tools enter context.

---

## Architecture

```
context-manager-cc/
├── install.py              ← entry point: setup + --sync to regenerate settings
├── README.md
├── config/
│   ├── CLAUDE.md           ← CLAUDE.md snippet (appended to target project)
│   ├── tools.json          ← tier registry (same format as API version)
│   └── memory.json         ← initial state template: {"approved_tools": []}
├── core/
│   ├── __init__.py
│   ├── tool_loader.py      ← reads tools.json, returns simple/advanced sets
│   ├── settings_manager.py ← reads/writes .claude/settings.json (deny/allow lists)
│   └── installer.py        ← initial setup: CLAUDE.md append, memory init, settings patch
└── tests/
    └── test_settings_manager.py ← unit tests
```

Installed into a target project, it creates/modifies:
```
<target-project>/
├── CLAUDE.md               ← appended with tool catalogue + approval protocol
└── .claude/
    ├── settings.json       ← advanced tools added to permissions.deny
    └── context-manager-cc/
        └── memory.json     ← {"approved_tools": []} — grows as user approves tools
```

---

## Tool Tiers (`config/tools.json`)

Same `tier` format as the API version. Claude Code tool names:

**Simple** (always in `allow` / not denied): `Read`, `Write`, `Glob`, `Grep`, `Edit`, `AskUserQuestion`, `ExitPlanMode`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `TaskStop`, `Bash` for basic commands*

**Advanced** (added to `permissions.deny` by default): `WebFetch`, `WebSearch`, plus any `mcp__*` tools

> *Bash can be simple or advanced depending on user preference. The config should support overriding tiers per-project.

The same `tier` field is used — tool_loader.py filters by tier, settings_manager.py applies the deny list from the advanced set minus whatever is in `approved_tools`.

---

## CLAUDE.md Template (`config/CLAUDE.md`)

Appended to the target project's `CLAUDE.md`:

```markdown
## Tool Catalogue (context-manager-cc)

Some tools are not loaded to reduce context. If you need one, ask the user first.

### Always available
Read, Write, Glob, Grep, Edit, AskUserQuestion, ExitPlanMode, Task*

### Requires approval (currently not in context)
WebFetch, WebSearch  ← replaced with actual deny list at install time

**If you need an unavailable tool:**
1. Tell the user which tool you need and why
2. Ask: "May I use [ToolName]?"
3. If yes: use Write to add the tool name to `approved_tools` in
   `.claude/context-manager-cc/memory.json`
4. Inform the user: "Approval saved. Run `python install.py --sync` or start
   a new conversation to activate [ToolName]."
```

The install step replaces the placeholder list with the actual tools in deny.

---

## Core Modules

### `core/tool_loader.py`
```python
def get_tier(tool_name, tools_path) -> str:          # "simple" or "advanced"
def get_advanced_tools(tools_path) -> list[str]:     # all advanced tool names
def get_denied_tools(tools_path, memory_path) -> list[str]:  # advanced minus approved
```
Mirrors the API version's `tool_loader.py` logic but outputs a deny list instead of a tools array.

### `core/settings_manager.py`
```python
def read_settings(dot_claude_path) -> dict:          # parse .claude/settings.json
def write_settings(dot_claude_path, data: dict):     # write back
def apply_deny_list(dot_claude_path, tools: list[str]):  # merge tools into permissions.deny
def apply_allow_list(dot_claude_path, tools: list[str]): # merge into permissions.allow
def sync(dot_claude_path, tools_path, memory_path):
    # 1. load approved from memory.json
    # 2. compute deny = advanced - approved
    # 3. write deny list to settings.json
    # 4. write approved to allow list in settings.json
```

### `core/installer.py`
1. Resolve target path
2. Create `.claude/context-manager-cc/` directory
3. Copy `config/tools.json` → `.claude/context-manager-cc/tools.json`
4. Create `.claude/context-manager-cc/memory.json` if absent
5. Call `settings_manager.sync()` to write initial deny list
6. Append `config/CLAUDE.md` block to `CLAUDE.md` (idempotent — guard comment)

---

## Entry Point: `install.py`

```
python install.py [--target /path/to/project] [--global]
python install.py --sync [--target /path/to/project]
```

- **default / `--target`**: First-time setup for a project
- **`--sync`**: Re-read memory.json, regenerate settings.json deny/allow lists (run after Claude writes an approval mid-session)
- **`--global`**: Install to `~/.claude/` for all projects

---

## Implementation Order

| Step | File | Description |
|------|------|-------------|
| 1 | `config/tools.json` | Tool tier registry with Claude Code tool names |
| 2 | `config/CLAUDE.md` | CLAUDE.md snippet template |
| 3 | `config/memory.json` | Initial state: `{"approved_tools": []}` |
| 4 | `core/tool_loader.py` | `get_denied_tools()`, `get_advanced_tools()` |
| 5 | `core/settings_manager.py` | Read/write `.claude/settings.json`, `sync()` |
| 6 | `core/installer.py` | Directory setup + initial sync |
| 7 | `install.py` | Argparse entry point (setup + --sync) |
| 8 | `tests/test_settings_manager.py` | Unit tests: sync logic, deny/allow merging |
| 9 | `README.md` | Quickstart, workflow, comparison with API version |

---

## Verification

1. `python install.py --target /some/project` → verify `.claude/settings.json` has WebFetch/WebSearch in deny, CLAUDE.md has catalogue appended
2. Manually edit `memory.json` to add `WebFetch` → run `python install.py --sync` → verify WebFetch moves from deny to allow in settings.json
3. Run `pytest tests/test_settings_manager.py`
4. Live test in Claude Code: install into a project, open it, ask Claude to fetch a URL → Claude should recognise WebFetch is unavailable, ask permission, write to memory.json → run --sync → next session Claude can use it

---

## Comparison with API Version

| Aspect | context-manager-api | context-manager-cc |
|--------|--------------------|--------------------|
| Mechanism | Controls `tools` array per request | `permissions.deny` removes schemas from context |
| Token savings | ~70% per turn (measured) | Proportional to # of denied tools |
| Primary value | Cost reduction at scale | Context reduction + safety gate |
| Entry point | `python claude_chat.py` (interactive chat) | `python install.py` (one-time setup + sync) |
| Approval UX | Interactive CLI prompt (y/n/always) | Claude asks → user says yes → Claude writes memory.json |
| Persistence | `config/memory.json` | `.claude/context-manager-cc/memory.json` |
| Approval activates | Same turn (tool added to array) | Next session (settings.json regenerated via --sync) |
| Hooks required | No | No |
| New tools | Can add any custom tool | Limited to CC's built-in + MCP tools |
