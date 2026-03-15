# Claude Workflow Instructions

Use `/start` to begin the planning phase for a new request.
Use `/step` to implement one step at a time.
Use `/replan` if a blocker is encountered during a step.

Skills auto-trigger on natural language too:
- "plan this" / "new plan" → `/start`
- "next step" / "continue" → `/step`
- "resolve blocker" / "replan" → `/replan`

# Additional Context
only read listed markdowns if required for current step.
- `.claude/ENV.md` for environment preferences.
- '' prefered testing patterns
- '' prefered UX / UI packages
- ''
