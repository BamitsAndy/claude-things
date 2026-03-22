"""
process_audit.py — Offline post-processor for .claude/TOOL_AUDIT.md

Parses the markdown table written by /tool-audit and can emit filtered
settings.json fragments without requiring a live Claude session.

Usage:
    python scripts/process_audit.py [--input PATH] [--summary | --emit-json | --deny-all | --allow-mcp]

Options:
    --input PATH    Path to TOOL_AUDIT.md (default: .claude/TOOL_AUDIT.md)
    --summary       Print tool count by category
    --emit-json     Print full draft settings.json to stdout (non-destructive)
    --deny-all      Emit a deny list for every tool found
    --allow-mcp     Emit an allow list for only MCP tools
"""

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_INPUT = Path(".claude/TOOL_AUDIT.md")


def parse_table(text: str) -> list[dict]:
    """Parse the tool table from TOOL_AUDIT.md content.

    Returns a list of dicts with keys: name, category, type, description, pattern.
    Skips the header row and separator row.
    """
    rows = []
    in_table = False

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("| Tool Name"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            # Split produces ['', col1, col2, ..., colN, ''] — drop empties at ends
            parts = [p for p in parts if p != ""]
            if len(parts) >= 5:
                rows.append({
                    "name": parts[0],
                    "category": parts[1],
                    "type": parts[2],
                    "description": parts[3],
                    "pattern": parts[4],
                })
        elif in_table and not line.startswith("|"):
            # Table ended
            break

    return rows


def summarize(rows: list[dict]) -> dict[str, int]:
    """Return tool count by category."""
    counts: dict[str, int] = {}
    for row in rows:
        cat = row["category"]
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def emit_json(rows: list[dict], mode: str = "emit-json") -> dict:
    """Build a settings.json-compatible permissions dict.

    mode: 'emit-json'  → deny list is empty (user fills in)
          'deny-all'   → deny every tool by its permission pattern
          'allow-mcp'  → allow only MCP tools, deny list empty
    """
    if mode == "deny-all":
        deny = [r["pattern"] for r in rows]
        allow: list[str] = []
    elif mode == "allow-mcp":
        deny = []
        allow = [r["pattern"] for r in rows if r["type"] == "mcp"]
    else:
        deny = []
        allow = []

    return {
        "_comment": "Draft from process_audit.py. Review TOOL_AUDIT.md, edit, rename to settings.json.",
        "permissions": {
            "deny": deny,
            "allow": allow,
        },
    }


def load_rows(input_path: Path) -> list[dict]:
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run /tool-audit first.", file=sys.stderr)
        sys.exit(1)
    return parse_table(input_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-process .claude/TOOL_AUDIT.md into settings.json fragments."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        metavar="PATH",
        help=f"Path to TOOL_AUDIT.md (default: {DEFAULT_INPUT})",
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--summary", action="store_true", help="Print tool count by category")
    mode_group.add_argument("--emit-json", action="store_true", help="Print draft settings.json to stdout")
    mode_group.add_argument("--deny-all", action="store_true", help="Emit deny list for every tool")
    mode_group.add_argument("--allow-mcp", action="store_true", help="Emit allow list for MCP tools only")

    args = parser.parse_args()
    rows = load_rows(args.input)

    if args.summary:
        counts = summarize(rows)
        total = sum(counts.values())
        print(f"Total: {total} tools\n")
        for cat, count in sorted(counts.items()):
            print(f"  {cat}: {count}")

    elif args.emit_json:
        print(json.dumps(emit_json(rows, "emit-json"), indent=2))

    elif args.deny_all:
        print(json.dumps(emit_json(rows, "deny-all"), indent=2))

    elif args.allow_mcp:
        print(json.dumps(emit_json(rows, "allow-mcp"), indent=2))


if __name__ == "__main__":
    main()
