import json
from pathlib import Path

TOOLS_PATH = Path(__file__).parent.parent / "config" / "tools.json"
MEMORY_PATH = Path(__file__).parent.parent / "config" / "memory.json"


def _all_tools() -> list[dict]:
    return json.loads(TOOLS_PATH.read_text(encoding="utf-8"))


def load_tools(session_approved: set[str] | None = None) -> list[dict]:
    """Return the tools array to pass to Claude on each API request.

    Always includes tier='simple' tools.  Adds tier='advanced' tools that are
    either persistently approved (memory.json) or approved this session.
    The 'tier' key is stripped before returning so the Claude API doesn't see it.
    """
    all_tools = _all_tools()
    baseline = [t for t in all_tools if t["tier"] == "simple"]

    approved_names = _load_persistent_approved() | (session_approved or set())
    advanced_approved = [
        t for t in all_tools
        if t["tier"] == "advanced" and t["name"] in approved_names
    ]

    result = baseline + advanced_approved
    for t in result:
        t.pop("tier", None)
    return result


def _load_persistent_approved() -> set[str]:
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        return set(data.get("approved_tools", []))
    except Exception:
        return set()


def save_approved(tool_name: str) -> None:
    """Persist a tool approval to memory.json."""
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data.setdefault("approved_tools", [])
    if tool_name not in data["approved_tools"]:
        data["approved_tools"].append(tool_name)
        MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
