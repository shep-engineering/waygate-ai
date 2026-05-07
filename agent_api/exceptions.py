"""Exception hierarchy for agent-api.

All provider errors are mapped to these types so the client retry logic
and callers never need to import provider-specific SDK exceptions.
"""


class AgentAPIError(Exception):
    """Base class for all agent-api errors."""


class RateLimitError(AgentAPIError):
    """Provider returned 429 / rate limit exceeded. Retryable."""


class TransientError(AgentAPIError):
    """Provider returned a 5xx or network error. Retryable."""


class AuthError(AgentAPIError):
    """Provider returned 401 / 403. Not retryable."""


class ConfigError(AgentAPIError):
    """No LLM backend is configured. Check environment variables."""
