"""Exception hierarchy for Limen.

All provider errors are mapped to these types so the client retry logic
and callers never need to import provider-specific SDK exceptions.
"""


class LimenError(Exception):
    """Base class for all Limen errors."""


# Backward-compatible alias for pre-rename internal consumers.
AgentAPIError = LimenError


class RateLimitError(LimenError):
    """Provider returned 429 / rate limit exceeded. Retryable."""


class TransientError(LimenError):
    """Provider returned a 5xx or network error. Retryable."""


class AuthError(LimenError):
    """Provider returned 401 / 403. Not retryable."""


class ConfigError(LimenError):
    """No LLM backend is configured. Check environment variables."""
