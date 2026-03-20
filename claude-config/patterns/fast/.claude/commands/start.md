---
description: Planning phase. Run when starting a new feature or project. Produces all planning artifacts before any code is written.
triggers: /start, "begin planning", "new plan", "plan this", "start planning"
---

Use the builtin plan agent.

If arguments were provided with this command, use $ARGUMENTS as the user's request.
Otherwise, read `docs/initial/PlanningPrompts.md` and use the most recent entry (last `---` section) as the request.

Ask clarifying questions before doing anything else.

Once all questions are answered, produce all four planning artifacts:

1. `docs/initial/PLAN_verbose.md` — questions, answers, assumptions and decisions
2. `docs/plan/PLAN.md` — concise numbered steps
3. `docs/plan/PROGRESS.md` — step tracker
4. Update `docs/initial/PlanningPrompts.md` with any refined version of the request if needed

Do NOT write any implementation code during this phase.

---

## Artifact Schemas

### docs/plan/PLAN.md

```md
# Implementation Plan

## Context
<!-- Why this project exists and what problem it solves -->

## Steps

### Step 1: [Title]
- **Goal**: What this step achieves
- **Files**: Files to create or modify
- **Acceptance**: How to verify this step is done
- **Context files**: Files Claude should read before starting

### Step 2: [Title]
- **Goal**:
- **Files**:
- **Acceptance**:
- **Context files**:
```

### docs/plan/PROGRESS.md

```md
# Progress

## Current Step: 1

## Steps
- [ ] 1 - [Title] | context: docs/plan/PLAN.md
- [ ] 2 - [Title] | context: docs/plan/PLAN.md

## Notes
<!-- General findings or session context not tied to a specific step -->
```

Blockers are recorded inline under the relevant step:
```
- [ ] 2 - [Title] | context: docs/plan/PLAN.md
  > BLOCKER: [description — run /replan to resolve]
```

### docs/initial/PLAN_verbose.md

```md
# Verbose Planning Record

## Questions Asked
<!-- List each clarifying question Claude asked -->

## User Responses
<!-- Answers given, verbatim or paraphrased -->

## Decisions & Rationale
<!-- Key decisions made and why -->

## Environment Choices
<!-- Python version, tooling, packages decided on -->

## Final Approach Summary
<!-- High-level description of the chosen implementation approach -->
```

When `/replan` runs, append a section:
```md
## Replan — Step N: [blocker summary]

### Blocker
<!-- What the blocker was -->

### Resolution
<!-- What was decided and why -->

### Plan Changes
<!-- Steps modified, added, or removed -->
```
