"""agent-api — unified LLM client for Anthropic, OpenAI, and Ollama."""

from agent_api.client import LLMClient, LLMResponse
from agent_api.config import detect_backend
from agent_api.exceptions import (
    AgentAPIError,
    AuthError,
    ConfigError,
    RateLimitError,
    TransientError,
)

__all__ = [
    "LLMClient",
    "LLMResponse",
    "detect_backend",
    "AgentAPIError",
    "AuthError",
    "ConfigError",
    "RateLimitError",
    "TransientError",
]
