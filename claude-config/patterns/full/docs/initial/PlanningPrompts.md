# Planning Prompts

<!-- Add new prompts at the bottom, newest last.
     Separate entries with ---
     The /start command reads the most recent entry. -->

---

## 2026-03-14

Add testing integration to the claude-config workflow pattern. Update `/start` to assess project complexity and suggest a testing tier (Simple / Moderate / Custom) with reasoning, reading ENV.md for preferences, getting user confirmation before producing artifacts. Update `/step` to run a two-phase sub-step: implement, then launch a test sub-agent that writes and runs behavior-verifying tests (AAA pattern, specific assertions, edge cases from Acceptance criteria), with a 2-retry fix loop (implementation only, explicit guardrails against weakening tests) and artifact output to `docs/tests/step_N/`. Update `/replan` to load test failure artifacts when the blocker is test-related, and reassess the tier if scope changes. Add a Testing section to ENV.md. Update README.md to document the system. Create CHANGELOG.md. Delete `new feature/` directory.
