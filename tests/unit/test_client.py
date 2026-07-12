"""Tests for LLMClient — retry logic, cost logging, canary injection, routing."""

from unittest.mock import patch

import pytest

from waygate_ai.client import LLMClient, LLMResponse, Session
from waygate_ai.exceptions import AuthError, ConfigError, RateLimitError, TransientError

VALID_KEY = "sk-ant-api03-" + "A" * 80


def _make_client(monkeypatch, backend="anthropic", model="claude-haiku-4-5-20251001"):
    monkeypatch.setenv("ANTHROPIC_API_KEY", VALID_KEY)
    monkeypatch.delenv("FORCE_OLLAMA", raising=False)
    client = LLMClient()
    client._backend = backend
    client._model = model
    return client


# ---------------------------------------------------------------------------
# Tier routing
# ---------------------------------------------------------------------------

class TestTierRouting:
    def test_tier_selects_model_for_active_provider(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
            client.call("sys", "user", tier="premium")
        assert mock_call.call_args[0][2] == "claude-opus-4-8"

    def test_cheap_tier_is_cheaper_than_premium(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 1_000_000, 0)):
            cheap = client.call("sys", "user", tier="cheap")
            premium = client.call("sys", "user", tier="premium")
        assert 0 < cheap.cost_usd < premium.cost_usd

    def test_every_tier_reports_nonzero_cost(self, monkeypatch):
        """Regression: premium billed $0.00 because its model had no price."""
        client = _make_client(monkeypatch)
        usage = ("ok", 1_000_000, 1_000_000)
        with patch("waygate_ai.providers.anthropic.call", return_value=usage):
            for tier in ("cheap", "standard", "premium"):
                assert client.call("sys", "user", tier=tier).cost_usd > 0, tier

    def test_tier_routes_to_the_provider_that_is_dispatched(self, monkeypatch):
        """Regression: routing and dispatch each detected the provider separately.

        The app resolved a tier against its own copy of provider detection
        while the client dispatched against `detect_backend()`. When the two
        disagreed — e.g. FORCE_OLLAMA=true, truthy to one and not the other —
        an Ollama model was sent to the Anthropic SDK. Both now read
        `self._backend`, so they cannot diverge.
        """
        client = _make_client(monkeypatch, backend="openai", model="gpt-5.4")
        with patch("waygate_ai.providers.openai.call", return_value=("ok", 5, 5)) as mock_call:
            client.call("sys", "user", tier="cheap")
        dispatched_model = mock_call.call_args[0][2]
        assert dispatched_model == "gpt-5.4-mini"
        assert not dispatched_model.startswith("claude-")

    def test_model_and_tier_together_is_rejected(self, monkeypatch):
        client = _make_client(monkeypatch)
        with pytest.raises(ValueError, match="not both"):
            client.call("sys", "user", model="claude-opus-4-8", tier="premium")

    def test_no_tier_falls_back_to_instance_default(self, monkeypatch):
        client = _make_client(monkeypatch, model="claude-sonnet-4-6")
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
            client.call("sys", "user")
        assert mock_call.call_args[0][2] == "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Cache-aware session pinning
# ---------------------------------------------------------------------------

class TestSession:
    def test_session_pins_one_model_across_turns(self, monkeypatch):
        """Switching models mid-conversation dumps the provider prompt cache."""
        client = _make_client(monkeypatch)
        session = client.session(tier="premium")
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
            for turn in range(3):
                session.call("sys", f"turn {turn}")
        models = {call.args[2] for call in mock_call.call_args_list}
        assert models == {"claude-opus-4-8"}

    def test_session_exposes_its_pinned_model(self, monkeypatch):
        client = _make_client(monkeypatch)
        assert client.session(tier="cheap").model == "claude-haiku-4-5"

    def test_session_holds_its_model_when_env_changes_midway(self, monkeypatch):
        """The tier is resolved once, at session start — not per turn."""
        client = _make_client(monkeypatch)
        session = client.session(tier="premium")
        monkeypatch.setenv("LLM_ANTHROPIC_PREMIUM_MODEL", "claude-sonnet-4-6")
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
            session.call("sys", "later turn")
        assert mock_call.call_args[0][2] == "claude-opus-4-8"

    def test_session_can_pin_an_explicit_model(self, monkeypatch):
        client = _make_client(monkeypatch)
        assert client.session(model="claude-sonnet-4-6").model == "claude-sonnet-4-6"

    def test_session_is_returned(self, monkeypatch):
        client = _make_client(monkeypatch)
        assert isinstance(client.session(tier="cheap"), Session)


# ---------------------------------------------------------------------------
# Basic call
# ---------------------------------------------------------------------------

class TestLLMClientCall:
    def test_returns_llm_response(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("waygate_ai.providers.anthropic.call", return_value=("answer", 10, 5)):
            response = client.call("sys", "user")
        assert isinstance(response, LLMResponse)
        assert response.text == "answer"
        assert response.provider == "anthropic"
        assert response.tokens_in == 10
        assert response.tokens_out == 5

    def test_cost_populated(self, monkeypatch):
        client = _make_client(monkeypatch, model="gpt-4o-mini")
        client._backend = "openai"
        with patch("waygate_ai.providers.openai.call", return_value=("ok", 1_000_000, 1_000_000)):
            response = client.call("sys", "user")
        assert response.cost_usd == pytest.approx(0.75)

    def test_latency_populated(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)):
            response = client.call("sys", "user")
        assert response.latency_ms >= 0

    def test_per_call_model_override(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("waygate_ai.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
            client.call("sys", "user", model="claude-sonnet-4-6")
        _, kwargs = mock_call.call_args
        assert mock_call.call_args[0][2] == "claude-sonnet-4-6"

    def test_raises_config_error_when_no_backend(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        client = LLMClient()
        with pytest.raises(ConfigError):
            client.call("sys", "user")


# ---------------------------------------------------------------------------
# Prompt injection guard (canary)
# ---------------------------------------------------------------------------

class TestCanaryInjection:
    def test_canary_appended_to_system_prompt(self, monkeypatch):
        client = _make_client(monkeypatch)
        captured = {}

        def fake_call(system, user, model, key, max_tokens):
            captured["system"] = system
            return ("ok", 1, 1)

        with patch("waygate_ai.providers.anthropic.call", side_effect=fake_call):
            client.call("My system prompt.", "user")

        assert "SECURITY RULE" in captured["system"]
        assert captured["system"].startswith("My system prompt.")

    def test_canary_disabled_when_none(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._canary = None
        captured = {}

        def fake_call(system, user, model, key, max_tokens):
            captured["system"] = system
            return ("ok", 1, 1)

        with patch("waygate_ai.providers.anthropic.call", side_effect=fake_call):
            client.call("Clean prompt.", "user")

        assert captured["system"] == "Clean prompt."


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------

class TestRetryLogic:
    def test_retries_on_rate_limit_and_succeeds(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._max_retries = 3
        calls = {"n": 0}

        def flaky(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] < 3:
                raise RateLimitError("too many requests")
            return ("ok", 1, 1)

        with patch("waygate_ai.providers.anthropic.call", side_effect=flaky), patch("time.sleep"):
            response = client.call("sys", "user")

        assert response.text == "ok"
        assert response.attempts == 3

    def test_retries_on_transient_error(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._max_retries = 2
        calls = {"n": 0}

        def flaky(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] < 2:
                raise TransientError("server error")
            return ("ok", 1, 1)

        with patch("waygate_ai.providers.anthropic.call", side_effect=flaky), patch("time.sleep"):
            response = client.call("sys", "user")

        assert response.text == "ok"

    def test_raises_after_max_retries_exhausted(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._max_retries = 2

        with patch(
            "waygate_ai.providers.anthropic.call",
            side_effect=RateLimitError("always limited"),
        ), patch("time.sleep"), pytest.raises(RateLimitError):
            client.call("sys", "user")

    def test_does_not_retry_on_auth_error(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._max_retries = 3
        calls = {"n": 0}

        def always_auth_fail(*args, **kwargs):
            calls["n"] += 1
            raise AuthError("bad key")

        with (
            patch("waygate_ai.providers.anthropic.call", side_effect=always_auth_fail),
            pytest.raises(AuthError),
        ):
            client.call("sys", "user")

        assert calls["n"] == 1  # no retries on auth failures
