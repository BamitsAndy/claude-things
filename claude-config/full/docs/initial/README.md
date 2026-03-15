# Claude Project Base Pattern

A reusable project template that enforces a disciplined **plan → clear context → implement step → repeat** cycle with Claude Code.

## Purpose

Claude's context window fills up fast. Without structure, a single session can sprawl from requirements gathering to half-implemented code to debugging — all mixed together. When context gets long, Claude loses track of earlier decisions, hallucinates file contents, and drifts from the original plan.

This pattern solves that by enforcing two distinct modes with a hard boundary between them:

- **Planning mode** — Claude asks questions, documents decisions, and produces a numbered plan. No code is written.
- **Implementation mode** — each session starts fresh with `/step`, loads only the context needed for one step, implements it, and stops.

The result is shorter, more focused sessions where Claude always knows what it's doing and why.

---

## Structure

```
project-root/
├── CLAUDE.md                        # Minimal stub loaded automatically by Claude Code
├── .claude/
│   ├── ENV.md                       # Python env & package preferences (incl. Testing section)
│   └── commands/
│       ├── start.md                 # /start skill (planning phase)
│       ├── step.md                  # /step skill (implementation phase)
│       └── replan.md                # /replan skill (blocker resolution)
└── docs/
    ├── initial/
    │   └── PlanningPrompts.md       # User requests (newest last); read by /start
    └── tests/
        └── step_N/                  # Test artifacts per step (created by /step)
            ├── pytest_output.txt    # Full test runner output
            └── failures.txt        # Failure details only (present on failure)
```

**Note:** `docs/plan/` and `docs/initial/PLAN_verbose.md` are created by `/start` when you run it — they don't exist in the template. The artifact schemas are embedded in `start.md`.

---

## Usage

### Setting up a new project

1. Copy this directory structure into your project root.
2. Fill in `.claude/ENV.md` with your Python version, tooling, and standard packages.
3. Optionally add your request to `docs/initial/PlanningPrompts.md` (or pass it inline with `/start your request`).
4. Open Claude Code in the project directory.

### Planning phase

Run `/start` or `/start your request here` to begin planning.

- **With inline argument**: uses that text directly as the request
- **Without argument**: reads the latest entry from `docs/initial/PlanningPrompts.md`

Claude will:

1. Ask clarifying questions
2. Read `.claude/ENV.md` and assess a testing tier for the project (see [Testing](#testing))
3. Present the suggested tier with reasoning and wait for your confirmation
4. Produce all planning artifacts before writing any code:
   - `docs/initial/PLAN_verbose.md` — the full Q&A, decision record, and testing assessment
   - `docs/plan/PLAN.md` — the concise numbered plan (includes `## Testing Strategy` and per-step `**Testing**:` fields)
   - `docs/plan/PROGRESS.md` — the step tracker
   - `docs/initial/PlanningPrompts.md` — updated if needed

Review the plan. Revise if needed. Only proceed when satisfied.

### Implementation phase

Run `/step` to begin each implementation session. Claude runs a two-phase sub-step model:

**Phase A — Implementation**

1. Read `docs/plan/PLAN.md` and `docs/plan/PROGRESS.md`
2. Identify the next unchecked step
3. Load only the context files listed for that step
4. Implement that step and nothing more

**Phase B — Testing**

5. Check the step's `**Testing**:` field in `PLAN.md`
6. If `None — [reason]`, skip testing and close the step
7. Otherwise, launch a test sub-agent that:
   - Writes behavior-verifying tests (AAA pattern) for the specific scenarios named in the Testing field
   - Runs the tests and writes full output to `docs/tests/step_N/pytest_output.txt`
   - Writes failure details (if any) to `docs/tests/step_N/failures.txt`
   - Reports PASS or FAIL with counts
8. On FAIL, the main agent may fix **implementation files only** and retry — maximum 2 retries
9. Record the result in `PROGRESS.md` before closing the step (see [Test result tracking](#test-result-tracking))

`/step` runs with `context: fork` — it automatically executes in an isolated subagent with a fresh context window. No need to manually `/clear` before each step.

### Replanning phase

If `/step` encounters a blocker — missing information, invalid assumptions, or a step that no longer makes sense — it records a `> BLOCKER:` note inline under that step in `PROGRESS.md` and stops.

Run `/replan` (or `/replan additional context here`) to re-enter planning mode with full context. Claude will:

1. Read the blocker from `PROGRESS.md`
2. If the blocker is test-related (`TESTS: FAIL`), automatically load `docs/tests/step_N/failures.txt` for context
3. Ask clarifying questions if needed
4. Revise `PLAN.md` and `PROGRESS.md` — removing the blocker note once resolved
5. Append a "Replan" record to `docs/initial/PLAN_verbose.md`
6. If the revised scope significantly changes, reassess the testing tier and note any change

Then run `/step` again to continue from the revised step.

---

## Testing

### Tiers

Testing strategy is assessed during `/start` and recorded in `docs/plan/PLAN.md` under `## Testing Strategy`.

| Tier | When to use | Approach |
|---|---|---|
| **Simple** | Straightforward scripts or single-purpose tools — minimal branching, no external dependencies | Inline assertions and a smoke test script. No pytest setup required. |
| **Moderate** | Multi-module projects with some logic complexity, limited external dependencies, or a small public API | pytest with behavior-verified unit tests covering core logic. No fixtures or mocks unless clearly needed. |
| **Custom** | Significant external integrations, async/concurrent logic, complex state machines, or a non-trivial public API | Bespoke named approach (e.g. "Integration-first", "Contract-tested"). Layers and rationale defined explicitly. |

The tier is suggested with reasoning and confirmed with you before any artifacts are written.

### Sub-agent test model

Each `/step` with a non-`None` Testing field launches a dedicated test sub-agent. The sub-agent:

- Receives the step's Testing field (specific scenarios) and Acceptance criteria
- Writes tests using the **Arrange / Act / Assert** pattern with named assertions for each scenario
- Runs the tests independently
- Writes all output to `docs/tests/step_N/pytest_output.txt`
- Writes failure details to `docs/tests/step_N/failures.txt` (only present on failure)

The main agent may fix **implementation files only** on failure, with a maximum of 2 retries. It must never modify test files, relax assertions, or add special-case logic.

### Test result tracking

Results are recorded inline in `docs/plan/PROGRESS.md` before the step is closed:

```
- [x] 3 - My step | context: docs/plan/PLAN.md
  > TESTS: PASS (4/4) | docs/tests/step_3/
```

On failure:

```
- [ ] 3 - My step | context: docs/plan/PLAN.md
  > TESTS: FAIL (2/4) | docs/tests/step_3/
  > BLOCKER: tests failed — run /replan to resolve
```

The `failures.txt` artifact is loaded automatically by `/replan` when a test-related blocker is present.

---

## Files Reference

| File | Purpose |
|---|---|
| `CLAUDE.md` | Loaded automatically; points to `/start`, `/step`, `/replan` |
| `.claude/ENV.md` | Python env & testing preferences (fill in manually; read by `/start`) |
| `.claude/commands/start.md` | `/start` skill — planning phase + testing tier assessment + artifact schemas |
| `.claude/commands/step.md` | `/step` skill — two-phase implementation + test sub-agent |
| `.claude/commands/replan.md` | `/replan` skill — blocker resolution + test artifact loading |
| `docs/initial/PlanningPrompts.md` | User requests (newest last); read by `/start` when no inline arg given |
| `docs/initial/PLAN_verbose.md` | Full planning record — generated by `/start`, updated by `/replan` |
| `docs/plan/PLAN.md` | The implementation plan — includes Testing Strategy and per-step Testing fields |
| `docs/plan/PROGRESS.md` | Step tracker — records `> TESTS:` results inline per step |
| `docs/tests/step_N/pytest_output.txt` | Full test runner output for step N — written by test sub-agent |
| `docs/tests/step_N/failures.txt` | Failure details for step N — present only when tests fail; loaded by `/replan` |
