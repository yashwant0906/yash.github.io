"""Shared helpers for the agentic workflow examples.

Every example calls Claude through `call()` or `call_json()` so that model
choice, refusal handling and fallbacks live in one place.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")

# Server-side fallback: if a safety classifier declines a request, the API
# re-runs it on Anthropic's recommended fallback model inside the same call.
_FALLBACK = {
    "extra_headers": {"anthropic-beta": "server-side-fallback-2026-07-01"},
    "extra_body": {"fallbacks": "default"},
}

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY (or an `ant auth login` profile)


class RefusalError(RuntimeError):
    """Raised when the model (and its fallback) declines the request."""


def create(**params: Any) -> anthropic.types.Message:
    """messages.create with fallbacks enabled and refusals surfaced as errors."""
    params.setdefault("model", MODEL)
    params.setdefault("max_tokens", 16000)
    params.setdefault("thinking", {"type": "adaptive"})
    response = client.messages.create(**params, **_FALLBACK)
    if response.stop_reason == "refusal":
        details = response.stop_details
        category = details.category if details else None
        raise RefusalError(f"Request declined (category: {category})")
    return response


def text_of(response: anthropic.types.Message) -> str:
    """Concatenate the text blocks of a response (skips thinking/tool blocks)."""
    return "".join(b.text for b in response.content if b.type == "text").strip()


def call(prompt: str, *, system: str | None = None, effort: str = "medium") -> str:
    """Single-turn call that returns plain text."""
    params: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"effort": effort},
    }
    if system:
        params["system"] = system
    return text_of(create(**params))


def call_json(
    prompt: str,
    schema: dict[str, Any],
    *,
    system: str | None = None,
    effort: str = "medium",
) -> Any:
    """Single-turn call whose output is guaranteed to match `schema`."""
    params: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {
            "effort": effort,
            "format": {"type": "json_schema", "schema": schema},
        },
    }
    if system:
        params["system"] = system
    return json.loads(text_of(create(**params)))


def banner(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}", file=sys.stderr)
