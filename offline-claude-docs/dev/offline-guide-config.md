# Offline Guide — Claude Code Config Summary

## Recommended Setup: `settings.json` + `CLAUDE.md`

The goal is to disable the built-in `claude-code-guide` agent and replace it with a local mirrored docs skill.

### How it works

- `settings.json` **hard-removes** the built-in agent from the prompt (same mechanism as denying `bash`)
- `CLAUDE.md` **positively routes** Claude to your local skill in its place
- Together they give a structural "no" and a clear "yes"

---

### `settings.json`

```json
{
  "permissions": {
    "deny": ["Agent(claude-code-guide)"]
  }
}
```

### `CLAUDE.md`

```markdown
## Agent Routing
For all Claude Code documentation queries, load and follow the skill at `/offline-guide/SKILL.md` before responding.
```

---

## Future Options

### Option 1 — Soft Subagent (minimal change)

Add to `CLAUDE.md`:

```markdown
## Agent Routing
For all Claude Code documentation queries, spawn a subagent and load `/offline-guide/SKILL.md` within that subagent context before responding.
```

**Why over basic skill:** Isolates doc lookup context from your main working context, keeping the parent window cleaner on heavier sessions.

**Caveat:** Still a soft instruction — Claude may inline the skill on simple lookups rather than always spawning.

---

### Option 2 — Full Subagent Replacement

Promote `/offline-guide` to a proper named subagent with its own scoped `CLAUDE.md`, invoked explicitly by the parent agent.

**Why over basic skill:** The subagent boundary is structural rather than instructional — context isolation is guaranteed every time, not just when Claude judges it necessary.

**Benefit:** Best choice if you find yourself doing multi-file doc traversal or hitting context pressure in doc-heavy sessions. The basic skill is the right starting point; promote to this only when usage patterns justify it.
