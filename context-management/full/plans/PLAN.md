# Plan: Lazy-Loading Tool Context Manager

**Primary goal:** Reduce token usage from the `tools` array by keeping only a minimal baseline loaded, adding advanced tools on-demand after user approval.
**Secondary benefit:** Explicit user consent gate before powerful tools run.

---

## Architecture Overview

```
context-manager-api/
├── claude_chat.py           ← main CLI entry point
├── config/
│   ├── claude.md            ← system prompt (baseline + compact catalogue)
│   ├── memory.json          ← approved tool state (persistent or session)
│   └── tools.json           ← single tiered tool registry
├── core/
│   ├── tool_loader.py       ← loads tools array for each request
│   ├── permission_hook.py   ← intercepts tool_use, asks user, updates memory
│   └── chat_loop.py         ← main Claude API conversation loop
└── tests/
    └── test_token_savings.py ← measures context size before/after
```

---

## Phase 1 — Tool Registry (`tools.json`)

Single file, `tier` field separates baseline from advanced:

```json
[
  {"name": "Read",             "tier": "simple",   "description": "Read a UTF-8 text file", "input_schema": { ... }},
  {"name": "Write",            "tier": "simple",   "description": "Write text to a file",   "input_schema": { ... }},
  {"name": "Glob",             "tier": "simple",   "description": "List files by glob",      "input_schema": { ... }},
  {"name": "AskUserQuestion",  "tier": "simple",   "description": "Prompt the user",         "input_schema": { ... }},
  {"name": "Bash",             "tier": "advanced", "description": "Execute shell commands",  "input_schema": { ... }},
  {"name": "Edit",             "tier": "advanced", "description": "Structured file edits",   "input_schema": { ... }},
  {"name": "Grep",             "tier": "advanced", "description": "Regex file search",        "input_schema": { ... }},
  {"name": "TaskCreate",       "tier": "advanced", "description": "Create background task",  "input_schema": { ... }},
  {"name": "TaskGet",          "tier": "advanced", "description": "Get task status",          "input_schema": { ... }},
  {"name": "TaskList",         "tier": "advanced", "description": "List tasks",               "input_schema": { ... }},
  {"name": "TaskUpdate",       "tier": "advanced", "description": "Update a task",            "input_schema": { ... }},
  {"name": "TaskStop",         "tier": "advanced", "description": "Stop a task",              "input_schema": { ... }}
]
```

**Why one file:** Easier to manage tiers, filter programmatically, and add new tools.

---

## Phase 2 — System Prompt (`claude.md`)

Keep the catalogue **compact** — names only, no parameter lists. Full schemas are in `tools.json` and only sent in the `tools` array when approved.

```markdown
You are a helpful assistant.

# Always-enabled tools
Read, Write, Glob, AskUserQuestion

# Available on approval (ask user before using)
Bash, Edit, Grep, TaskCreate, TaskGet, TaskList, TaskUpdate, TaskStop

**Rule:** For any approval-required tool, say:
  "I'd like to use [ToolName] — may I?"
Do not emit a tool_use block until the user says yes.
```

**Token saving:** ~3 tokens per tool name vs. ~30–80 tokens per full schema in claude.md.
The full schema cost is only paid when a tool enters the `tools` array.

---

## Phase 3 — Tool Loader (`core/tool_loader.py`)

```python
import json
from pathlib import Path

TOOLS_PATH = Path("config/tools.json")
MEMORY_PATH = Path("config/memory.json")

def _all_tools() -> list[dict]:
    return json.loads(TOOLS_PATH.read_text())

def load_tools(session_approved: set[str] | None = None) -> list[dict]:
    """Return the tools array to pass to Claude on each request."""
    all_tools = _all_tools()
    baseline = [t for t in all_tools if t["tier"] == "simple"]

    approved_names = _load_persistent_approved() | (session_approved or set())
    advanced_approved = [t for t in all_tools if t["tier"] == "advanced"
                         and t["name"] in approved_names]

    # Strip the 'tier' key — Claude API doesn't expect it
    result = baseline + advanced_approved
    for t in result:
        t.pop("tier", None)
    return result

def _load_persistent_approved() -> set[str]:
    try:
        data = json.loads(MEMORY_PATH.read_text())
        return set(data.get("approved_tools", []))
    except Exception:
        return set()

def save_approved(tool_name: str):
    try:
        data = json.loads(MEMORY_PATH.read_text())
    except Exception:
        data = {}
    data.setdefault("approved_tools", [])
    if tool_name not in data["approved_tools"]:
        data["approved_tools"].append(tool_name)
        MEMORY_PATH.write_text(json.dumps(data, indent=2))
```

---

## Phase 4 — Permission Hook (`core/permission_hook.py`)

```python
from core.tool_loader import save_approved

def ask_permission(tool_name: str, args: dict, persist: bool) -> bool:
    """Prompt user for approval. Returns True if approved."""
    print(f"\n⚡ Claude wants to use [{tool_name}]")
    if args:
        for k, v in list(args.items())[:3]:   # show first 3 args to keep it brief
            print(f"   {k}: {str(v)[:80]}")
    resp = input("Allow? (y/n/always): ").strip().lower()

    if resp == "always":
        save_approved(tool_name)   # persist permanently
        return True
    return resp.startswith("y")
```

**Three approval levels:**
- `y` — allow this one call (session, resets on restart)
- `always` — approve permanently (written to `memory.json`)
- `n` — deny

---

## Phase 5 — Chat Loop (`core/chat_loop.py`)

```python
import anthropic
from core.tool_loader import load_tools
from core.permission_hook import ask_permission
from pathlib import Path

client = anthropic.Anthropic()
SYSTEM_PROMPT = Path("config/claude.md").read_text()

def run(persist: bool = True):
    messages = []
    session_approved: set[str] = set()

    print("Context Manager Chat — type 'quit' to exit")
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            tools = load_tools(session_approved)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                tool_block = next(b for b in response.content if b.type == "tool_use")
                tool_name = tool_block.name
                args = tool_block.input

                # Check if in approved set already
                approved_names = load_tools(session_approved)  # re-derive
                if tool_name not in {t["name"] for t in approved_names}:
                    # Shouldn't happen if Claude follows protocol, but guard anyway
                    pass

                approved = ask_permission(tool_name, args, persist)
                if approved:
                    session_approved.add(tool_name)
                    # Execute tool (delegate to executor)
                    result = execute_tool(tool_name, args)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{"type": "tool_result",
                                     "tool_use_id": tool_block.id,
                                     "content": str(result)}]
                    })
                else:
                    # Denied — tell Claude
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{"type": "tool_result",
                                     "tool_use_id": tool_block.id,
                                     "content": "Permission denied by user."}]
                    })
            else:
                # Text response
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nClaude: {block.text}")
                messages.append({"role": "assistant", "content": response.content})
                break
```

---

## Phase 6 — Entry Point (`claude_chat.py`)

```python
import argparse
from core.chat_loop import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-persist", action="store_true",
                        help="Session-only approvals (don't write to memory.json)")
    args = parser.parse_args()
    run(persist=not args.no_persist)
```

---

## Phase 7 — Token Measurement (`tests/test_token_savings.py`)

Validate the approach actually saves tokens:

```python
import anthropic, json
from core.tool_loader import load_tools, _all_tools

client = anthropic.Anthropic()

def count_tool_tokens(tools: list[dict]) -> int:
    """Use the tokenize endpoint to measure tools array token cost."""
    resp = client.beta.messages.count_tokens(
        model="claude-haiku-4-5-20251001",
        tools=tools,
        messages=[{"role": "user", "content": "hello"}],
        system="test",
    )
    return resp.input_tokens

baseline = load_tools()
full = _all_tools()
for t in full:
    t.pop("tier", None)

baseline_tokens = count_tool_tokens(baseline)
full_tokens = count_tool_tokens(full)

print(f"Baseline tools  : {baseline_tokens:,} tokens  ({len(baseline)} tools)")
print(f"Full tools      : {full_tokens:,} tokens  ({len(full)} tools)")
print(f"Saved           : {full_tokens - baseline_tokens:,} tokens  "
      f"({100*(full_tokens-baseline_tokens)/full_tokens:.0f}% reduction)")
```

---

## Implementation Order

| Step | Task | Deliverable |
|------|------|-------------|
| 1 | Create `config/tools.json` with real Claude API `input_schema` blocks | Tool registry |
| 2 | Write `config/claude.md` compact catalogue | System prompt |
| 3 | Implement `core/tool_loader.py` | Tool loading + persistence |
| 4 | Implement `core/permission_hook.py` | y/n/always gate |
| 5 | Implement a minimal `execute_tool()` dispatcher | Actual tool execution |
| 6 | Wire up `core/chat_loop.py` + `claude_chat.py` | Working CLI |
| 7 | Run `tests/test_token_savings.py` | Validate token reduction |

---

## Key Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| Single `tools.json` with `tier` field | Avoids two-file sync drift |
| Compact catalogue in `claude.md` (names only) | ~3 tokens/tool vs. ~50/tool — pays for itself on first turn |
| `always` option in permission prompt | Avoids re-asking for tools user consistently approves |
| `--no-persist` flag | Security-conscious users can reset every session |
| `defer_loading: true` excluded | Currently conflicts with Claude Code prompt caching; revisit when stable |

---

## Out of Scope (for now)

- Web UI / server deployment
- `defer_loading: true` API beta — revisit when the caching regression is fixed
- Multi-user sessions
- Tool-use audit logging
