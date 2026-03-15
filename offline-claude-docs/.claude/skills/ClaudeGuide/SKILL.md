---
name: ClaudeGuide
description: Offline Claude Code documentation guide. Use when the user asks about Claude Code features, capabilities, configuration, commands, hooks, skills, subagents, or any other Claude Code topic.
disable-model-invocation: true
---

# Offline Claude Code Guide

This skill provides offline access to Claude Code documentation when the built-in `claude-code-guide` subagent cannot fetch documentation from the network.

## Documentation Location

All Claude Code documentation is available locally at `~/.claude/docs/`. First read the documentation map to find which file contains the relevant information.

## How to Answer Questions

Use `$ARGUMENTS` to access the user's question and follow these steps to provide an accurate and helpful response:

1. Read `~/.claude/docs/claude_code_docs_map.md` to identify which documentation file(s) contain the relevant information
2. Read the appropriate documentation file(s) from `~/.claude/docs/`
3. Provide accurate information based on the official documentation
4. Include relevant examples and code snippets from the docs
