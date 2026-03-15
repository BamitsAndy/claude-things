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

## Testing Strategy Assessment

Before producing the planning artifacts, assess the complexity of the implementation and assign a testing tier. Use your judgment based on factors such as: number of modules and their interdependencies, presence of external services or I/O, statefulness, concurrency, error surface, and expected public API size.

### Tiers

**Simple**
Straightforward scripts or single-purpose tools with minimal branching and no external dependencies. Recommended approach: inline assertions and a smoke test script. No pytest setup required.

**Moderate**
Multi-module projects with some logic complexity, limited external dependencies, or a small public API. Recommended approach: pytest with unit tests covering core logic. No fixtures or mocks unless clearly needed.

**Custom**
Use this tier when the project doesn't fit Simple or Moderate — for example: significant external integrations, async or concurrent logic, complex state machines, or a non-trivial public API. Define a bespoke testing approach and name it clearly (e.g. "Integration-first", "Contract-tested", "Layered"). Describe what layers of testing are needed and why.

### Output

The chosen tier and its rationale must be recorded in both:
- `docs/initial/PLAN_verbose.md` under **Testing Assessment**
- `docs/plan/PLAN.md` under **Testing Strategy**

---

## Artifact Schemas

### docs/plan/PLAN.md

```md
# Implementation Plan

## Context
<!-- Why this project exists and what problem it solves -->

## Testing Strategy
**Tier**: [Simple | Moderate | Custom — name]
**Approach**: <!-- One paragraph: what will be tested, with what tools, and at what granularity -->
**Rationale**: <!-- Why this tier was chosen for this project -->

## Steps

### Step 1: [Title]
- **Goal**: What this step achieves
- **Files**: Files to create or modify
- **Acceptance**: How to verify this step is done
- **Testing**: <!-- What testing applies to this step, if any. Reference the Testing Strategy and note any step-specific requirements or exclusions. Use "None — [reason]" if no testing is needed for this step. -->
- **Context files**: Files Claude should read before starting

### Step 2: [Title]
- **Goal**:
- **Files**:
- **Acceptance**:
- **Testing**:
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

## Testing Assessment
**Tier**: [Simple | Moderate | Custom — name]
**Rationale**: <!-- Detailed reasoning for the chosen tier, including the signals that drove the decision -->
**Approach**: <!-- Full description of the testing approach: tools, layers, conventions, and any coverage expectations -->

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
