# offline-claude-docs

Provides offline Claude Code documentation via a local skill and/or dedicated agent. No network access required once docs are downloaded.

## Attribution

Inspired by and draws from [motlin/claude-code-plugins](https://github.com/motlin/claude-code-plugins/tree/main/plugins/offline-claude-code-guide).
I have completely borrowed the idea and especially the update script, however did not want the plugin approach and wanted to expand usecases and disconnect the update from the CC usage.
Thanks Motlin.

## How it works

The built-in `claude-code-guide` agent calls out to the network. This project replaces it with a local alternative that reads documentation from `~/.claude/docs/` — a folder you populate in advance using the included refresh script.

The configuration uses two mechanisms together:
- `settings.json` hard-removes the built-in agent from the prompt (same as denying `bash`)
- `CLAUDE.md` positively routes documentation queries to the local replacement

## Deployment options

Two deployment packages are provided in `release/`:

| Option | Description |
|--------|-------------|
| **skillOnly** | Lightweight `ClaudeGuide` skill. Simple, no subagent overhead. Good starting point. |
| **skillWithAgent** | `ClaudeGuide` skill + dedicated `claude-doc-guide` agent (haiku model). Better context isolation for doc-heavy sessions. |

Use **skillOnly** for most cases. Upgrade to **skillWithAgent** if you find doc lookups creating context pressure in long sessions.

## Refreshing documentation

The `release/updateDocs/refresh-docs.sh` script downloads the latest docs from `code.claude.com` into `~/.claude/docs/`. Run it once while online; afterward everything works offline.

**Prerequisites:** Git Bash (Windows), Linux, or macOS — the script requires a bash-compatible shell.

## Getting started

See [`release/README.md`](release/README.md) for deployment instructions.
