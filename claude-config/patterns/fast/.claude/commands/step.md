---
description: Implementation phase. Run to execute the next planned step. Reads the plan and implements exactly one step.
triggers: /step, "next step", "implement next", "continue", "do the next step"
---

Read `docs/plan/PLAN.md` and `docs/plan/PROGRESS.md`.

Identify the next unchecked step (marked `[ ]`) in PROGRESS.md.

Check if that step has an inline `> BLOCKER:` note beneath it.
If a blocker is present, do NOT proceed — inform the user of the blocker and instruct them to run `/replan` to revise the plan before continuing.

If the step has other listed notes that have not been addressed, raise this before proceeding.

Load any context files listed for that step.

Implement only that step — nothing more. Do not deviate from the plan to progress the implementation.

If insufficient information is available to complete the step, or the requested development step does not make sense — highlight this clearly as a blocker and record it as a `> BLOCKER:` note under the step in PROGRESS.md.

When done:
- Mark the step `[x]` in `docs/plan/PROGRESS.md` if it was completed
- Update the "Current Step" number
- Add any blockers or findings as inline `> BLOCKER:` notes under the relevant step
