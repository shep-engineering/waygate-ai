"""Backend detection and shared configuration.

All values are env-overridable so deployments can pin specific model
snapshots without code changes.
"""

from __future__ import annotations

import logging
import os
import re

from waygate_ai.router import estimate_cost as _estimate_cost

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults (all overridable via env)
# ---------------------------------------------------------------------------

DEFAULT_ANTHROPIC_MODEL: str = os.getenv("LLM_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
DEFAULT_OPENAI_MODEL: str = os.getenv("LLM_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
DEFAULT_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "8192"))
DEFAULT_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

# ---------------------------------------------------------------------------
# Key validation
# ---------------------------------------------------------------------------

_ANTHROPIC_KEY_RE = re.compile(r"^sk-ant-api03-[A-Za-z0-9_\-]{80,}$")


def is_valid_anthropic_key(key: str) -> bool:
    """Return True if *key* looks like a real Anthropic API key.

    Placeholder strings such as ``sk-ant-api03-...`` from ``.env.example``
    do not match and are treated as unset.

    Args:
        key: Candidate Anthropic API key.

    Returns:
        ``True`` when the key matches the expected shape, otherwise ``False``.

    Raises:
        AttributeError: If *key* is not a string-like object with ``strip()``.
    """
    return bool(_ANTHROPIC_KEY_RE.match(key.strip()))


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

def detect_backend() -> tuple[str, str]:
    """Return ``(backend, model)`` based on environment variables.

    Priority:
      1. ``ANTHROPIC_API_KEY`` valid + not ``FORCE_OLLAMA`` → ``('anthropic', model)``
      2. ``OPENAI_API_KEY`` set + not ``FORCE_OLLAMA``       → ``('openai', model)``
      3. ``OLLAMA_MODEL`` set                                → ``('ollama', model)``
      4. Nothing configured                                  → ``('none', '')``

    Set ``FORCE_OLLAMA=1`` to use Ollama even when a cloud key is present.
    An Anthropic key that does not match the expected format is treated as
    unset and a warning is logged.

    Args:
        None.

    Returns:
        Tuple containing backend name and selected model. Backend is one of
        ``"anthropic"``, ``"openai"``, ``"ollama"``, or ``"none"``.

    Raises:
        None.
    """
    force_ollama = os.environ.get("FORCE_OLLAMA", "").strip() == "1"

    raw_anthropic = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    has_valid_anthropic = bool(raw_anthropic) and is_valid_anthropic_key(raw_anthropic)
    if raw_anthropic and not has_valid_anthropic:
        logger.warning(
            "ANTHROPIC_API_KEY is set but does not match the expected format "
            "(sk-ant-api03-<80+ chars>); treating as unset."
        )

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    ollama_model = os.environ.get("OLLAMA_MODEL", "").strip()

    if has_valid_anthropic and not force_ollama:
        return "anthropic", DEFAULT_ANTHROPIC_MODEL
    if openai_key and not force_ollama:
        return "openai", DEFAULT_OPENAI_MODEL
    if ollama_model:
        return "ollama", ollama_model
    return "none", ""


# ---------------------------------------------------------------------------
# Cost estimation
#
# Prices live in ``waygate_ai.router`` alongside the routing table, so the
# model a tier resolves to and the price it bills at can never drift apart.
# This re-export keeps ``from waygate_ai.config import estimate_cost``
# working for existing callers.
# ---------------------------------------------------------------------------

estimate_cost = _estimate_cost
