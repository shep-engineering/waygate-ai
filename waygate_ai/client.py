"""Unified LLM client with retry, cost logging, and prompt injection guard."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

from waygate_ai.config import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    detect_backend,
    estimate_cost,
)
from waygate_ai.exceptions import ConfigError, RateLimitError, TransientError
from waygate_ai.security import DEFAULT_CANARY, apply_canary, check_response

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from any LLM provider.

    Args:
        text: Scrubbed response text returned to the caller.
        provider: Backend that handled the call.
        model: Effective model used for the call.
        tokens_in: Provider-reported input tokens, or 0 when unavailable.
        tokens_out: Provider-reported output tokens, or 0 when unavailable.
        cost_usd: Estimated call cost for known models.
        latency_ms: Provider call latency in milliseconds.
        attempts: Attempt number that produced the response.

    Returns:
        Dataclass instance populated by ``LLMClient.call()``.

    Raises:
        None.
    """
    text: str
    provider: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    attempts: int = 1


class LLMClient:
    """Unified LLM client.

    Auto-detects backend from environment variables. All calls go through
    this class — no direct provider SDK calls in application code.

    Args:
        api_key:        Override for the provider API key. Falls back to env.
        model:          Default model for all calls. Can be overridden per call.
        max_tokens:     Maximum tokens for completions.
        max_retries:    Retry attempts on RateLimitError or TransientError.
        system_canary:  Prompt injection guard appended to every system prompt.
                        Pass ``None`` to disable (not recommended in production).
        scrub_output:   Whether to scrub leaked instruction text from responses.

    Returns:
        Configured client instance.

    Raises:
        None.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        system_canary: str | None = DEFAULT_CANARY,
        scrub_output: bool = True,
    ) -> None:
        self._backend, detected_model = detect_backend()
        self._api_key = api_key
        self._model = model or detected_model
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self._canary = system_canary
        self._scrub_output = scrub_output
        self._ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def call(
        self,
        system: str,
        user: str,
        model: str | None = None,
    ) -> LLMResponse:
        """Call the configured LLM provider and return a structured response.

        Args:
            system: System prompt.
            user:   User message.
            model:  Per-call model override. Falls back to instance default.

        Raises:
            ConfigError:    No LLM backend is configured.
            AuthError:      Provider rejected the API key.
            RateLimitError: All retry attempts were rate-limited.
            TransientError: All retry attempts hit transient failures.
            WaygateError:  Base class for mapped provider failures.
        """
        if self._backend == "none":
            raise ConfigError(
                "No LLM backend configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, "
                "or OLLAMA_MODEL environment variable."
            )

        effective_model = model or self._model
        guarded_system = apply_canary(system, self._canary)

        return self._call_with_retry(guarded_system, user, effective_model)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _call_with_retry(self, system: str, user: str, model: str) -> LLMResponse:
        last_exc: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                t0 = time.monotonic()
                text, tokens_in, tokens_out = self._dispatch(system, user, model)
                latency_ms = (time.monotonic() - t0) * 1000

                if self._scrub_output:
                    text = check_response(text)
                cost = estimate_cost(model, tokens_in, tokens_out)
                response = LLMResponse(
                    text=text,
                    provider=self._backend,
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                    attempts=attempt,
                )
                self._log(response)
                return response

            except (RateLimitError, TransientError) as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    break
                wait = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.warning(
                    "LLM call failed (attempt %d/%d, %s). Retrying in %ds.",
                    attempt, self._max_retries, type(exc).__name__, wait,
                )
                time.sleep(wait)

        raise last_exc  # type: ignore[misc]

    def _dispatch(self, system: str, user: str, model: str) -> tuple[str, int, int]:
        """Route to the correct provider module.

        Args:
            system: Guarded system prompt.
            user: User message.
            model: Effective model name.

        Returns:
            Tuple of response text, input tokens, and output tokens.

        Raises:
            ConfigError: Backend name is unknown.
            AuthError: Provider rejected credentials.
            RateLimitError: Provider returned a rate-limit response.
            TransientError: Provider returned a transient failure.
            ImportError: Selected provider package is not installed.
        """
        if self._backend == "anthropic":
            from waygate_ai.providers import anthropic as _anthropic
            key = self._api_key or os.environ.get("ANTHROPIC_API_KEY", "")
            return _anthropic.call(system, user, model, key, self._max_tokens)

        if self._backend == "openai":
            from waygate_ai.providers import openai as _openai
            key = self._api_key or os.environ.get("OPENAI_API_KEY", "")
            return _openai.call(system, user, model, key, self._max_tokens)

        if self._backend == "ollama":
            from waygate_ai.providers import ollama as _ollama
            ollama_model = os.environ.get("OLLAMA_MODEL", model)
            return _ollama.call(system, user, ollama_model, self._ollama_base, self._max_tokens)

        raise ConfigError(f"Unknown backend: {self._backend!r}")

    @staticmethod
    def _log(response: LLMResponse) -> None:
        logger.info(
            "llm_call provider=%s model=%s tokens_in=%d tokens_out=%d "
            "cost_usd=%.6f latency_ms=%.1f attempts=%d",
            response.provider,
            response.model,
            response.tokens_in,
            response.tokens_out,
            response.cost_usd,
            response.latency_ms,
            response.attempts,
        )
