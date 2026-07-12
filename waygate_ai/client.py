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
from waygate_ai.router import Tier, resolve
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
        tier: Tier | None = None,
    ) -> LLMResponse:
        """Call the configured LLM provider and return a structured response.

        Pass ``tier`` to let the router pick the cheapest model on the
        active provider that can do the job -- this is the normal path,
        and it means the caller never names a model. Pass ``model`` only
        to pin an exact model id, bypassing the router.

        Args:
            system: System prompt.
            user:   User message.
            model:  Exact model id, bypassing tier routing. Falls back to
                    the instance default when neither is given.
            tier:   ``"cheap"``, ``"standard"``, or ``"premium"``. Resolved
                    against the detected backend.

        Returns:
            ``LLMResponse`` with the scrubbed text, the model that served
            the call, token counts, and estimated cost.

        Raises:
            ValueError:     Both ``model`` and ``tier`` were given, or the
                            tier is not a known tier.
            ConfigError:    No LLM backend is configured.
            AuthError:      Provider rejected the API key.
            RateLimitError: All retry attempts were rate-limited.
            TransientError: All retry attempts hit transient failures.
            WaygateError:   Base class for mapped provider failures.
        """
        guarded_system = apply_canary(system, self._canary)
        effective_model = self.resolve_model(model=model, tier=tier)

        return self._call_with_retry(guarded_system, user, effective_model)

    def resolve_model(
        self,
        model: str | None = None,
        tier: Tier | None = None,
    ) -> str:
        """Return the model id a ``(model, tier)`` pair selects.

        Tier resolution runs against ``self._backend`` -- the backend this
        client will actually dispatch to. Routing and dispatch therefore
        read the same detection result, so a tier can never resolve to a
        model from a provider other than the one that gets called.

        Args:
            model: Exact model id, bypassing tier routing.
            tier:  Tier to resolve against the active backend.

        Returns:
            A provider-native model id.

        Raises:
            ValueError:  Both ``model`` and ``tier`` were given, or the
                         tier is not a known tier.
            ConfigError: No LLM backend is configured.
        """
        if self._backend == "none":
            raise ConfigError(
                "No LLM backend configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, "
                "or OLLAMA_MODEL environment variable."
            )

        if model is not None and tier is not None:
            raise ValueError(
                "Pass model= or tier=, not both. `tier` routes to the cheapest "
                "capable model on the active provider; `model` pins an exact id."
            )

        if tier is not None:
            return resolve(tier, self._backend)

        return model or self._model

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

    def session(
        self,
        tier: Tier | None = None,
        model: str | None = None,
    ) -> Session:
        """Open a model-pinned session for a multi-turn conversation.

        Args:
            tier:  Tier to resolve once, at session start.
            model: Exact model id to pin instead of resolving a tier.

        Returns:
            A :class:`Session` bound to this client and one fixed model.

        Raises:
            ValueError:  Both ``model`` and ``tier`` were given.
            ConfigError: No LLM backend is configured.
        """
        return Session(self, self.resolve_model(model=model, tier=tier))


class Session:
    """A multi-turn conversation pinned to one model.

    WHY PIN
    -------
    Providers cache the prompt prefix, and a cache read costs roughly a
    tenth of a fresh input token. That cache is keyed to the model: switch
    models mid-conversation and the entire cached prefix is discarded and
    re-billed at full price.

    This is the trap that makes naive routing *lose* money. Route a
    long chat turn-by-turn -- cheap tier for "ok", premium for the hard
    follow-up -- and every switch dumps a cache that was about to pay for
    itself. On a conversation of any length, always-premium-and-cached can
    beat cleverly-routed-and-uncached outright.

    So the rule is: route *between* conversations, never *within* one.
    One-shot work (classify, extract, summarize) has no cache to protect
    and should route freely per call. Multi-turn chat resolves its tier
    once, here, and holds it for the life of the conversation.

    The session pins the model, not the history -- the caller still owns
    the transcript and passes it in each turn.

    Args:
        client: The client to dispatch through.
        model:  The model id fixed for every turn of this session.

    Returns:
        Session instance.

    Raises:
        None.
    """

    def __init__(self, client: LLMClient, model: str) -> None:
        self._client = client
        self._model = model

    @property
    def model(self) -> str:
        """The model every turn of this session runs on."""
        return self._model

    def call(self, system: str, user: str) -> LLMResponse:
        """Run one turn of the conversation on the pinned model.

        Args:
            system: System prompt. Keep this byte-identical across turns
                -- it is the head of the cached prefix, and any change to
                it invalidates the cache just as a model switch would.
            user:   This turn's user message.

        Returns:
            ``LLMResponse`` for this turn.

        Raises:
            ConfigError:    No LLM backend is configured.
            AuthError:      Provider rejected the API key.
            RateLimitError: All retry attempts were rate-limited.
            TransientError: All retry attempts hit transient failures.
            WaygateError:   Base class for mapped provider failures.
        """
        return self._client.call(system=system, user=user, model=self._model)
