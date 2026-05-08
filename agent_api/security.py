"""Backward-compatible shim for ``agent_api.security``.

New code should import from ``limen.security``.
"""

from limen.security import *  # noqa: F403
