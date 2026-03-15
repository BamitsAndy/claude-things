# Changelog

All notable changes to this project will be documented here.
Format: `[version] YYYY-MM-DD — description`

---

## Unreleased

- Initial project structure planned (see PLAN.md)

---

## [0.1.0] 2026-03-06 — Phases 1–6 implemented

### Added
- `context-manager-api/config/tools.json` — tiered tool registry (4 simple + 8 advanced) with full Claude API `input_schema` blocks
- `context-manager-api/config/claude.md` — compact system prompt with ask-permission protocol
- `context-manager-api/config/memory.json` — persistent approval store (initial state)
- `context-manager-api/core/tool_loader.py` — lazy loader: baseline always present, advanced added on approval
- `context-manager-api/core/permission_hook.py` — y / n / always permission gate
- `context-manager-api/core/executor.py` — full tool dispatcher (Read, Write, Glob, AskUserQuestion, Bash, Edit, Grep, Task*)
- `context-manager-api/core/chat_loop.py` — main API loop with tool intercept and session approval tracking
- `context-manager-api/claude_chat.py` — CLI entry point with `--no-persist` flag
- `context-manager-api/tests/test_token_savings.py` — token measurement script (Phase 7, ready to run)

---

<!-- Add entries above this line as work progresses -->
