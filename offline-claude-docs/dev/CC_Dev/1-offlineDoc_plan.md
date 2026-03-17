# Plugin Fix & Deployment: offline-claude-code-guide

## Context

The plugin has a one-line bash compatibility bug preventing `refresh-docs.sh` from running on Git Bash (Windows). The fix enables running the refresh on an internet-connected Windows machine, which will download all current docs (including the missing `migration-guide.md`) before deploying the plugin to the offline Windows environment.

---

## The Problem

`scripts/refresh-docs.sh` line 22 uses BSD sed syntax (`sed -i ''`) which is macOS-only. Git Bash on Windows ships with GNU sed, which rejects the empty string backup extension.

```bash
# Line 22 - CURRENT (broken on Git Bash / GNU sed):
sed -i '' 's|(https://code.claude.com/docs/en/|(./|g' "$DOCS_DIR/claude_code_docs_map.md"

# FIXED (GNU sed compatible, also works on Linux):
sed -i 's|(https://code.claude.com/docs/en/|(./|g' "$DOCS_DIR/claude_code_docs_map.md"
```

No other changes are needed. All other script constructs (`curl`, `grep -oE`, `BASH_SOURCE`, `set -Eeuo pipefail`, `wc -l | xargs`) work correctly in Git Bash.

---

## Change Required

**File:** `scripts/refresh-docs.sh`, **line 22**

| | Content |
|---|---|
| Old | `sed -i '' 's\|(https://code.claude.com/docs/en/\|(./\|g' "$DOCS_DIR/claude_code_docs_map.md"` |
| New | `sed -i 's\|(https://code.claude.com/docs/en/\|(./\|g' "$DOCS_DIR/claude_code_docs_map.md"` |

---

## Deployment Workflow (After the Fix)

1. **On internet-connected Windows machine** (with Git for Windows installed):
   ```bash
   bash "plugin to test/offline-claude-code-guide/scripts/refresh-docs.sh"
   ```
   This downloads all current docs to `docs/`, including `migration-guide.md` and any docs added since Nov 2025.

2. **Verify** the `docs/` folder now contains `migration-guide.md` and no `null`-content files remain.

3. **Copy the plugin folder** to the offline Windows deployment machine (the `docs/` folder travels with it).

4. **Install the plugin** on the offline machine — the cached docs serve all queries without internet.

---

## Verification Steps

After running the refresh script:
- Confirm `docs/migration-guide.md` exists
- Confirm `docs/claude_code_docs_map.md` no longer contains `https://code.claude.com/docs/en/` absolute links (they should be `./` relative)
- Confirm no files contain only `null` as their content

After deploying to offline machine:
- Ask Claude: "What are the Claude Code keyboard shortcuts?" → should read `interactive-mode.md`
- Ask Claude: "How do I configure a proxy?" → should read `network-config.md`
- Ask Claude: "How do I migrate?" → should now read `migration-guide.md`
