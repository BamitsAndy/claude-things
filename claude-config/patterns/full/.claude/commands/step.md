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

---

## Phase A — Implementation

Implement the step as described in PLAN.md. Write or modify only the files listed under **Files** for that step.

---

## Phase B — Testing

After implementation is complete, check the step's **Testing** field in PLAN.md.

If the Testing field is `None — [reason]`, skip Phase B and proceed directly to closing the step.

Otherwise, launch a test sub-agent with the following inputs:
- The step's **Testing** field (specific scenarios and edge cases to cover)
- The step's **Acceptance** criteria
- The list of implementation files written in Phase A
- Artifact output path: `docs/tests/step_N/` (where N is the step number)

### Test sub-agent instructions

The test sub-agent must:

1. Write tests using the AAA pattern (Arrange / Act / Assert) with specific assertions for each scenario named in the Testing field and Acceptance criteria.
2. Run the tests.
3. Write all output to `docs/tests/step_N/pytest_output.txt`.
4. If any tests fail, write only the failure details to `docs/tests/step_N/failures.txt`.
5. Report back: PASS (X/X) or FAIL (X/X) with a summary of any failures.

### Fix loop

If the test sub-agent reports FAIL:

- The main agent may fix **implementation files only** (the files listed under **Files** for this step).
- Re-launch the test sub-agent. Maximum **2 retries**.

**Guardrails — the main agent must never:**
- Modify test files
- Relax or weaken assertions
- Add special-case logic that makes a specific test input pass without fixing the underlying behaviour

If the fix required to make tests pass would change the step's **Goal** or **Acceptance** criteria, do NOT attempt the fix — declare a BLOCKER immediately and record it as a `> BLOCKER:` note under the step in PROGRESS.md.

---

## Closing the step

Before marking the step complete, update PROGRESS.md:

- If testing was skipped (None): mark the step `[x]` and update Current Step.
- If tests passed: add `> TESTS: PASS (X/X) | docs/tests/step_N/` under the step, then mark `[x]` and update Current Step.
- If tests failed after all retries: add `> TESTS: FAIL (X/X) | docs/tests/step_N/` under the step. Do NOT mark `[x]`. Record a `> BLOCKER: tests failed — run /replan to resolve` note under the step.
