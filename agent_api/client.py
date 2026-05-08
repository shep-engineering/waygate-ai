"""Backward-compatible shim for ``agent_api.client``.

New code should import from ``waygate_ai.client``.
"""

from waygate_ai.client import *  # noqa: F403
