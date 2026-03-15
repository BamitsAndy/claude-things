"""
Reads and writes .claude/settings.json, managing permissions.deny and permissions.allow.
"""
import json
from pathlib import Path

from core.tool_loader import get_denied_tools, get_approved_advanced_tools


def _settings_path(dot_claude_path: str | Path) -> Path:
    return Path(dot_claude_path) / "settings.json"


def read_settings(dot_claude_path: str | Path) -> dict:
    """Parse .claude/settings.json. Returns {} if file does not exist."""
    path = _settings_path(dot_claude_path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_settings(dot_claude_path: str | Path, data: dict) -> None:
    """Write data back to .claude/settings.json (pretty-printed)."""
    path = _settings_path(dot_claude_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def apply_deny_list(dot_claude_path: str | Path, tools: list[str]) -> None:
    """
    Merge *tools* into permissions.deny in settings.json.
    Existing entries not in *tools* are preserved.
    """
    settings = read_settings(dot_claude_path)
    permissions = settings.setdefault("permissions", {})
    existing_deny = set(permissions.get("deny", []))
    existing_deny.update(tools)
    permissions["deny"] = sorted(existing_deny)
    write_settings(dot_claude_path, settings)


def apply_allow_list(dot_claude_path: str | Path, tools: list[str]) -> None:
    """
    Merge *tools* into permissions.allow in settings.json.
    Existing entries not in *tools* are preserved.
    """
    settings = read_settings(dot_claude_path)
    permissions = settings.setdefault("permissions", {})
    existing_allow = set(permissions.get("allow", []))
    existing_allow.update(tools)
    permissions["allow"] = sorted(existing_allow)
    write_settings(dot_claude_path, settings)


def remove_from_deny(dot_claude_path: str | Path, tools: list[str]) -> None:
    """Remove *tools* from permissions.deny (used when they get approved)."""
    settings = read_settings(dot_claude_path)
    permissions = settings.setdefault("permissions", {})
    existing_deny = set(permissions.get("deny", []))
    existing_deny -= set(tools)
    permissions["deny"] = sorted(existing_deny)
    write_settings(dot_claude_path, settings)


def sync(dot_claude_path: str | Path, tools_path: str | Path, memory_path: str | Path) -> dict:
    """
    Recompute deny/allow lists from tools.json + memory.json and write to settings.json.

    Returns a dict with keys 'denied' and 'allowed' listing what was written.
    """
    denied = get_denied_tools(tools_path, memory_path)
    allowed_advanced = get_approved_advanced_tools(tools_path, memory_path)

    settings = read_settings(dot_claude_path)
    permissions = settings.setdefault("permissions", {})

    # Rebuild deny: preserve any non-managed entries, replace managed ones
    existing_deny = set(permissions.get("deny", []))
    # Remove all advanced tools from deny, then add back only the denied ones
    from core.tool_loader import get_advanced_tools
    all_advanced = set(get_advanced_tools(tools_path))
    existing_deny -= all_advanced
    existing_deny.update(denied)
    permissions["deny"] = sorted(existing_deny)

    # Rebuild allow: preserve any non-managed entries, replace managed ones
    existing_allow = set(permissions.get("allow", []))
    existing_allow -= all_advanced
    existing_allow.update(allowed_advanced)
    permissions["allow"] = sorted(existing_allow)

    write_settings(dot_claude_path, settings)

    return {"denied": denied, "allowed": allowed_advanced}
