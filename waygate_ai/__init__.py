"""waygate_ai — guarded, cost-aware LLM gateway for Anthropic, OpenAI, and Ollama."""

from waygate_ai.client import LLMClient, LLMResponse, Session
from waygate_ai.config import detect_backend
from waygate_ai.exceptions import (
    AuthError,
    ConfigError,
    RateLimitError,
    TransientError,
    WaygateError,
)
from waygate_ai.router import (
    MODEL_REGISTRY,
    TIERS,
    ModelSpec,
    Tier,
    estimate_cost,
    resolve,
    spec_for,
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
    "Session",
    "detect_backend",
    "WaygateError",
    "AuthError",
    "ConfigError",
    "RateLimitError",
    "TransientError",
    "MODEL_REGISTRY",
    "TIERS",
    "ModelSpec",
    "Tier",
    "estimate_cost",
    "resolve",
    "spec_for",
    "sanitize",
    "wrap",
    "check_response",
    "is_safe",
    "apply_canary",
]
