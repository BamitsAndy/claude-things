"""Main Claude API conversation loop with lazy tool loading and permission gating."""

import anthropic
from pathlib import Path

from core.tool_loader import load_tools
from core.permission_hook import ask_permission
from core.executor import execute_tool

SYSTEM_PROMPT = (Path(__file__).parent.parent / "config" / "claude.md").read_text(encoding="utf-8")

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"


def run(persist: bool = True) -> None:
    messages: list[dict] = []
    session_approved: set[str] = set()

    print("Context Manager Chat — type 'quit' to exit\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Inner loop: handle tool_use turns until Claude returns end_turn
        while True:
            tools = load_tools(session_approved)
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                # Find the tool_use block
                tool_block = next(
                    (b for b in response.content if b.type == "tool_use"), None
                )
                if tool_block is None:
                    # Malformed response; treat as end_turn
                    _print_text_blocks(response.content)
                    messages.append({"role": "assistant", "content": response.content})
                    break

                tool_name = tool_block.name
                args = tool_block.input or {}

                # Always ask — baseline tools get auto-approved (they're always loaded)
                # Advanced tools need explicit approval unless already in session/persistent set
                already_approved = tool_name in session_approved or _is_baseline(tool_name, tools)
                if already_approved:
                    approved = True
                else:
                    approved = ask_permission(tool_name, args, persist=persist)

                messages.append({"role": "assistant", "content": response.content})

                if approved:
                    session_approved.add(tool_name)
                    result = execute_tool(tool_name, args)
                else:
                    result = "Permission denied by user."

                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result,
                    }],
                })

            else:
                # end_turn or other — print text and move to next user turn
                _print_text_blocks(response.content)
                messages.append({"role": "assistant", "content": response.content})
                break


def _is_baseline(tool_name: str, loaded_tools: list[dict]) -> bool:
    """Return True if the tool is in the always-loaded baseline set."""
    from core.tool_loader import _all_tools
    simple_names = {t["name"] for t in _all_tools() if t["tier"] == "simple"}
    return tool_name in simple_names


def _print_text_blocks(content) -> None:
    for block in content:
        if hasattr(block, "text") and block.text:
            print(f"\nClaude: {block.text}")
