# Changelog — claude-config

Covers both variants: `fast` (no testing integration) and `full` (with testing integration).

---

## [1.2.0] — 2026-03-20

### Consolidation — doc restructure and repo organisation

Moved shared artefacts to the parent `claude-config/` level so they are version-agnostic and serve both variants.

- Added `README.md` at repo root describing both variants and linking to their sub-READMEs
- Moved `CHANGELOG.md` from `full/` to repo root; now covers both variants
- Moved `docs/plan/PLAN.md` and `docs/plan/PROGRESS.md` from `full/docs/plan/` to `claude-config/docs/plan/`
- Moved `docs/initial/PLAN_verbose.md` from `full/docs/initial/` to `claude-config/docs/initial/`
- `full/docs/plan/` is now an empty template directory, consistent with `fast/docs/plan/`
- Added `consolidation_plan.md` at repo root documenting the consolidation decisions

---

## [1.1.0] — 2026-03-14

### Testing Integration

Added testing as a first-class concern across the plan → step → replan workflow.

> Note: `[1.1.0]` corresponds to the `full` variant baseline (testing integration).

**`.claude/ENV.md`**
- Added `## Testing` section with template fields: runner, config file, test directory, file naming convention, coverage tool and threshold, fixture approach, and preferred patterns. Pre-filled with pytest defaults; overridable per project.

**`.claude/commands/start.md`**
- Added testing tier assessment phase: reads `ENV.md`, assesses project complexity, proposes a tier (Simple / Moderate / Custom) with explicit reasoning, and waits for user confirmation before writing artifacts.
- Updated `PLAN.md` schema to include `## Testing Strategy` (Tier, Approach, Rationale) and per-step `**Testing**:` field.
- Updated `PLAN_verbose.md` schema to include `## Testing Assessment` section.
- Updated `PROGRESS.md` schema to include `> TESTS: PASS/FAIL (X/X) | docs/tests/step_N/` inline format.

**`.claude/commands/step.md`**
- Replaced single-phase implementation with a two-phase sub-step model:
  - **Phase A**: implement the step as before.
  - **Phase B**: launch a dedicated test sub-agent that writes behavior-verifying tests (AAA pattern), runs them, writes artifacts to `docs/tests/step_N/`, and reports PASS/FAIL.
- Fix loop: main agent may fix implementation files only, maximum 2 retries.
- Guardrails: test files must not be modified; assertions must not be relaxed; special-case logic is prohibited. If a fix would change the step's Goal or Acceptance, declare a BLOCKER immediately.
- `PROGRESS.md` updated with test result before closing the step.

**`.claude/commands/replan.md`**
- Added: if PROGRESS.md shows `TESTS: FAIL` on the blocked step, load `docs/tests/step_N/failures.txt` alongside standard context.
- Added: if the revised plan significantly changes scope, reassess the testing tier and note any change in `PLAN_verbose.md` and `PLAN.md`.

**`docs/initial/README.md`**
- Added `## Testing` section documenting: three testing tiers with descriptions, the sub-agent test model, the `docs/tests/` artifact folder structure, and the `> TESTS:` tracking line in `PROGRESS.md`.
- Updated folder structure diagram to include `docs/tests/step_N/`.
- Updated Files Reference table with new and revised entries.

---

## [1.0.0] — initial

Initial release of the Claude project base pattern: plan → step → replan workflow with `ENV.md`, `start.md`, `step.md`, `replan.md`, and `README.md`.

> Note: `[1.0.0]` corresponds to the `fast` variant baseline (no testing integration).
