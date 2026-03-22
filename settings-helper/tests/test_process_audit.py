"""
Tests for scripts/process_audit.py

Run with: pytest tests/test_process_audit.py -v
"""

import json
import sys
from pathlib import Path

# Allow importing the script directly without a package install
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from process_audit import parse_table, emit_json, summarize


SAMPLE_TABLE = """\
# Tool Audit

Generated: 2026-03-20
Session total: 5 tools (3 builtin, 2 mcp)

## Tool Table

| Tool Name | Category | Type | Description | Permission Pattern |
|-----------|----------|------|-------------|-------------------|
| Read | core-fs | builtin | Read a file from the filesystem | Read |
| Write | core-fs | builtin | Write content to a file | Write |
| Bash | core-shell | builtin | Execute a shell command | Bash(*) |
| mcp__github__create_issue | mcp-github | mcp | Create a GitHub issue | mcp__github__create_issue |
| mcp__github__list_prs | mcp-github | mcp | List pull requests in a repo | mcp__github__list_prs |

## Summary by Category
"""


def test_parse_table_row_count():
    """parse_table extracts the correct number of rows from a sample audit file."""
    rows = parse_table(SAMPLE_TABLE)
    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"


def test_parse_table_fields():
    """parse_table correctly extracts all fields for each row."""
    rows = parse_table(SAMPLE_TABLE)

    # First row: Read
    assert rows[0]["name"] == "Read"
    assert rows[0]["category"] == "core-fs"
    assert rows[0]["type"] == "builtin"
    assert rows[0]["pattern"] == "Read"

    # MCP row: mcp__github__create_issue
    mcp_row = rows[3]
    assert mcp_row["name"] == "mcp__github__create_issue"
    assert mcp_row["category"] == "mcp-github"
    assert mcp_row["type"] == "mcp"
    assert mcp_row["pattern"] == "mcp__github__create_issue"


def test_emit_json_structure():
    """emit_json returns valid JSON with permissions.deny and permissions.allow keys."""
    rows = parse_table(SAMPLE_TABLE)
    result = emit_json(rows)

    # Must be JSON-serializable
    serialized = json.dumps(result)
    parsed = json.loads(serialized)

    assert "permissions" in parsed
    assert "deny" in parsed["permissions"]
    assert "allow" in parsed["permissions"]
    assert isinstance(parsed["permissions"]["deny"], list)
    assert isinstance(parsed["permissions"]["allow"], list)


def test_emit_json_deny_all():
    """emit_json with deny-all mode includes every tool's pattern in the deny list."""
    rows = parse_table(SAMPLE_TABLE)
    result = emit_json(rows, mode="deny-all")

    deny = result["permissions"]["deny"]
    assert len(deny) == 5
    assert "Read" in deny
    assert "mcp__github__create_issue" in deny


def test_emit_json_allow_mcp():
    """emit_json with allow-mcp mode includes only MCP tools in the allow list."""
    rows = parse_table(SAMPLE_TABLE)
    result = emit_json(rows, mode="allow-mcp")

    allow = result["permissions"]["allow"]
    assert len(allow) == 2
    assert "mcp__github__create_issue" in allow
    assert "mcp__github__list_prs" in allow
    assert "Read" not in allow


def test_summarize():
    """summarize returns correct counts per category."""
    rows = parse_table(SAMPLE_TABLE)
    counts = summarize(rows)

    assert counts["core-fs"] == 2
    assert counts["core-shell"] == 1
    assert counts["mcp-github"] == 2
