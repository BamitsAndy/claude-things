"""Tool executor — maps tool names to actual Python implementations."""

import glob as _glob
import json
import re
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Simple (baseline) tools
# ---------------------------------------------------------------------------

def _read(file_path: str, offset: int = 0, limit: int = 0) -> str:
    path = Path(file_path)
    if not path.exists():
        return f"Error: file not found: {file_path}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(0, offset - 1) if offset else 0
    end = start + limit if limit else len(lines)
    numbered = [f"{i+start+1}\t{l}" for i, l in enumerate(lines[start:end])]
    return "\n".join(numbered)


def _write(file_path: str, content: str) -> str:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {file_path}"


def _glob_tool(pattern: str, path: str = ".") -> str:
    base = Path(path)
    matches = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        return "No files matched."
    return "\n".join(str(m) for m in matches)


def _ask_user_question(question: str, options: list[str] | None = None) -> str:
    print(f"\n{question}")
    if options:
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
    try:
        answer = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    return answer


# ---------------------------------------------------------------------------
# Advanced tools
# ---------------------------------------------------------------------------

def _bash(command: str, timeout: int = 30000, **_) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout / 1000,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out"
    except Exception as exc:
        return f"Error: {exc}"


def _edit(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    path = Path(file_path)
    if not path.exists():
        return f"Error: file not found: {file_path}"
    text = path.read_text(encoding="utf-8", errors="replace")
    if old_string not in text:
        return f"Error: old_string not found in {file_path}"
    if replace_all:
        new_text = text.replace(old_string, new_string)
    else:
        new_text = text.replace(old_string, new_string, 1)
    path.write_text(new_text, encoding="utf-8")
    count = text.count(old_string) if replace_all else 1
    return f"Replaced {count} occurrence(s) in {file_path}"


def _grep(
    pattern: str,
    path: str = ".",
    glob: str | None = None,
    output_mode: str = "files_with_matches",
    case_insensitive: bool = False,
    context: int = 0,
) -> str:
    flags = re.IGNORECASE if case_insensitive else 0
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        return f"Error: invalid pattern: {exc}"

    search_path = Path(path)
    files: list[Path] = []
    if search_path.is_file():
        files = [search_path]
    else:
        file_glob = glob or "**/*"
        files = [p for p in search_path.glob(file_glob) if p.is_file()]

    results: list[str] = []
    for fp in sorted(files):
        try:
            lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        matched_indices = [i for i, l in enumerate(lines) if compiled.search(l)]
        if not matched_indices:
            continue

        if output_mode == "files_with_matches":
            results.append(str(fp))
        elif output_mode == "count":
            results.append(f"{fp}: {len(matched_indices)}")
        else:  # content
            shown: set[int] = set()
            for idx in matched_indices:
                start = max(0, idx - context)
                end = min(len(lines) - 1, idx + context)
                for i in range(start, end + 1):
                    if i not in shown:
                        prefix = ">" if i == idx else " "
                        results.append(f"{fp}:{i+1}{prefix} {lines[i]}")
                        shown.add(i)

    return "\n".join(results) if results else "No matches."


# ---------------------------------------------------------------------------
# Task management (file-backed, minimal)
# ---------------------------------------------------------------------------

_TASKS_PATH = Path(__file__).parent.parent / "config" / "tasks.json"


def _load_tasks() -> dict:
    try:
        return json.loads(_TASKS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"next_id": 1, "tasks": {}}


def _save_tasks(data: dict) -> None:
    _TASKS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _task_create(subject: str, description: str, activeForm: str = "") -> str:
    data = _load_tasks()
    tid = str(data["next_id"])
    data["next_id"] += 1
    data["tasks"][tid] = {
        "id": tid,
        "subject": subject,
        "description": description,
        "activeForm": activeForm,
        "status": "pending",
        "owner": "",
    }
    _save_tasks(data)
    return f"Task #{tid} created: {subject}"


def _task_get(taskId: str) -> str:
    data = _load_tasks()
    task = data["tasks"].get(taskId)
    if not task:
        return f"Error: task {taskId} not found"
    return json.dumps(task, indent=2)


def _task_list() -> str:
    data = _load_tasks()
    if not data["tasks"]:
        return "No tasks."
    lines = []
    for tid, t in sorted(data["tasks"].items(), key=lambda x: int(x[0])):
        if t["status"] != "deleted":
            lines.append(f"#{tid} [{t['status']}] {t['subject']}")
    return "\n".join(lines) if lines else "No active tasks."


def _task_update(taskId: str, **kwargs) -> str:
    data = _load_tasks()
    task = data["tasks"].get(taskId)
    if not task:
        return f"Error: task {taskId} not found"
    for k, v in kwargs.items():
        if k in task and v is not None:
            task[k] = v
    _save_tasks(data)
    return f"Task #{taskId} updated."


def _task_stop(task_id: str) -> str:
    return _task_update(task_id, status="deleted")


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_DISPATCH: dict[str, callable] = {
    "Read": _read,
    "Write": _write,
    "Glob": _glob_tool,
    "AskUserQuestion": _ask_user_question,
    "Bash": _bash,
    "Edit": _edit,
    "Grep": _grep,
    "TaskCreate": _task_create,
    "TaskGet": _task_get,
    "TaskList": _task_list,
    "TaskUpdate": _task_update,
    "TaskStop": _task_stop,
}


def execute_tool(tool_name: str, args: dict) -> str:
    fn = _DISPATCH.get(tool_name)
    if fn is None:
        return f"Error: unknown tool '{tool_name}'"
    try:
        return fn(**args)
    except TypeError as exc:
        return f"Error calling {tool_name}: {exc}"
    except Exception as exc:
        return f"Error: {exc}"
