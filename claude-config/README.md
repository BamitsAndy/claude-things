# claude-config

A reusable Claude Code workflow pattern that enforces a disciplined **plan → implement step → replan** cycle.

Claude's context window fills up fast. Without structure, a session sprawls from requirements gathering to half-implemented code to debugging — all mixed together. This pattern solves that by enforcing two distinct modes: a planning phase (no code written) and an implementation phase (one step per session, fresh context each time).

---

## Variants

Both variants are actively developed in parallel.

| Variant | Testing | Version | Details |
|---|---|---|---|
| [`patterns/fast/`](patterns/fast/docs/initial/README.md) | No testing integration | v1.0.0 | Minimal — plan → step → replan with no test sub-agent |
| [`patterns/full/`](patterns/full/docs/initial/README.md) | With testing integration | v1.1.0 | Adds testing tier assessment, test sub-agent per step, and failure artifacts |

---

## Shared Artefacts

These live at the repo root and are version-agnostic:

| Artefact | Purpose |
|---|---|
| [`CHANGELOG.md`](CHANGELOG.md) | Version history covering both variants |
| [`docs/plan/PLAN.md`](docs/plan/PLAN.md) | Implementation plan for this repo's own development |
| [`docs/plan/PROGRESS.md`](docs/plan/PROGRESS.md) | Step tracker for this repo's own development |
| [`docs/initial/PLAN_verbose.md`](docs/initial/PLAN_verbose.md) | Full planning record (Q&A, decisions, rationale) |
| [`consolidation_plan.md`](consolidation_plan.md) | Documents the consolidation decisions for this repo structure |

---

## Quick Start

1. Pick a variant (`patterns/fast/` or `patterns/full/`) and copy its contents into your project root.
2. Fill in `.claude/ENV.md` with your environment preferences.
3. Open Claude Code and run `/start your request here`.

See the variant's `docs/initial/README.md` for full usage instructions.
