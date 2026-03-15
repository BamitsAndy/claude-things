from core.tool_loader import save_approved


def ask_permission(tool_name: str, args: dict, persist: bool = True) -> bool:
    """Prompt the user to approve a tool call.

    Returns True if approved, False if denied.

    Approval levels:
      y      — allow this one call (session only)
      always — approve permanently (written to memory.json if persist=True)
      n      — deny
    """
    print(f"\n\u26a1 Claude wants to use [{tool_name}]")
    if args:
        for k, v in list(args.items())[:3]:
            print(f"   {k}: {str(v)[:80]}")

    try:
        resp = input("Allow? (y/n/always): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    if resp == "always":
        if persist:
            save_approved(tool_name)
        return True
    return resp.startswith("y")
