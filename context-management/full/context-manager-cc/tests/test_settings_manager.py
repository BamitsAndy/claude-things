"""
Unit tests for core/settings_manager.py and core/tool_loader.py.
"""
import json
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import settings_manager, tool_loader

CONFIG_DIR = Path(__file__).parent.parent / "config"
TOOLS_PATH = CONFIG_DIR / "tools.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dot_claude(tmp_path):
    """A temporary .claude directory."""
    d = tmp_path / ".claude"
    d.mkdir()
    return d


@pytest.fixture
def memory_none(tmp_path):
    """memory.json with no approved tools."""
    p = tmp_path / "memory.json"
    p.write_text(json.dumps({"approved_tools": []}), encoding="utf-8")
    return p


@pytest.fixture
def memory_webfetch(tmp_path):
    """memory.json with WebFetch approved."""
    p = tmp_path / "memory.json"
    p.write_text(json.dumps({"approved_tools": ["WebFetch"]}), encoding="utf-8")
    return p


@pytest.fixture
def memory_all_advanced(tmp_path):
    """memory.json with all advanced tools approved."""
    advanced = tool_loader.get_advanced_tools(TOOLS_PATH)
    p = tmp_path / "memory.json"
    p.write_text(json.dumps({"approved_tools": advanced}), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# tool_loader tests
# ---------------------------------------------------------------------------

class TestToolLoader:
    def test_get_advanced_tools_nonempty(self):
        advanced = tool_loader.get_advanced_tools(TOOLS_PATH)
        assert len(advanced) > 0
        assert "WebFetch" in advanced
        assert "WebSearch" in advanced

    def test_get_simple_tools_nonempty(self):
        simple = tool_loader.get_simple_tools(TOOLS_PATH)
        assert "Read" in simple
        assert "Write" in simple
        assert "WebFetch" not in simple

    def test_get_tier_simple(self):
        assert tool_loader.get_tier("Read", TOOLS_PATH) == "simple"

    def test_get_tier_advanced(self):
        assert tool_loader.get_tier("WebFetch", TOOLS_PATH) == "advanced"

    def test_get_tier_unknown_raises(self):
        with pytest.raises(KeyError):
            tool_loader.get_tier("NonExistentTool", TOOLS_PATH)

    def test_denied_tools_none_approved(self, memory_none):
        denied = tool_loader.get_denied_tools(TOOLS_PATH, memory_none)
        advanced = tool_loader.get_advanced_tools(TOOLS_PATH)
        assert set(denied) == set(advanced)

    def test_denied_tools_webfetch_approved(self, memory_webfetch):
        denied = tool_loader.get_denied_tools(TOOLS_PATH, memory_webfetch)
        assert "WebFetch" not in denied
        assert "WebSearch" in denied

    def test_denied_tools_all_approved(self, memory_all_advanced):
        denied = tool_loader.get_denied_tools(TOOLS_PATH, memory_all_advanced)
        assert denied == []

    def test_approved_advanced_none(self, memory_none):
        approved = tool_loader.get_approved_advanced_tools(TOOLS_PATH, memory_none)
        assert approved == []

    def test_approved_advanced_webfetch(self, memory_webfetch):
        approved = tool_loader.get_approved_advanced_tools(TOOLS_PATH, memory_webfetch)
        assert "WebFetch" in approved
        assert "WebSearch" not in approved


# ---------------------------------------------------------------------------
# settings_manager tests
# ---------------------------------------------------------------------------

class TestReadWriteSettings:
    def test_read_nonexistent_returns_empty(self, dot_claude):
        assert settings_manager.read_settings(dot_claude) == {}

    def test_write_then_read_roundtrip(self, dot_claude):
        data = {"permissions": {"deny": ["WebFetch"], "allow": []}}
        settings_manager.write_settings(dot_claude, data)
        assert settings_manager.read_settings(dot_claude) == data

    def test_write_creates_file(self, dot_claude):
        settings_manager.write_settings(dot_claude, {"foo": "bar"})
        assert (dot_claude / "settings.json").exists()


class TestApplyDenyList:
    def test_adds_tools_to_deny(self, dot_claude):
        settings_manager.apply_deny_list(dot_claude, ["WebFetch", "WebSearch"])
        s = settings_manager.read_settings(dot_claude)
        assert "WebFetch" in s["permissions"]["deny"]
        assert "WebSearch" in s["permissions"]["deny"]

    def test_merges_with_existing_deny(self, dot_claude):
        settings_manager.write_settings(dot_claude, {"permissions": {"deny": ["ExistingTool"]}})
        settings_manager.apply_deny_list(dot_claude, ["WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        assert "ExistingTool" in s["permissions"]["deny"]
        assert "WebFetch" in s["permissions"]["deny"]

    def test_deny_list_is_sorted(self, dot_claude):
        settings_manager.apply_deny_list(dot_claude, ["WebSearch", "WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        deny = s["permissions"]["deny"]
        assert deny == sorted(deny)

    def test_no_duplicates(self, dot_claude):
        settings_manager.apply_deny_list(dot_claude, ["WebFetch"])
        settings_manager.apply_deny_list(dot_claude, ["WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        assert s["permissions"]["deny"].count("WebFetch") == 1


class TestApplyAllowList:
    def test_adds_tools_to_allow(self, dot_claude):
        settings_manager.apply_allow_list(dot_claude, ["WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        assert "WebFetch" in s["permissions"]["allow"]

    def test_merges_with_existing_allow(self, dot_claude):
        settings_manager.write_settings(dot_claude, {"permissions": {"allow": ["Read"]}})
        settings_manager.apply_allow_list(dot_claude, ["WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        assert "Read" in s["permissions"]["allow"]
        assert "WebFetch" in s["permissions"]["allow"]


class TestRemoveFromDeny:
    def test_removes_tool(self, dot_claude):
        settings_manager.write_settings(
            dot_claude, {"permissions": {"deny": ["WebFetch", "WebSearch"]}}
        )
        settings_manager.remove_from_deny(dot_claude, ["WebFetch"])
        s = settings_manager.read_settings(dot_claude)
        assert "WebFetch" not in s["permissions"]["deny"]
        assert "WebSearch" in s["permissions"]["deny"]

    def test_remove_nonexistent_is_safe(self, dot_claude):
        settings_manager.write_settings(dot_claude, {"permissions": {"deny": ["WebSearch"]}})
        settings_manager.remove_from_deny(dot_claude, ["NonExistent"])
        s = settings_manager.read_settings(dot_claude)
        assert s["permissions"]["deny"] == ["WebSearch"]


class TestSync:
    def test_sync_none_approved(self, dot_claude, memory_none):
        result = settings_manager.sync(dot_claude, TOOLS_PATH, memory_none)
        s = settings_manager.read_settings(dot_claude)
        advanced = set(tool_loader.get_advanced_tools(TOOLS_PATH))
        assert set(s["permissions"]["deny"]) == advanced
        assert result["denied"] == sorted(advanced)
        assert result["allowed"] == []

    def test_sync_webfetch_approved(self, dot_claude, memory_webfetch):
        result = settings_manager.sync(dot_claude, TOOLS_PATH, memory_webfetch)
        s = settings_manager.read_settings(dot_claude)
        assert "WebFetch" not in s["permissions"]["deny"]
        assert "WebFetch" in s["permissions"]["allow"]
        assert "WebSearch" in s["permissions"]["deny"]
        assert "WebFetch" in result["allowed"]
        assert "WebFetch" not in result["denied"]

    def test_sync_all_approved(self, dot_claude, memory_all_advanced):
        result = settings_manager.sync(dot_claude, TOOLS_PATH, memory_all_advanced)
        s = settings_manager.read_settings(dot_claude)
        advanced = set(tool_loader.get_advanced_tools(TOOLS_PATH))
        assert set(s["permissions"]["deny"]) == set()
        assert set(s["permissions"]["allow"]) == advanced
        assert result["denied"] == []

    def test_sync_preserves_non_managed_entries(self, dot_claude, memory_none):
        """Custom deny/allow entries not in tools.json should be preserved."""
        settings_manager.write_settings(
            dot_claude,
            {"permissions": {"deny": ["mcp__custom__tool"], "allow": ["SomeOtherTool"]}},
        )
        settings_manager.sync(dot_claude, TOOLS_PATH, memory_none)
        s = settings_manager.read_settings(dot_claude)
        assert "mcp__custom__tool" in s["permissions"]["deny"]
        assert "SomeOtherTool" in s["permissions"]["allow"]

    def test_sync_idempotent(self, dot_claude, memory_webfetch):
        """Running sync twice produces the same result."""
        settings_manager.sync(dot_claude, TOOLS_PATH, memory_webfetch)
        result1 = settings_manager.read_settings(dot_claude)
        settings_manager.sync(dot_claude, TOOLS_PATH, memory_webfetch)
        result2 = settings_manager.read_settings(dot_claude)
        assert result1 == result2
