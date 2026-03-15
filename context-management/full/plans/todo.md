# Todo

## Backlog
_Nothing remaining — all phases complete._

## In Progress
_Nothing in progress._

## Done

### Phase 1 — Tool Registry
- [x] Created `context-manager-api/config/tools.json` with all 12 tools, `tier` field, and real Claude API `input_schema` blocks

### Phase 2 — System Prompt
- [x] Created `context-manager-api/config/claude.md` — compact catalogue (names only) + ask-permission protocol
- [x] Created `context-manager-api/config/memory.json` — initial state `{"approved_tools": []}`

### Phase 3 — Tool Loader
- [x] Implemented `context-manager-api/core/tool_loader.py` — `load_tools()`, `save_approved()`, `_load_persistent_approved()`

### Phase 4 — Permission Hook
- [x] Implemented `context-manager-api/core/permission_hook.py` — `ask_permission()` with y / n / always levels

### Phase 5 — Tool Executor
- [x] Implemented `context-manager-api/core/executor.py` — full dispatcher for all 12 tools incl. file-backed TaskManager

### Phase 6 — Chat Loop & Entry Point
- [x] Implemented `context-manager-api/core/chat_loop.py` — main Anthropic API loop with tool intercept logic
- [x] Implemented `context-manager-api/claude_chat.py` — CLI entry point with `--no-persist` flag

### Phase 7 — Validation
- [x] Ran `python -m tests.test_token_savings` — **70% reduction** (875 tokens/turn saved). Results in `devStatus.md`.
