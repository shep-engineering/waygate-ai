"""waygate_ai — unified LLM client for Anthropic, OpenAI, and Ollama."""

from waygate_ai.client import LLMClient, LLMResponse
from waygate_ai.config import detect_backend
from waygate_ai.exceptions import (
    AgentAPIError,
    AuthError,
    ConfigError,
    RateLimitError,
    TransientError,
    WaygateError,
)
from waygate_ai.security import (
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
    "WaygateError",
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
