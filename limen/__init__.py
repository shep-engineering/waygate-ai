"""limen — unified LLM client for Anthropic, OpenAI, and Ollama."""

from limen.client import LLMClient, LLMResponse
from limen.config import detect_backend
from limen.exceptions import (
    AgentAPIError,
    AuthError,
    ConfigError,
    LimenError,
    RateLimitError,
    TransientError,
)
from limen.security import (
    apply_canary,
    check_response,
    is_safe,
    sanitize,
    wrap,
)

__all__ = [
    "LLMClient",
    "LLMResponse",
    "detect_backend",
    "AgentAPIError",
    "LimenError",
    "AuthError",
    "ConfigError",
    "RateLimitError",
    "TransientError",
    "sanitize",
    "wrap",
    "check_response",
    "is_safe",
    "apply_canary",
]
