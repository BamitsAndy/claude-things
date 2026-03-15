"""Entry point for the context-manager-api chat CLI."""

import argparse
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `core.*` imports resolve
sys.path.insert(0, str(Path(__file__).parent))

from core.chat_loop import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Claude chat CLI with lazy tool loading and permission gating."
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Session-only approvals — do not write to memory.json",
    )
    args = parser.parse_args()
    run(persist=not args.no_persist)
