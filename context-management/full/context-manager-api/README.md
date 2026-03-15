# Context Manager — Lazy-Loading Tool Chat CLI

A Claude API chat CLI that reduces per-turn token usage by **70%** through lazy tool loading and explicit user permission gating.

Instead of sending every tool schema on every request (~1,257 tokens), only the four baseline tools are loaded upfront (~382 tokens). Advanced tools are added to the `tools` array only after the user approves them.

## How It Works

Tools are split into two tiers in `config/tools.json`:

| Tier | Tools | Loaded |
|------|-------|--------|
| `simple` | Read, Write, Glob, AskUserQuestion | Every request |
| `advanced` | Bash, Edit, Grep, TaskCreate, TaskGet, TaskList, TaskUpdate, TaskStop | Only after user approval |

When Claude wants to use an advanced tool, it asks permission first. The user can respond:
- `y` — allow this call only (session-scoped)
- `n` — deny; Claude tries an alternative approach
- `always` — approve permanently (saved to `config/memory.json`)

## Token Savings

| Metric | Value |
|--------|-------|
| Baseline (4 simple tools) | 382 tokens/turn |
| Full set (12 tools) | 1,257 tokens/turn |
| Saved per turn | **875 tokens** |
| Reduction | **70%** |

## Project Structure

```
context-manager-api/
├── claude_chat.py           # CLI entry point
├── config/
│   ├── claude.md            # System prompt — compact tool catalogue
│   ├── memory.json          # Persistent approved-tool state
│   └── tools.json           # Tiered tool registry (all schemas)
├── core/
│   ├── chat_loop.py         # Main Anthropic API conversation loop
│   ├── executor.py          # Tool dispatcher + file-backed TaskManager
│   ├── permission_hook.py   # y / n / always permission gate
│   └── tool_loader.py       # Builds tools[] per request
└── tests/
    └── test_token_savings.py  # Measures baseline vs full token cost
```

## Requirements

- Python 3.11+
- An Anthropic API key with credits

## Setup

1. **Clone / copy the project**

   ```bash
   cd context-manager-api
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

3. **Activate it**

   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - Windows (bash/Git Bash): `source .venv/Scripts/activate`
   - macOS / Linux: `source .venv/bin/activate`

4. **Install dependencies**

   ```bash
   pip install anthropic
   ```

   Optional — for precise token counting (instead of the char-heuristic fallback):

   ```bash
   pip install tiktoken
   ```

5. **Set your API key**

   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."   # bash / macOS / Linux
   set ANTHROPIC_API_KEY=sk-ant-...        # Windows cmd
   $env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
   ```

6. **Reset approved tools** (optional, first run)

   `config/memory.json` ships with an empty approved list. To reset it at any time:

   ```bash
   echo '{"approved_tools": []}' > config/memory.json
   ```

## Running the Chat CLI

Run from inside `context-manager-api/`:

```bash
python claude_chat.py
```

### Flags

| Flag | Effect |
|------|--------|
| _(none)_ | Approvals persist to `config/memory.json` across sessions |
| `--no-persist` | Approvals are session-only; `memory.json` is never written |

```bash
# Session-only mode — nothing is saved to memory.json
python claude_chat.py --no-persist
```

### Example session

```
Context Manager Chat — type 'quit' to exit

> list all .py files in the src directory

⚡ Claude wants to use [Glob]
   pattern: **/*.py
Allow? (y/n/always): always

Claude: Found 5 Python files: ...

> quit
```

Type `quit` or `exit` to end the session.

## Running the Token Savings Test

From inside `context-manager-api/`:

```bash
python -m tests.test_token_savings
```

Expected output:

```
Baseline tools  :   382 tokens  (4 tools)
Full tools      : 1,257 tokens  (12 tools)
Saved           :   875 tokens  (70% reduction)
```

> Note: without API credits the test falls back to a character-heuristic counter (~4 chars/token). Results are still representative.

## Configuration

### Changing the model

Edit the `model` value in `core/chat_loop.py`:

```python
response = client.messages.create(
    model="claude-haiku-4-5-20251001",   # change here
    ...
)
```

### Adding or reclassifying tools

Edit `config/tools.json`. Each entry requires:

```json
{
  "name": "ToolName",
  "tier": "simple",          // or "advanced"
  "description": "...",
  "input_schema": { ... }    // standard Claude API tool schema
}
```

The `tier` key is stripped before the schema is sent to the API.

### Editing the system prompt

Edit `config/claude.md`. The compact catalogue lists tool names only — full schemas are in `tools.json` and only sent in the `tools` array when a tool is active. This keeps the system prompt lightweight.

## Out of Scope

- Web UI / server deployment
- Multi-user sessions
- `defer_loading: true` API beta (conflicts with prompt caching; revisit when stable)
- Tool-use audit logging
