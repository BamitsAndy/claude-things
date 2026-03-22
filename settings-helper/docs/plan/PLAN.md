# Implementation Plan

## Context

When starting a new Claude Code project, users need to configure `settings.json` permissions to control which tools Claude can use. There's no built-in way to discover available tools upfront. This feature adds a `/tool-audit` slash command that instructs Claude to enumerate all tools from its context and write a structured audit file + draft settings to the project.

## Testing Strategy

**Tier**: Simple
**Approach**: Two pytest tests in `tests/test_process_audit.py` covering the Python script's table parser and JSON emitter. No fixtures. No mocks. Run with `pytest tests/test_process_audit.py -v`.
**Rationale**: Only the Python script has executable logic. The command file and README are static content — correctness is verified by reading them.

## Steps

### Step 0: Create planning artifacts
- **Goal**: Write docs/ planning artifacts per /start workflow
- **Files**: `docs/initial/PLAN_verbose.md`, `docs/plan/PLAN.md`, `docs/plan/PROGRESS.md`, `docs/initial/PlanningPrompts.md`
- **Acceptance**: All four files exist with correct content
- **Testing**: None — static content
- **Context files**: Plan file

### Step 1: Create the `/tool-audit` command file
- **Goal**: Core artifact — slash command that enumerates all tools, writes `.claude/TOOL_AUDIT.md` table, writes `.claude/settings.json.draft`
- **Files**: `.claude/commands/tool-audit.md`
- **Acceptance**: File exists, frontmatter matches pattern of `start.md`/`step.md`, command content covers all 5 spec requirements
- **Testing**: None — static prompt content
- **Context files**: `.claude/commands/start.md` (frontmatter pattern), `.claude/settings.json` (existing denials to preserve)

### Step 2: Create Python post-processor
- **Goal**: Offline script to parse `TOOL_AUDIT.md` and emit filtered `settings.json` fragments
- **Files**: `scripts/process_audit.py`, `tests/test_process_audit.py`
- **Acceptance**: `--summary` prints category counts; `--emit-json | python -m json.tool` succeeds; pytest passes
- **Testing**: Parse sample table → verify row count and field extraction; `emit_json()` → verify valid JSON with `permissions.deny` and `permissions.allow` keys
- **Context files**: Plan file (table format spec)

### Step 3: Create usage README
- **Goal**: User-facing documentation for the full workflow
- **Files**: `docs/tool-audit/README.md`
- **Acceptance**: Covers why, how to run, what gets created, how to review, how to apply, how to disable, how to use the Python script
- **Testing**: None — documentation
- **Context files**: Plan file
