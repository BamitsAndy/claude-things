# Verbose Planning Record

## Questions Asked

1. Is `new feature/start.md` the authoritative basis for the updated `/start` command, or just a reference?
2. Should the test sub-agent write AND run tests, or only run tests the main agent has already written?
3. What should the retry limit be for the test fix loop?
4. What should happen to the `new feature/` directory after implementation?
5. What testing tier applies to this plan (all deliverables are markdown files)?

## User Responses

1. Use `new feature/start.md` as the basis; our brainstorm's refinements apply on top. It is the seed, not the final form.
2. Suggest the best approach.
3. 2 retries; guardrails must ensure fixes do not deviate from the intended purpose of the code.
4. Delete `new feature/`; create a CHANGELOG.md for version and feature tracking.
5. Agreed — Simple/None; testing occurs in practice (manual read-through per step).

## Decisions & Rationale

**Testing tier assessment flow in `/start`:**
Read ENV.md for testing preferences → ask clarifying questions → assess complexity after full scope is understood → suggest tier with explicit reasoning → user confirms or adjusts → produce artifacts. Placing the tier suggestion after clarifying questions ensures the agent has complete scope before committing to an approach. Presenting the reasoning alongside the suggestion lets the user push back on specific signals rather than just a label.

**Test sub-agent model — Option (a): sub-agent writes AND runs tests:**
A dedicated test sub-agent with a fresh context window and sole focus on "does this implementation satisfy the Acceptance criteria" will write stronger behavior-verifying tests than the implementing agent, which carries bias toward making the implementation work. The sub-agent receives: the step's Testing field, Acceptance criteria, implementation files written, and the artifact output path. It writes tests using the AAA (Arrange/Act/Assert) pattern with specific assertions and edge cases named in the Acceptance field — not generic smoke tests.

**Fix loop guardrails:**
Maximum 2 retries. On failure, the main agent fixes implementation only — it must never modify test files, relax assertions, or add special-case logic to satisfy specific test inputs. If the fix would require changing the step's intended interface or behavior as described in Goal/Acceptance, the main agent must declare a BLOCKER immediately rather than attempt a workaround. This ensures tests remain a genuine specification, not a hurdle to clear.

**Test artifacts:**
Written to `docs/tests/step_N/` per step: `pytest_output.txt` (full output), `failures.txt` (extracted failures only). The compact `failures.txt` is what `/replan` loads — full signal, no noise.

**CHANGELOG.md:**
Created at project root. First entry documents this testing integration. Provides a lightweight version history as the pattern evolves.

**`new feature/` cleanup:**
Deleted in the final step. All content is either absorbed into updated command files or superseded by the brainstorm discussion.

## Environment Choices

No Python environment — all deliverables are markdown instruction files plus one new markdown file (CHANGELOG.md). No packages, no tooling setup required.

## Testing Assessment

**Tier**: Simple / None
**Rationale**: All deliverables are markdown files. No automated testing is applicable. Correctness is verified by manual read-through of each file after editing, confirming instructions are coherent, schemas are consistent across files, and the sub-agent flow logic is unambiguous.
**Approach**: Manual review only after each step. The real test is using the updated commands in a subsequent project.

## Final Approach Summary

Update the three command files and ENV.md to integrate testing as a first-class concern in the plan→step→replan cycle. Key additions: (1) `/start` reads ENV.md for testing preferences, suggests a tier with reasoning after clarifying questions, gets user confirmation, and records the decision in both planning artifacts with updated schemas throughout; (2) `/step` runs a two-phase sub-step — implement, then launch a test sub-agent that writes and runs behavior-verifying tests — with a 2-retry fix loop (implementation only, explicit guardrails), artifact writing to `docs/tests/step_N/`, and PROGRESS.md updated with PASS/FAIL outcome; (3) `/replan` loads test failure artifacts when the blocker is test-related and reassesses the tier if scope has changed; (4) ENV.md gains a Testing section; (5) README.md documents the new system; (6) CHANGELOG.md created; (7) `new feature/` deleted.
