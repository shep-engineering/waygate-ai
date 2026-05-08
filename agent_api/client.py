"""Backward-compatible shim for ``agent_api.client``.

New code should import from ``limen.client``.
"""

from limen.client import *  # noqa: F403
