# Verbose Planning Record

## Questions Asked

1. When you say "system tools portion", what specifically do you want to capture?
2. What is the primary goal for creating the settings.json permissions?
3. How should the tool info be surfaced to the user?

## User Responses

1. **Tool definitions (schemas)** — the full JSON schema definitions of all tools available in the session
2. **Understand & decide** — first understand what tools are available, then decide the allow/deny strategy
3. **Markdown table** at session startup; activity is run once, Claude Code is reloaded after settings.json is configured

## Decisions & Rationale

- **Command over hook**: Hooks don't have access to tool schemas (only to invoked tool names + inputs). Claude has complete tool schema knowledge in its context window. A `/tool-audit` slash command is the accurate, idiomatic approach.
- **Draft file, not auto-apply**: The audit is a discovery activity. The user reviews and decides — the command provides information, the user makes the configuration decision. Auto-applying to `settings.json` would bypass that review.
- **`_comment` keys in JSON**: `settings.json` is plain JSON (not JSONC). `_comment` string keys are a common workaround that survives JSON parsers while remaining human-readable.
- **Python script as alternate/companion**: An offline post-processor (`scripts/process_audit.py`) serves users who want to parse/filter the audit output programmatically without a live Claude session.
- **Disable by deletion**: The audit is removed by deleting the command file — clean, explicit, no flags or toggles required.

## Environment Choices

- Shell scripts: bash (Windows 11 with bash shell)
- Scripting: Python (per ENV.md preferences), stdlib-only (`re`, `json`, `argparse`, `pathlib`)
- No new dependencies required

## Testing Assessment

**Tier**: Simple
**Rationale**: The primary artifact (`.claude/commands/tool-audit.md`) is a static markdown prompt file — no executable logic to unit-test. The Python post-processor (`scripts/process_audit.py`) has two testable functions: markdown table parsing and JSON emission. No external dependencies, no I/O beyond file reads.
**Approach**: Two pytest tests in `tests/test_process_audit.py` — one verifies table row parsing extracts correct count/fields from a sample `TOOL_AUDIT.md`, one verifies `--emit-json` output is valid JSON with expected structure. Inline assertions via pytest (no fixtures needed).

## Final Approach Summary

A `/tool-audit` slash command file that instructs Claude to enumerate all tools in its context, write a structured markdown table to `.claude/TOOL_AUDIT.md`, and write a draft `settings.json.draft`. A companion Python script (`scripts/process_audit.py`) allows offline post-processing of the generated audit file. The workflow is one-time: run `/tool-audit`, review the outputs, configure `settings.json`, reload Claude Code, then delete the command file.
