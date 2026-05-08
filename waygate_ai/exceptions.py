"""Exception hierarchy for waygate_ai.

All provider errors are mapped to these types so the client retry logic
and callers never need to import provider-specific SDK exceptions.
"""


class WaygateError(Exception):
    """Base class for all Waygate AI errors."""


class RateLimitError(WaygateError):
    """Provider returned 429 / rate limit exceeded. Retryable."""


class TransientError(WaygateError):
    """Provider returned a 5xx or network error. Retryable."""


class AuthError(WaygateError):
    """Provider returned 401 / 403. Not retryable."""


class ConfigError(WaygateError):
    """No LLM backend is configured. Check environment variables."""
