"""Tests for LLMClient — retry logic, cost logging, canary injection."""

from unittest.mock import patch

import pytest

from agent_api.client import LLMClient, LLMResponse
from agent_api.exceptions import AuthError, ConfigError, RateLimitError, TransientError

VALID_KEY = "sk-ant-api03-" + "A" * 80


def _make_client(monkeypatch, backend="anthropic", model="claude-haiku-4-5-20251001"):
    monkeypatch.setenv("ANTHROPIC_API_KEY", VALID_KEY)
    monkeypatch.delenv("FORCE_OLLAMA", raising=False)
    client = LLMClient()
    client._backend = backend
    client._model = model
    return client


# ---------------------------------------------------------------------------
# Basic call
# ---------------------------------------------------------------------------

class TestLLMClientCall:
    def test_returns_llm_response(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("agent_api.providers.anthropic.call", return_value=("answer", 10, 5)):
            response = client.call("sys", "user")
        assert isinstance(response, LLMResponse)
        assert response.text == "answer"
        assert response.provider == "anthropic"
        assert response.tokens_in == 10
        assert response.tokens_out == 5

    def test_cost_populated(self, monkeypatch):
        client = _make_client(monkeypatch, model="gpt-4o-mini")
        client._backend = "openai"
        with patch("agent_api.providers.openai.call", return_value=("ok", 1_000_000, 1_000_000)):
            response = client.call("sys", "user")
        assert response.cost_usd == pytest.approx(0.75)

    def test_latency_populated(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("agent_api.providers.anthropic.call", return_value=("ok", 5, 5)):
            response = client.call("sys", "user")
        assert response.latency_ms >= 0

    def test_per_call_model_override(self, monkeypatch):
        client = _make_client(monkeypatch)
        with patch("agent_api.providers.anthropic.call", return_value=("ok", 5, 5)) as mock_call:
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

        with patch("agent_api.providers.anthropic.call", side_effect=fake_call):
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

        with patch("agent_api.providers.anthropic.call", side_effect=fake_call):
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

        with patch("agent_api.providers.anthropic.call", side_effect=flaky), patch("time.sleep"):
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

        with patch("agent_api.providers.anthropic.call", side_effect=flaky), patch("time.sleep"):
            response = client.call("sys", "user")

        assert response.text == "ok"

    def test_raises_after_max_retries_exhausted(self, monkeypatch):
        client = _make_client(monkeypatch)
        client._max_retries = 2

        with patch(
            "agent_api.providers.anthropic.call",
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
            patch("agent_api.providers.anthropic.call", side_effect=always_auth_fail),
            pytest.raises(AuthError),
        ):
            client.call("sys", "user")

        assert calls["n"] == 1  # no retries on auth failures
