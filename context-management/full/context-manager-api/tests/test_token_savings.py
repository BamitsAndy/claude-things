"""Phase 7 — Measure token savings from lazy tool loading.

Run from the context-manager-api/ directory:
    python -m tests.test_token_savings

Token counting uses the Anthropic API if ANTHROPIC_API_KEY is set and the
account has credits; otherwise falls back to a local tiktoken estimate.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tool_loader import load_tools, _all_tools


# ---------------------------------------------------------------------------
# Token counting — API preferred, tiktoken fallback, char-heuristic last resort
# ---------------------------------------------------------------------------

def _count_via_api(tools: list[dict]) -> int | None:
    """Try the Anthropic token-counting beta endpoint. Returns None on any failure."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.beta.messages.count_tokens(
            model="claude-haiku-4-5-20251001",
            tools=tools,
            messages=[{"role": "user", "content": "hello"}],
            system="test",
            betas=["token-counting-2024-11-01"],
        )
        return resp.input_tokens
    except Exception:
        return None


def _count_via_tiktoken(tools: list[dict]) -> int | None:
    """Estimate using tiktoken (cl100k_base ≈ Claude tokeniser)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        text = json.dumps(tools)
        return len(enc.encode(text))
    except Exception:
        return None


def _count_via_chars(tools: list[dict]) -> int:
    """Rough fallback: ~4 chars per token."""
    return len(json.dumps(tools)) // 4


def count_tool_tokens(tools: list[dict]) -> tuple[int, str]:
    """Return (token_count, method_used)."""
    n = _count_via_api(tools)
    if n is not None:
        return n, "API"
    n = _count_via_tiktoken(tools)
    if n is not None:
        return n, "tiktoken"
    return _count_via_chars(tools), "char-heuristic"


def main() -> None:
    baseline_tools = load_tools(session_approved=set())

    all_tools = _all_tools()
    for t in all_tools:
        t.pop("tier", None)

    print("Counting tokens...")
    baseline_tokens, method = count_tool_tokens(baseline_tools)
    full_tokens, _ = count_tool_tokens(all_tools)

    saved = full_tokens - baseline_tokens
    pct = 100 * saved / full_tokens if full_tokens else 0

    print(f"  method          : {method}")
    print()
    print(f"  Baseline tools  : {baseline_tokens:>6,} tokens  ({len(baseline_tools)} tools)")
    print(f"  Full tools      : {full_tokens:>6,} tokens  ({len(all_tools)} tools)")
    print(f"  Saved           : {saved:>6,} tokens  ({pct:.0f}% reduction per turn)")


if __name__ == "__main__":
    main()
