"""Tier-based model routing: send each task to the cheapest capable model.

WHY THIS LIVES IN WAYGATE
-------------------------
Model selection is a provider concern, not an application concern. An
application should be able to say "this task needs the cheap tier" and
never learn the name of a model. Before this module existed, callers
encoded tiers as literal model names of one provider and remapped them
downstream -- which meant business code knew about ``gpt-4o-mini``, and
every consumer reimplemented provider detection (and drifted from
``config.detect_backend`` while doing it).

THE MODEL
---------
Three tiers, ordered by capability and price:

    cheap     high-volume, mechanical work (classify, extract, tag)
    standard  the default for real work (summarize, parse, analyze)
    premium   the small slice that genuinely needs a frontier model

Research on production routing consistently finds only ~8-16% of tasks
need the premium tier, while humans -- left to choose -- pick premium
~85% of the time. Declaring a tier per touchpoint and auditing those
declarations downward is where the savings come from.

``MODEL_REGISTRY`` maps ``(provider, tier)`` to a :class:`ModelSpec` that
carries the model id *and its price*. Pairing them is deliberate: a
router that cannot price a model cannot route on price, and a cost table
maintained separately from the routing table drifts out of sync -- which
is exactly how unpriced models end up silently billing as $0.00.

Every tier is overridable per deployment via
``LLM_<PROVIDER>_<TIER>_MODEL`` (e.g. ``LLM_ANTHROPIC_PREMIUM_MODEL``),
so an environment can bias cheaper without a code change.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Final, Literal

logger = logging.getLogger(__name__)

Tier = Literal["cheap", "standard", "premium"]

TIERS: Final[tuple[Tier, ...]] = ("cheap", "standard", "premium")


@dataclass(frozen=True)
class ModelSpec:
    """A model and what it costs to call.

    Args:
        model_id: Provider-native model identifier, sent to the SDK as-is.
        cost_in: USD per 1M input tokens, or ``None`` when the price is
            not known to this library.
        cost_out: USD per 1M output tokens, or ``None`` when unknown.

    Returns:
        Frozen dataclass instance.

    Raises:
        None.
    """

    model_id: str
    cost_in: float | None
    cost_out: float | None

    @property
    def is_priced(self) -> bool:
        """Return True when both input and output prices are known."""
        return self.cost_in is not None and self.cost_out is not None


# ---------------------------------------------------------------------------
# The registry: (provider, tier) -> ModelSpec
#
# Anthropic prices verified against the published Claude pricing table
# (Haiku 4.5 $1/$5, Sonnet 4.6 $3/$15, Opus 4.8 $5/$25 per 1M tokens).
#
# OpenAI models are carried UNPRICED (None) rather than guessed. An
# unpriced model still routes correctly -- it just cannot be costed, and
# `estimate_cost` says so out loud instead of returning a confident 0.0.
# Populate these from the provider's published pricing to enable cost
# telemetry on the OpenAI path.
#
# Ollama runs locally: there is no per-token charge, so 0.0 is the true
# cost, not an unknown one. Every tier collapses onto OLLAMA_MODEL --
# a single local model serves all three.
# ---------------------------------------------------------------------------
MODEL_REGISTRY: Final[dict[str, dict[Tier, ModelSpec]]] = {
    "anthropic": {
        "cheap": ModelSpec("claude-haiku-4-5", 1.00, 5.00),
        "standard": ModelSpec("claude-sonnet-4-6", 3.00, 15.00),
        "premium": ModelSpec("claude-opus-4-8", 5.00, 25.00),
    },
    # Standard short-context list prices, per 1M tokens, from OpenAI's official pricing
    # page (developers.openai.com/api/docs/pricing, checked 2026-07-12). These are the
    # non-batch, non-cached rates -- Batch/Flex and cached input are cheaper, so a real
    # bill lands at or below these numbers. Estimating high is the safe direction for a
    # cost guardrail; estimating $0.00 (which is what shipping these as None did) is not.
    "openai": {
        "cheap": ModelSpec("gpt-5.4-mini", 0.75, 4.50),
        "standard": ModelSpec("gpt-5.4", 2.50, 15.00),
        "premium": ModelSpec("gpt-5.5", 5.00, 30.00),
    },
}

# Prices for models that are not the current pick for any tier: previous
# defaults, dated aliases, and models a deployment pins via an env
# override. Without these, switching a tier to an older model would
# silently zero out its cost telemetry.
_EXTRA_PRICES: Final[dict[str, ModelSpec]] = {
    "claude-haiku-4-5-20251001": ModelSpec("claude-haiku-4-5-20251001", 1.00, 5.00),
    "claude-opus-4-7": ModelSpec("claude-opus-4-7", 5.00, 25.00),
    "claude-opus-4-6": ModelSpec("claude-opus-4-6", 5.00, 25.00),
    "claude-sonnet-5": ModelSpec("claude-sonnet-5", 3.00, 15.00),
    "claude-fable-5": ModelSpec("claude-fable-5", 10.00, 50.00),
    "gpt-4o": ModelSpec("gpt-4o", 5.00, 15.00),
    "gpt-4o-mini": ModelSpec("gpt-4o-mini", 0.15, 0.60),
}

_OLLAMA_FALLBACK_MODEL: Final[str] = "llama3"

# Unknown-model warnings fire once per model id, not once per call: a
# high-volume unpriced model would otherwise flood the log with a line
# per request.
_warned_unknown: set[str] = set()


def _env_override(provider: str, tier: Tier) -> str | None:
    """Return the ``LLM_<PROVIDER>_<TIER>_MODEL`` override, if set."""
    raw = os.environ.get(f"LLM_{provider.upper()}_{tier.upper()}_MODEL", "").strip()
    return raw or None


def resolve(tier: Tier, provider: str) -> str:
    """Return the model *provider* should use for *tier*.

    Resolution order: the ``LLM_<PROVIDER>_<TIER>_MODEL`` env override
    wins; then the registry default. Ollama collapses every tier onto
    ``OLLAMA_MODEL`` -- one local model serves all three.

    Args:
        tier: One of ``"cheap"``, ``"standard"``, ``"premium"``.
        provider: Backend name from ``detect_backend`` (``"anthropic"``,
            ``"openai"``, or ``"ollama"``).

    Returns:
        A provider-native model id, ready to hand to the provider SDK.

    Raises:
        ValueError: *tier* is not a known tier, or *provider* has no
            registry entry and is not Ollama.
    """
    if tier not in TIERS:
        raise ValueError(f"Unknown tier {tier!r}. Expected one of {TIERS}.")

    override = _env_override(provider, tier)
    if override:
        return override

    if provider == "ollama":
        return os.environ.get("OLLAMA_MODEL", "").strip() or _OLLAMA_FALLBACK_MODEL

    tiers = MODEL_REGISTRY.get(provider)
    if tiers is None:
        raise ValueError(
            f"No models registered for provider {provider!r}. "
            f"Known providers: {sorted(MODEL_REGISTRY)} (plus 'ollama')."
        )
    return tiers[tier].model_id


def spec_for(model_id: str) -> ModelSpec | None:
    """Return the :class:`ModelSpec` for *model_id*, or ``None`` if unregistered.

    Searches the tier registry first, then the supplementary price table.
    Ollama models are reported at zero cost -- local inference has no
    per-token charge, so 0.0 is the true price rather than an unknown one.

    Args:
        model_id: Provider-native model identifier.

    Returns:
        The matching spec, or ``None`` when the model is not registered
        and therefore cannot be priced.

    Raises:
        None.
    """
    for tiers in MODEL_REGISTRY.values():
        for spec in tiers.values():
            if spec.model_id == model_id:
                return spec

    extra = _EXTRA_PRICES.get(model_id)
    if extra is not None:
        return extra

    ollama_model = os.environ.get("OLLAMA_MODEL", "").strip()
    if ollama_model and model_id == ollama_model:
        return ModelSpec(model_id, 0.0, 0.0)

    return None


def estimate_cost(model_id: str, tokens_in: int, tokens_out: int) -> float:
    """Return the estimated USD cost of one call.

    Unknown or unpriced models return ``0.0`` -- but unlike a silent
    lookup miss, they also log a warning (once per model id). A model
    that quietly costs nothing is indistinguishable from a model that is
    genuinely free, and that ambiguity is how a cost dashboard ends up
    reading $0.00 for a month of production traffic.

    Args:
        model_id: Model that served the call.
        tokens_in: Input tokens billed.
        tokens_out: Output tokens billed.

    Returns:
        Estimated USD cost, or ``0.0`` when the model has no known price.

    Raises:
        None.
    """
    spec = spec_for(model_id)

    if spec is None:
        if model_id not in _warned_unknown:
            _warned_unknown.add(model_id)
            logger.warning(
                "No price registered for model %r -- cost_usd will be reported "
                "as 0.00 for every call on this model. Add it to "
                "waygate_ai.router.MODEL_REGISTRY or _EXTRA_PRICES to enable "
                "cost telemetry.",
                model_id,
            )
        return 0.0

    if not spec.is_priced:
        if model_id not in _warned_unknown:
            _warned_unknown.add(model_id)
            logger.warning(
                "Model %r is registered but unpriced -- cost_usd will be "
                "reported as 0.00. Populate cost_in/cost_out in "
                "waygate_ai.router to enable cost telemetry.",
                model_id,
            )
        return 0.0

    return (tokens_in * spec.cost_in + tokens_out * spec.cost_out) / 1_000_000
