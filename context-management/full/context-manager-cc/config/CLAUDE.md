<!-- context-manager-cc: begin -->
## Tool Catalogue (context-manager-cc)

Some tools are not loaded into context to reduce token usage. If you need one,
ask the user first.

### Always available
Read, Write, Glob, Grep, Edit, AskUserQuestion, ExitPlanMode, Bash,
TaskCreate, TaskGet, TaskList, TaskUpdate, TaskStop

### Requires approval (currently not in context)
<!-- DENIED_TOOLS_PLACEHOLDER -->

**If you need an unavailable tool:**
1. Tell the user which tool you need and why
2. Ask: "May I use [ToolName]?"
3. If yes: use Write to add the tool name to `approved_tools` in
   `.claude/context-manager-cc/memory.json`
4. Inform the user: "Approval saved. Run `python install.py --sync` or start
   a new conversation to activate [ToolName]."
<!-- context-manager-cc: end -->
