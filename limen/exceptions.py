"""Backward-compatible shim for ``limen.exceptions``.

New code should import from ``waygate_ai.exceptions``.
"""

from waygate_ai.exceptions import *  # noqa: F403
