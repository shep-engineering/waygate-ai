"""Backward-compatible shim for ``agent_api.config``.

New code should import from ``limen.config``.
"""

from limen.config import *  # noqa: F403
