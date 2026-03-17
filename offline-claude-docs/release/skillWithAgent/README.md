# skillWithAgent

Deploys the `ClaudeGuide` skill plus a dedicated `claude-doc-guide` agent for offline Claude Code documentation lookups. The agent runs on haiku (fast and cost-efficient) with Read, Grep, and Glob tools, providing structural context isolation for every doc lookup.

## Contents

```
.claude/
  agents/
    claude-doc-guide.md
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

Add the following to your `CLAUDE.md` to route documentation queries to the local agent:

```markdown
## Agent Routing
For all Claude Code documentation queries, use the claude-doc-guide agent.
```

## Notes

- The agent uses haiku for speed and cost efficiency — doc lookups are fast.
- Context isolation is structural: the agent boundary guarantees doc traversal never bleeds into your main working context, regardless of how much documentation you look up.
