"""Backward-compatible shim for ``agent_api.exceptions``.

New code should import from ``waygate_ai.exceptions``.
"""

from waygate_ai.exceptions import *  # noqa: F403
