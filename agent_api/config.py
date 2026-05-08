"""Backward-compatible shim for ``agent_api.config``.

New code should import from ``waygate_ai.config``.
"""

from waygate_ai.config import *  # noqa: F403
