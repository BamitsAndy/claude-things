# Dev Note: offline-claude-code-guide Plugin Update

**Date:** 2026-03-05
**Plugin:** `plugin to test/offline-claude-code-guide`

---

## What Was Done

### Bug Fix — `scripts/refresh-docs.sh` line 22

The refresh script used BSD `sed` syntax (`sed -i ''`) which is macOS-only. Git Bash on Windows uses GNU sed, which rejects the empty string backup extension, causing the script to fail.

**Fix applied:**
```bash
# Before (macOS only):
sed -i '' 's|(https://code.claude.com/docs/en/|(./|g' "$DOCS_DIR/claude_code_docs_map.md"

# After (GNU sed / Git Bash / Linux compatible):
sed -i 's|(https://code.claude.com/docs/en/|(./|g' "$DOCS_DIR/claude_code_docs_map.md"
```

### Docs Refresh — Run on 2026-03-05

After applying the fix, `refresh-docs.sh` was run successfully on this internet-connected Windows machine.

**Result:** 62 markdown files downloaded to `docs/`

---

## Verification Results

| Check | Result |
|---|---|
| Absolute links in `claude_code_docs_map.md` | None — all converted to `./` relative |
| Files containing only `null` | None — none were removed |
| `docs/migration-guide.md` present | **Not found** — page does not exist on `code.claude.com` at this time |

> **Note:** `migration-guide.md` was expected based on prior planning but is not linked in the live docs map. It may not exist on the site or may be under a different filename.

---

## Deployment Steps (To Offline Machine)

1. Copy the entire `offline-claude-code-guide/` folder to the offline machine — `docs/` travels with it
2. Install the plugin on the offline machine
3. Verify queries like "What are the Claude Code keyboard shortcuts?" resolve correctly from cached docs

---

## Files Changed

- `scripts/refresh-docs.sh` — one-line sed fix (line 22)
- `docs/` — all 62 `.md` files refreshed from `code.claude.com`
