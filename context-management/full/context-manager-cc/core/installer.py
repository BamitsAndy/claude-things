"""
First-time setup for a target project: creates directories, copies config,
patches settings.json, and appends CLAUDE.md catalogue block.
"""
import json
import shutil
from pathlib import Path

from core import tool_loader, settings_manager

# Sentinel comment that guards against double-appending the CLAUDE.md block
_CLAUDE_MD_GUARD = "<!-- context-manager-cc: begin -->"


def _resolve_paths(target: str | Path, global_mode: bool) -> tuple[Path, Path]:
    """
    Return (target_project_root, dot_claude_dir).
    In global mode, dot_claude_dir is ~/.claude/.
    """
    if global_mode:
        dot_claude = Path.home() / ".claude"
        project_root = dot_claude  # CLAUDE.md lives at ~/.claude/CLAUDE.md
    else:
        project_root = Path(target).resolve()
        dot_claude = project_root / ".claude"
    return project_root, dot_claude


def _cm_data_dir(dot_claude: Path) -> Path:
    return dot_claude / "context-manager-cc"


def _init_memory(cm_data_dir: Path, template_memory_path: Path) -> Path:
    """Create memory.json from template if it doesn't exist yet."""
    cm_data_dir.mkdir(parents=True, exist_ok=True)
    dest = cm_data_dir / "memory.json"
    if not dest.exists():
        shutil.copy2(template_memory_path, dest)
    return dest


def _copy_tools(cm_data_dir: Path, template_tools_path: Path) -> Path:
    """Always overwrite tools.json so upgrades propagate."""
    cm_data_dir.mkdir(parents=True, exist_ok=True)
    dest = cm_data_dir / "tools.json"
    shutil.copy2(template_tools_path, dest)
    return dest


def _build_denied_list_text(denied_tools: list[str]) -> str:
    if not denied_tools:
        return "(none — all tools are currently approved)"
    return ", ".join(denied_tools)


def _append_claude_md(project_root: Path, claude_md_template: Path, denied_tools: list[str]) -> None:
    """
    Append the CLAUDE.md catalogue block to <project_root>/CLAUDE.md.
    Idempotent: skips if guard comment is already present.
    """
    target_claude_md = project_root / "CLAUDE.md"

    # Read template
    template_text = claude_md_template.read_text(encoding="utf-8")

    # Replace placeholder with actual denied tools
    denied_text = _build_denied_list_text(denied_tools)
    block = template_text.replace("<!-- DENIED_TOOLS_PLACEHOLDER -->", denied_text)

    # Check if already installed
    if target_claude_md.exists():
        existing = target_claude_md.read_text(encoding="utf-8")
        if _CLAUDE_MD_GUARD in existing:
            # Already present — update the denied tools section only
            _update_claude_md_denied_section(target_claude_md, denied_text)
            return
        # Append with a blank line separator
        content = existing.rstrip("\n") + "\n\n" + block
    else:
        content = block

    target_claude_md.write_text(content, encoding="utf-8")


def _update_claude_md_denied_section(target: Path, denied_text: str) -> None:
    """
    Replace the line after '### Requires approval' in an existing CLAUDE.md block.
    This keeps the block up-to-date after --sync runs.
    """
    text = target.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip() == "### Requires approval (currently not in context)":
            # Replace the very next non-empty line
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                out.append(lines[i])
                i += 1
            if i < len(lines):
                out.append(denied_text + "\n")
                i += 1  # skip old line
            continue
        i += 1
    target.write_text("".join(out), encoding="utf-8")


def install(
    target: str | Path,
    global_mode: bool,
    config_dir: str | Path,
) -> dict:
    """
    First-time install into *target* project (or global ~/.claude/).

    config_dir should point to the context-manager-cc/config/ directory.

    Returns a summary dict with paths and what was written.
    """
    config_dir = Path(config_dir)
    template_tools = config_dir / "tools.json"
    template_memory = config_dir / "memory.json"
    template_claude_md = config_dir / "CLAUDE.md"

    project_root, dot_claude = _resolve_paths(target, global_mode)
    cm_data = _cm_data_dir(dot_claude)

    # 1. Create data dir + copy/init files
    tools_path = _copy_tools(cm_data, template_tools)
    memory_path = _init_memory(cm_data, template_memory)

    # 2. Sync settings.json (writes deny list)
    result = settings_manager.sync(dot_claude, tools_path, memory_path)

    # 3. Append/update CLAUDE.md
    _append_claude_md(project_root, template_claude_md, result["denied"])

    return {
        "project_root": str(project_root),
        "dot_claude": str(dot_claude),
        "tools_path": str(tools_path),
        "memory_path": str(memory_path),
        "denied": result["denied"],
        "allowed": result["allowed"],
    }


def sync_only(
    target: str | Path,
    global_mode: bool,
    config_dir: str | Path,
) -> dict:
    """
    Re-read memory.json and regenerate settings.json + update CLAUDE.md denied list.
    Does NOT re-copy tools.json (preserves any local overrides).
    """
    config_dir = Path(config_dir)
    project_root, dot_claude = _resolve_paths(target, global_mode)
    cm_data = _cm_data_dir(dot_claude)

    tools_path = cm_data / "tools.json"
    memory_path = cm_data / "memory.json"

    if not tools_path.exists():
        raise FileNotFoundError(
            f"tools.json not found at {tools_path}. Run install first."
        )
    if not memory_path.exists():
        raise FileNotFoundError(
            f"memory.json not found at {memory_path}. Run install first."
        )

    result = settings_manager.sync(dot_claude, tools_path, memory_path)

    # Update the CLAUDE.md denied section
    template_claude_md = config_dir / "CLAUDE.md"
    _append_claude_md(project_root, template_claude_md, result["denied"])

    return {
        "project_root": str(project_root),
        "dot_claude": str(dot_claude),
        "denied": result["denied"],
        "allowed": result["allowed"],
    }
