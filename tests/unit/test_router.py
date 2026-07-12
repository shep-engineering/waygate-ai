"""Tests for waygate_ai.router — tier resolution and cost estimation."""

import logging

import pytest

from waygate_ai.router import (
    MODEL_REGISTRY,
    TIERS,
    estimate_cost,
    resolve,
    spec_for,
)

VALID_KEY = "sk-ant-api03-" + "A" * 80


@pytest.fixture(autouse=True)
def _clear_warn_cache():
    """Reset the warn-once set so each test sees warnings fire fresh."""
    from waygate_ai import router
    router._warned_unknown.clear()
    yield
    router._warned_unknown.clear()


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """Strip routing env vars so registry defaults are what is under test."""
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    for provider in ("ANTHROPIC", "OPENAI", "OLLAMA"):
        for tier in ("CHEAP", "STANDARD", "PREMIUM"):
            monkeypatch.delenv(f"LLM_{provider}_{tier}_MODEL", raising=False)


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier", TIERS)
def test_every_tier_resolves_on_every_registered_provider(tier):
    for provider in MODEL_REGISTRY:
        assert resolve(tier, provider)


def test_tiers_are_ordered_cheapest_first():
    anthropic = MODEL_REGISTRY["anthropic"]
    assert anthropic["cheap"].cost_in < anthropic["standard"].cost_in
    assert anthropic["standard"].cost_in < anthropic["premium"].cost_in


def test_resolve_anthropic_defaults():
    assert resolve("cheap", "anthropic") == "claude-haiku-4-5"
    assert resolve("standard", "anthropic") == "claude-sonnet-4-6"
    assert resolve("premium", "anthropic") == "claude-opus-4-8"


def test_env_override_wins_over_registry(monkeypatch):
    monkeypatch.setenv("LLM_ANTHROPIC_PREMIUM_MODEL", "claude-sonnet-4-6")
    assert resolve("premium", "anthropic") == "claude-sonnet-4-6"


def test_blank_env_override_is_ignored(monkeypatch):
    monkeypatch.setenv("LLM_ANTHROPIC_PREMIUM_MODEL", "   ")
    assert resolve("premium", "anthropic") == "claude-opus-4-8"


def test_ollama_collapses_every_tier_onto_one_local_model(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    assert {resolve(t, "ollama") for t in TIERS} == {"qwen2.5:7b"}


def test_unknown_tier_raises():
    with pytest.raises(ValueError, match="Unknown tier"):
        resolve("cheapest", "anthropic")  # type: ignore[arg-type]


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="No models registered"):
        resolve("cheap", "bedrock")


# ---------------------------------------------------------------------------
# estimate_cost
#
# The zero-cost regression: a tier that resolved to a model missing from
# the price table used to report cost_usd=0.00 on every call, silently.
# Pairing price with model in one registry makes that unrepresentable for
# routed models, and the warning covers everything else.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier", TIERS)
def test_every_anthropic_tier_is_priced(tier):
    """Regression: premium resolved to a model absent from the cost table."""
    model = resolve(tier, "anthropic")
    spec = spec_for(model)
    assert spec is not None, f"{tier} -> {model} has no spec"
    assert spec.is_priced, f"{tier} -> {model} would bill as $0.00"
    assert estimate_cost(model, 1_000_000, 1_000_000) > 0


def test_haiku_price_matches_published_rate():
    """Regression: the table carried $0.80/$4.00; the real rate is $1.00/$5.00."""
    assert estimate_cost("claude-haiku-4-5", 1_000_000, 0) == pytest.approx(1.00)
    assert estimate_cost("claude-haiku-4-5", 0, 1_000_000) == pytest.approx(5.00)


def test_opus_premium_is_priced():
    assert estimate_cost("claude-opus-4-8", 1_000_000, 1_000_000) == pytest.approx(30.00)


def test_dated_haiku_alias_prices_same_as_bare_alias():
    dated = estimate_cost("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
    bare = estimate_cost("claude-haiku-4-5", 1_000_000, 1_000_000)
    assert dated == pytest.approx(bare)


def test_unknown_model_returns_zero_but_warns(caplog):
    with caplog.at_level(logging.WARNING, logger="waygate_ai.router"):
        cost = estimate_cost("totally-made-up-model", 1000, 1000)
    assert cost == 0.0
    assert "No price registered" in caplog.text


def test_registered_but_unpriced_model_returns_zero_but_warns(caplog, monkeypatch):
    """A registered-but-unpriced model returns 0.0 AND says so loudly.

    This used to assert that the real OpenAI tiers were unpriced -- i.e. it encoded the
    $0.00 bug as intended behaviour, which is why the bug was never caught. The OpenAI
    tiers now carry real prices (and test_every_registered_model_is_priced forbids adding
    an unpriced one), so the unpriced case is simulated rather than shipped.

    The warning still matters: if someone adds a provider and forgets its prices, the unit
    test above fails at build time -- but if a model somehow reaches production unpriced,
    this is what stops cost_usd=0.00 from looking like a genuinely free call.
    """
    from waygate_ai import router

    monkeypatch.setitem(
        router.MODEL_REGISTRY,
        "fauxprovider",
        {t: router.ModelSpec(f"faux-{t}", None, None) for t in TIERS},
    )
    with caplog.at_level(logging.WARNING, logger="waygate_ai.router"):
        cost = estimate_cost(resolve("premium", "fauxprovider"), 1000, 1000)
    assert cost == 0.0
    assert "unpriced" in caplog.text


def test_unknown_model_warns_only_once(caplog):
    with caplog.at_level(logging.WARNING, logger="waygate_ai.router"):
        for _ in range(5):
            estimate_cost("noisy-unknown-model", 10, 10)
    assert caplog.text.count("No price registered") == 1


def test_ollama_model_costs_nothing(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    assert estimate_cost("qwen2.5:7b", 1_000_000, 1_000_000) == 0.0
    assert spec_for("qwen2.5:7b").is_priced


def test_zero_tokens_cost_nothing():
    assert estimate_cost("claude-opus-4-8", 0, 0) == 0.0


# ---------------------------------------------------------------------------
# Every registered model MUST carry a price.
#
# The OpenAI tiers shipped with cost_in/cost_out = None. They routed correctly, so every
# test passed -- and every OpenAI call silently reported cost_usd = $0.00. A model that
# quietly costs nothing is indistinguishable from a model that is genuinely free, so a
# cost dashboard reads $0.00 for a month of production traffic and nobody notices.
#
# estimate_cost() warns on an unpriced model, but a warning in a log nobody greps is not a
# guardrail. This is: a provider cannot be added to the registry without its prices.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provider", sorted(MODEL_REGISTRY))
@pytest.mark.parametrize("tier", sorted(TIERS))
def test_every_registered_model_is_priced(provider: str, tier: str) -> None:
    spec = MODEL_REGISTRY[provider][tier]
    assert spec.cost_in is not None, (
        f"{provider}/{tier} ({spec.model_id}) has no INPUT price. It would report "
        f"cost_usd=0.00 on every call -- silently free. Add the real price."
    )
    assert spec.cost_out is not None, (
        f"{provider}/{tier} ({spec.model_id}) has no OUTPUT price. It would report "
        f"cost_usd=0.00 on every call -- silently free. Add the real price."
    )
    assert spec.cost_in > 0 and spec.cost_out > 0, (
        f"{provider}/{tier} ({spec.model_id}) is priced at zero. No model is free."
    )


@pytest.mark.parametrize("provider", sorted(MODEL_REGISTRY))
@pytest.mark.parametrize("tier", sorted(TIERS))
def test_every_registered_model_reports_nonzero_cost(provider: str, tier: str) -> None:
    """The property that actually matters: a real call must not report $0.00."""
    spec = MODEL_REGISTRY[provider][tier]
    cost = estimate_cost(spec.model_id, tokens_in=1_000, tokens_out=1_000)
    assert cost > 0, (
        f"estimate_cost({spec.model_id!r}) returned {cost} for a 1k/1k call. "
        f"That is the $0.00 bug: the model is registered but not priced."
    )


def test_a_cheaper_tier_never_costs_more_than_a_dearer_one() -> None:
    """Guards a fat-fingered price: cheap <= standard <= premium, per provider."""
    for provider, tiers in MODEL_REGISTRY.items():
        c = estimate_cost(tiers["cheap"].model_id, 1_000, 1_000)
        s = estimate_cost(tiers["standard"].model_id, 1_000, 1_000)
        p = estimate_cost(tiers["premium"].model_id, 1_000, 1_000)
        assert c <= s <= p, (
            f"{provider} tier prices are not monotonic: "
            f"cheap={c:.6f} standard={s:.6f} premium={p:.6f}"
        )
