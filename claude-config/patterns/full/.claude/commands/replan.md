---
description: Blocker resolution. Run when a step has a BLOCKER note in PROGRESS.md. Revises the plan and clears the blocker.
triggers: /replan, "resolve blocker", "unblock", "replan", "there's a blocker"
---

Use the builtin plan agent.

Read `docs/plan/PROGRESS.md`, `docs/plan/PLAN.md`, and `docs/initial/PLAN_verbose.md`.

Identify the blocker — look for a `> BLOCKER:` note under the current step in PROGRESS.md.
If $ARGUMENTS were provided, treat them as additional context about the blocker.

If PROGRESS.md shows a `> TESTS: FAIL` line on the blocked step, load `docs/tests/step_N/failures.txt` (where N is the blocked step number) alongside the standard context files before proceeding.

Ask clarifying questions if the blocker requires information you don't have.

Once you understand the blocker, revise the plan:
- Modify the blocked step, split it, add prerequisite steps, or remove it as appropriate
- Ensure all downstream steps remain valid

Once you understand the blocker and have gathered all relevant context, assess whether the revised plan significantly changes scope compared to the original. If it does, reassess whether the current testing tier (recorded in `docs/plan/PLAN.md` under **Testing Strategy**) still fits the revised scope. Note any tier change in the updated `docs/initial/PLAN_verbose.md` under the Replan section.

Produce updated artifacts:
1. `docs/plan/PLAN.md` — revised plan with updated or new steps; update **Testing Strategy** if the tier has changed
2. `docs/plan/PROGRESS.md` — updated step list; remove the `> BLOCKER:` note from the resolved step
3. `docs/initial/PLAN_verbose.md` — append a "Replan" section noting the blocker and decisions made; update the steps here but clearly identify changes as a result of the replan phase; note any testing tier reassessment
