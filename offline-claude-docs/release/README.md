# release

Deployment-ready packages for offline Claude Code documentation.

## Contents

### `skillOnly/`

Lightweight option. Contains only the `ClaudeGuide` skill (`disable-model-invocation: true`), which reads documentation inline without spawning a subagent. Minimal overhead; good for most users.

### `skillWithAgent/`

Full option. Contains the `ClaudeGuide` skill plus a dedicated `claude-doc-guide` agent running on haiku. The agent boundary provides structural context isolation — doc lookups never pollute your main working context. Best choice if you do heavy doc traversal or hit context pressure in long sessions.

### `updateDocs/`

Contains `refresh-docs.sh`. Run this script (requires bash) to download the latest Claude Code documentation from `code.claude.com` into `~/.claude/docs/`. Run it once online; both deployment options then work fully offline.

## Choosing an option

- **Start with `skillOnly`** — it's simpler and sufficient for most usage patterns.
- **Switch to `skillWithAgent`** if you notice context pressure or want guaranteed isolation between doc lookups and your main session.

See the README in each subdirectory for deployment instructions.
