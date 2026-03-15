# Implementation Plan

## Context

The claude-config workflow pattern (plan→step→replan) has no testing integration. This plan adds testing as a first-class concern: the planning phase assesses and records a testing strategy, each implementation step runs a dedicated test sub-agent that writes and runs behavior-verifying tests, failures are persisted as artifacts for context across sessions, and the full system is documented.

## Testing Strategy

**Tier**: Simple / None
**Approach**: Manual read-through of each updated file after editing. Confirm instructions are coherent, schemas are consistent across files, and sub-agent flow logic is unambiguous.
**Rationale**: All deliverables are markdown instruction files. No automated testing is applicable to this plan.

---

## Steps

### Step 1: Update ENV.md — add Testing section

- **Goal**: Add a Testing section to ENV.md so the `/start` planning agent can read it to inform tier assessment, and the `/step` agent can read it for tool and convention preferences.
- **Files**: `.claude/ENV.md`
- **Acceptance**: ENV.md contains a Testing section with template fields for: runner, config file, test directory, file naming convention, coverage tool and threshold, fixture approach, and preferred patterns. Fields are pre-filled with sensible defaults (pytest, pyproject.toml, tests/, test_*.py) and marked as overridable per project.
- **Testing**: None — this step defines the testing configuration source itself.
- **Context files**: `.claude/ENV.md`

---

### Step 2: Update start.md — testing tier assessment and updated artifact schemas

- **Goal**: Incorporate the testing tier assessment into the `/start` planning flow, and update all three artifact schemas to include testing fields.
- **Files**: `.claude/commands/start.md`
- **Acceptance**:
  - `start.md` instructs the agent to read `ENV.md` before the tier assessment
  - Tier suggestion flow is explicit: assess complexity → suggest tier with reasoning → user confirms or adjusts
  - Three tiers defined: Simple (smoke/assertions, no pytest setup), Moderate (pytest, behavior-verified unit tests), Custom (named bespoke approach)
  - `PLAN.md` schema includes `## Testing Strategy` section (Tier, Approach, Rationale) and per-step `**Testing**:` field (must name specific scenarios, not just "write tests")
  - `PLAN_verbose.md` schema includes `## Testing Assessment` section (Tier, Rationale, Approach)
  - `PROGRESS.md` schema includes `> TESTS: PASS (X/X) | docs/tests/step_N/` line format
  - Content is a superset of `new feature/start.md` with all brainstorm refinements applied
- **Testing**: None — markdown file, manual review.
- **Context files**: `new feature/start.md`, `.claude/commands/start.md`, `.claude/ENV.md`

---

### Step 3: Update step.md — sub-step model with test sub-agent

- **Goal**: Add the two-phase sub-step model: (A) implement the step, (B) launch a test sub-agent that writes and runs behavior-verifying tests, with a 2-retry fix loop (implementation only, with explicit guardrails), artifact writing, and PROGRESS.md update.
- **Files**: `.claude/commands/step.md`
- **Acceptance**:
  - `step.md` instructs: implement → launch test sub-agent → interpret result
  - Test sub-agent receives: step's Testing field, Acceptance criteria, implementation files written, artifact path `docs/tests/step_N/`
  - Test sub-agent writes tests using AAA pattern with specific assertions and edge cases named in the Acceptance field; runs them; reports PASS/FAIL with failure details
  - Fix loop: max 2 retries; main agent fixes implementation files only
  - Guardrail language explicitly states: do not modify test files, do not relax assertions, do not add special-case logic for specific inputs; if fix would change the step's Goal or Acceptance, declare BLOCKER immediately
  - Artifacts written to `docs/tests/step_N/`: `pytest_output.txt` and `failures.txt` (failures only, for /replan context)
  - PROGRESS.md updated with `> TESTS: PASS (X/X) | docs/tests/step_N/` or FAIL equivalent before closing the step
- **Testing**: None — markdown file, manual review.
- **Context files**: `.claude/commands/step.md`, `.claude/commands/start.md`

---

### Step 4: Update replan.md — test artifact context loading

- **Goal**: Instruct `/replan` to load test failure artifacts when the current blocker is test-related, and to reassess the testing tier if the replanned scope has changed significantly.
- **Files**: `.claude/commands/replan.md`
- **Acceptance**:
  - `replan.md` instructs: if PROGRESS.md shows `TESTS: FAIL` on the blocked step, load `docs/tests/step_N/failures.txt` alongside the standard context files
  - `replan.md` instructs: if the revised plan significantly changes scope, reassess whether the current testing tier still fits and note any change in the updated `PLAN_verbose.md`
- **Testing**: None — markdown file, manual review.
- **Context files**: `.claude/commands/replan.md`, `.claude/commands/start.md`

---

### Step 5: Update README.md — document testing system

- **Goal**: Update the README to document the testing tier system, sub-agent test model, test artifacts folder, and the TESTS line in PROGRESS.md.
- **Files**: `docs/initial/README.md`
- **Acceptance**: README describes: the three testing tiers and when each applies, the two-phase sub-step model in `/step`, the `docs/tests/` artifact folder structure, and the `> TESTS:` line in PROGRESS.md.
- **Testing**: None — markdown file, manual review.
- **Context files**: `docs/initial/README.md`

---

### Step 6: Create CHANGELOG.md and clean up new feature/

- **Goal**: Create a `CHANGELOG.md` at the project root for version and feature tracking. Record this testing integration as the first entry. Delete the `new feature/` directory.
- **Files**: `CHANGELOG.md` (create), `new feature/` (delete all contents and directory)
- **Acceptance**: `CHANGELOG.md` exists at project root with a versioned entry describing all testing integration additions. `new feature/` directory no longer exists.
- **Testing**: None.
- **Context files**: None
