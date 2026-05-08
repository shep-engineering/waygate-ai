"""Ollama provider — uses the OpenAI-compatible /v1/chat/completions endpoint.

No third-party dependencies; uses stdlib urllib only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from limen.exceptions import TransientError


def call(
    system: str,
    user: str,
    model: str,
    base_url: str,
    max_tokens: int,
) -> tuple[str, int, int]:
    """Call a local Ollama instance and return ``(text, tokens_in, tokens_out)``.

    Token counts may be 0 if the model does not report them.

    Args:
        system: System prompt sent in the chat completion request.
        user: User message content.
        model: Ollama model name.
        base_url: Ollama base URL.
        max_tokens: Completion token cap.

    Returns:
        Tuple of response text, input tokens, and output tokens.

    Raises:
        TransientError: Ollama not reachable or returned a non-200 response.
    """
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise TransientError(
            f"Ollama not reachable at {base_url}. Is Ollama running? Run: ollama serve"
        ) from exc

    text = body["choices"][0]["message"]["content"].strip()
    usage = body.get("usage", {})
    tokens_in = usage.get("prompt_tokens", 0)
    tokens_out = usage.get("completion_tokens", 0)
    return text, tokens_in, tokens_out
