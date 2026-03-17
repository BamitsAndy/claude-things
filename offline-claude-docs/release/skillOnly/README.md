# skillOnly

Deploys the `ClaudeGuide` skill for offline Claude Code documentation lookups. No subagent is used — the skill runs inline with `disable-model-invocation: true`.

## Contents

```
.claude/
  skills/
    ClaudeGuide/
      SKILL.md
```

## Prerequisites

Docs must be present at `~/.claude/docs/` before use. If you haven't done this yet, run the refresh script first:

```bash
../updateDocs/refresh-docs.sh
```

## Deployment

Copy the `.claude/` folder into your project root, or into `~/.claude/` for user-level availability across all projects.

### `settings.json`

Add the following to your `settings.json` (`.claude/settings.json` or `~/.claude/settings.json`) to disable the built-in `claude-code-guide` agent:

```json
{
  "permissions": {
    "deny": ["Agent(claude-code-guide)"]
  }
}
```

### `CLAUDE.md`

Add the following to your `CLAUDE.md` to route documentation queries to the local skill:

```markdown
## Agent Routing
For all Claude Code documentation queries, load and follow the ClaudeGuide skill before responding.
```
