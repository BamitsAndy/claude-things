"""
Reads tools.json and computes which tools should be denied based on memory.json.
"""
import json
from pathlib import Path


def _load_tools(tools_path: str | Path) -> list[dict]:
    with open(tools_path, encoding="utf-8") as f:
        return json.load(f)


def _load_approved(memory_path: str | Path) -> list[str]:
    with open(memory_path, encoding="utf-8") as f:
        data = json.load(f)
    return [t.strip() for t in data.get("approved_tools", [])]


def get_tier(tool_name: str, tools_path: str | Path) -> str:
    """Return 'simple' or 'advanced' for the named tool. Raises KeyError if not found."""
    tools = _load_tools(tools_path)
    for t in tools:
        if t["name"] == tool_name:
            return t["tier"]
    raise KeyError(f"Tool '{tool_name}' not found in {tools_path}")


def get_advanced_tools(tools_path: str | Path) -> list[str]:
    """Return names of all tools with tier == 'advanced'."""
    return [t["name"] for t in _load_tools(tools_path) if t["tier"] == "advanced"]


def get_simple_tools(tools_path: str | Path) -> list[str]:
    """Return names of all tools with tier == 'simple'."""
    return [t["name"] for t in _load_tools(tools_path) if t["tier"] == "simple"]


def get_denied_tools(tools_path: str | Path, memory_path: str | Path) -> list[str]:
    """Return advanced tools that have NOT been approved (i.e. should stay in deny list)."""
    advanced = set(get_advanced_tools(tools_path))
    approved = set(_load_approved(memory_path))
    return sorted(advanced - approved)


def get_approved_advanced_tools(tools_path: str | Path, memory_path: str | Path) -> list[str]:
    """Return advanced tools that have been approved (move from deny to allow)."""
    advanced = set(get_advanced_tools(tools_path))
    approved = set(_load_approved(memory_path))
    return sorted(advanced & approved)
