"""Backward-compatible shim for ``agent_api.exceptions``.

New code should import from ``limen.exceptions``.
"""

from limen.exceptions import *  # noqa: F403
