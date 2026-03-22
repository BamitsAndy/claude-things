# Tool Audit

Generated: 2026-03-20
Session total: 37 tools (26 builtin, 11 mcp)

## Tool Table

| Tool Name | Category | Type | Description | Permission Pattern |
|-----------|----------|------|-------------|-------------------|
| Agent | agent | builtin | Launches specialized sub-agents for complex multi-step tasks | Agent |
| Bash | core-shell | builtin | Executes bash commands in the shell environment | Bash |
| Glob | core-search | builtin | Finds files by glob pattern, sorted by modification time | Glob |
| Grep | core-search | builtin | Searches file contents using ripgrep with regex support | Grep |
| Read | core-fs | builtin | Reads files from the local filesystem, including images and PDFs | Read |
| Edit | core-fs | builtin | Performs exact string replacements in existing files | Edit |
| Write | core-fs | builtin | Writes or overwrites files on the local filesystem | Write |
| Skill | other | builtin | Executes a named user-invocable skill (slash command) | Skill |
| ToolSearch | other | builtin | Fetches full schema definitions for deferred tools | ToolSearch |
| AskUserQuestion | other | builtin | Pauses execution to ask the user a clarifying question | AskUserQuestion |
| CronCreate | other | builtin | Creates a scheduled cron job to run a command on a recurring interval | CronCreate |
| CronDelete | other | builtin | Deletes an existing cron job by ID | CronDelete |
| CronList | other | builtin | Lists all currently configured cron jobs | CronList |
| EnterPlanMode | other | builtin | Enters plan mode to design implementation strategies before writing code | EnterPlanMode |
| ExitPlanMode | other | builtin | Exits plan mode and returns to normal execution | ExitPlanMode |
| EnterWorktree | core-nav | builtin | Enters a git worktree for isolated branch work | EnterWorktree |
| ExitWorktree | core-nav | builtin | Exits the current git worktree and returns to the main repo | ExitWorktree |
| NotebookEdit | core-fs | builtin | Edits cells in a Jupyter notebook file | NotebookEdit |
| TaskCreate | other | builtin | Creates a new background task to track work in the current conversation | TaskCreate |
| TaskGet | other | builtin | Retrieves the status and details of a specific task | TaskGet |
| TaskList | other | builtin | Lists all tasks in the current conversation | TaskList |
| TaskOutput | other | builtin | Reads the output of a background task | TaskOutput |
| TaskStop | other | builtin | Stops a running background task | TaskStop |
| TaskUpdate | other | builtin | Updates the status or details of an existing task | TaskUpdate |
| WebFetch | other | builtin | Fetches content from a URL and returns it as text | WebFetch |
| WebSearch | other | builtin | Searches the web and returns relevant results | WebSearch |
| mcp__claude_ai_Google_Calendar__gcal_create_event | mcp-google-calendar | mcp | Creates a new event on Google Calendar | mcp__claude_ai_Google_Calendar__gcal_create_event |
| mcp__claude_ai_Google_Calendar__gcal_delete_event | mcp-google-calendar | mcp | Deletes an existing Google Calendar event | mcp__claude_ai_Google_Calendar__gcal_delete_event |
| mcp__claude_ai_Google_Calendar__gcal_find_meeting_times | mcp-google-calendar | mcp | Finds available meeting times across calendars | mcp__claude_ai_Google_Calendar__gcal_find_meeting_times |
| mcp__claude_ai_Google_Calendar__gcal_find_my_free_time | mcp-google-calendar | mcp | Finds free time blocks on the user's Google Calendar | mcp__claude_ai_Google_Calendar__gcal_find_my_free_time |
| mcp__claude_ai_Google_Calendar__gcal_get_event | mcp-google-calendar | mcp | Retrieves details of a specific Google Calendar event | mcp__claude_ai_Google_Calendar__gcal_get_event |
| mcp__claude_ai_Google_Calendar__gcal_list_calendars | mcp-google-calendar | mcp | Lists all calendars available to the user | mcp__claude_ai_Google_Calendar__gcal_list_calendars |
| mcp__claude_ai_Google_Calendar__gcal_list_events | mcp-google-calendar | mcp | Lists events from a Google Calendar within a time range | mcp__claude_ai_Google_Calendar__gcal_list_events |
| mcp__claude_ai_Google_Calendar__gcal_respond_to_event | mcp-google-calendar | mcp | Responds to a Google Calendar event invitation (accept/decline/maybe) | mcp__claude_ai_Google_Calendar__gcal_respond_to_event |
| mcp__claude_ai_Google_Calendar__gcal_update_event | mcp-google-calendar | mcp | Updates an existing Google Calendar event | mcp__claude_ai_Google_Calendar__gcal_update_event |
| mcp__ide__executeCode | mcp-ide | mcp | Executes code in the connected IDE environment | mcp__ide__executeCode |
| mcp__ide__getDiagnostics | mcp-ide | mcp | Retrieves diagnostics (errors, warnings) from the connected IDE | mcp__ide__getDiagnostics |

## Summary by Category

| Category | Count |
|----------|-------|
| core-fs | 4 |
| core-shell | 1 |
| core-search | 2 |
| core-nav | 2 |
| agent | 1 |
| other | 16 |
| mcp-google-calendar | 9 |
| mcp-ide | 2 |

## How to Disable This Audit Command

When you no longer need to run tool audits, delete the command file:

```bash
rm .claude/commands/tool-audit.md
```

Then reload Claude Code. The `/tool-audit` command will no longer appear in autocomplete.
