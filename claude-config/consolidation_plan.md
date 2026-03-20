# Consolidation Plan

## What This Is

Documents the structural decisions made on 2026-03-20 to organise the `claude-config` repo for parallel development of two variants.

---

## Background

The `claude-config` repo holds two variants of a Claude Code development pattern:

- **`fast/`** — v1.0.0, no testing integration. The minimal baseline: plan → step → replan with ENV.md and three command files.
- **`full/`** — v1.1.0, with testing integration. Adds testing tier assessment in `/start`, a two-phase sub-step model with a dedicated test sub-agent in `/step`, failure artifact loading in `/replan`, and a Testing section in `ENV.md`.

Both are actively developed in parallel.

---

## Why Artefacts Moved to Parent

Planning artefacts (PLAN.md, PROGRESS.md, PLAN_verbose.md) and the CHANGELOG previously lived inside `full/`. This was a problem:

- The CHANGELOG documents the evolution of the *pattern*, not just the `full` variant. It should be accessible without knowing which variant to look in.
- Planning artefacts for the pattern's own development are not variant-specific — they describe decisions made at the repo level.
- As both variants develop in parallel, having one variant "own" shared history creates confusion.

Moving them to the parent makes the repo structure reflect reality: the variants are peers, and their shared history lives above both.

---

## Parallel Development Intent

`fast/` and `full/` are not a migration path — you don't graduate from one to the other. They serve different use cases:

- Use `fast/` when you want the lightweight pattern with no testing overhead.
- Use `full/` when you want testing integrated into every implementation step.

Each variant has its own `docs/initial/README.md` with full usage instructions. The parent `README.md` describes both and links to each.

---

## Repo Structure After Consolidation

```
claude-config/
├── README.md                        # Describes both variants; links to sub-READMEs
├── CHANGELOG.md                     # Version history covering both variants
├── consolidation_plan.md            # This file
├── docs/
│   ├── plan/
│   │   ├── PLAN.md                  # Implementation plan for the testing integration work
│   │   └── PROGRESS.md              # Step tracker (all steps complete)
│   └── initial/
│       └── PLAN_verbose.md          # Full Q&A and decision record for the testing integration
├── fast/                            # v1.0.0 — no testing integration
│   └── docs/
│       ├── plan/                    # Empty template directory
│       └── initial/
│           ├── README.md
│           └── PlanningPrompts.md
└── full/                            # v1.1.0 — with testing integration
    └── docs/
        ├── plan/                    # Empty template directory (artefacts moved to parent)
        └── initial/
            ├── README.md
            └── PlanningPrompts.md
```

---

## Pointers

- Version history: [`CHANGELOG.md`](CHANGELOG.md)
- Implementation plan (testing integration): [`docs/plan/PLAN.md`](docs/plan/PLAN.md)
- Full planning record: [`docs/initial/PLAN_verbose.md`](docs/initial/PLAN_verbose.md)
- `fast` variant: [`fast/docs/initial/README.md`](fast/docs/initial/README.md)
- `full` variant: [`full/docs/initial/README.md`](full/docs/initial/README.md)
