"""Backward-compatible import shim for the previous ``limen`` package name.

New code should import from ``waygate_ai``.
"""

from waygate_ai import *  # noqa: F403
from waygate_ai import __all__  # noqa: F401
