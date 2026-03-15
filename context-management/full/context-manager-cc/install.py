"""
context-manager-cc entry point.

Usage:
  python install.py [--target /path/to/project] [--global]
  python install.py --sync [--target /path/to/project] [--global]
"""
import argparse
import sys
from pathlib import Path

# Ensure the package root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from core import installer

CONFIG_DIR = Path(__file__).parent / "config"


def _print_result(result: dict, mode: str) -> None:
    print(f"\n[context-manager-cc] {mode} complete")
    print(f"  Project root : {result['project_root']}")
    print(f"  .claude dir  : {result['dot_claude']}")
    if result["denied"]:
        print(f"  Denied tools : {', '.join(result['denied'])}")
    else:
        print("  Denied tools : (none)")
    if result["allowed"]:
        print(f"  Allowed tools: {', '.join(result['allowed'])}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="context-manager-cc: context reduction for Claude Code"
    )
    parser.add_argument(
        "--target",
        default=".",
        metavar="PATH",
        help="Target project directory (default: current directory)",
    )
    parser.add_argument(
        "--global",
        dest="global_mode",
        action="store_true",
        help="Install to ~/.claude/ for all projects",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Re-read memory.json and regenerate settings.json without full reinstall",
    )
    args = parser.parse_args()

    if args.sync:
        result = installer.sync_only(
            target=args.target,
            global_mode=args.global_mode,
            config_dir=CONFIG_DIR,
        )
        _print_result(result, "Sync")
        print("\n  settings.json updated. Restart Claude Code to apply changes.")
    else:
        result = installer.install(
            target=args.target,
            global_mode=args.global_mode,
            config_dir=CONFIG_DIR,
        )
        _print_result(result, "Install")
        print(
            "\n  CLAUDE.md updated and settings.json written.\n"
            "  Open the project in Claude Code to start a context-managed session."
        )


if __name__ == "__main__":
    main()
