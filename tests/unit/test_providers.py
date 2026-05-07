"""Tests for provider modules — all external SDK calls are mocked."""

import json
from unittest.mock import MagicMock, patch

import pytest

from agent_api.exceptions import AuthError, RateLimitError, TransientError

# ---------------------------------------------------------------------------
# Anthropic provider
# ---------------------------------------------------------------------------

class TestAnthropicProvider:
    def _make_message(self, text="Hello", tokens_in=10, tokens_out=5):
        msg = MagicMock()
        msg.content = [MagicMock(text=f"  {text}  ")]
        msg.usage.input_tokens = tokens_in
        msg.usage.output_tokens = tokens_out
        return msg

    def test_successful_call(self):
        with patch("anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.return_value = self._make_message("Hi")
            from agent_api.providers.anthropic import call
            text, tin, tout = call("sys", "user", "claude-haiku-4-5-20251001", "key", 100)
        assert text == "Hi"
        assert tin == 10
        assert tout == 5

    def test_strips_whitespace(self):
        with patch("anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.return_value = self._make_message("  padded  ")
            from agent_api.providers.anthropic import call
            text, _, _ = call("sys", "user", "model", "key", 100)
        assert text == "padded"

    def test_auth_error_raises_auth_error(self):
        import anthropic as sdk
        with patch("anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = sdk.AuthenticationError(
                message="invalid key", response=MagicMock(status_code=401), body={}
            )
            from agent_api.providers.anthropic import call
            with pytest.raises(AuthError):
                call("sys", "user", "model", "bad-key", 100)

    def test_rate_limit_raises_rate_limit_error(self):
        import anthropic as sdk
        with patch("anthropic.Anthropic") as mock_cls:
            mock_cls.return_value.messages.create.side_effect = sdk.RateLimitError(
                message="rate limit", response=MagicMock(status_code=429), body={}
            )
            from agent_api.providers.anthropic import call
            with pytest.raises(RateLimitError):
                call("sys", "user", "model", "key", 100)


# ---------------------------------------------------------------------------
# Ollama provider
# ---------------------------------------------------------------------------

class TestOllamaProvider:
    def _mock_response(self, text="Ollama says hi", prompt_tokens=8, completion_tokens=4):
        body = {
            "choices": [{"message": {"content": f"  {text}  "}}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
        }
        return json.dumps(body).encode()

    def test_successful_call(self):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = self._mock_response()

        with patch("urllib.request.urlopen", return_value=mock_resp):
            from agent_api.providers.ollama import call
            text, tin, tout = call("sys", "user", "llama3", "http://localhost:11434", 100)

        assert text == "Ollama says hi"
        assert tin == 8
        assert tout == 4

    def test_strips_whitespace(self):
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = self._mock_response("  padded  ")

        with patch("urllib.request.urlopen", return_value=mock_resp):
            from agent_api.providers.ollama import call
            text, _, _ = call("sys", "user", "llama3", "http://localhost:11434", 100)
        assert text == "padded"

    def test_network_error_raises_transient_error(self):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
            from agent_api.providers.ollama import call
            with pytest.raises(TransientError, match="Ollama not reachable"):
                call("sys", "user", "llama3", "http://localhost:11434", 100)

    def test_missing_usage_defaults_to_zero(self):
        body = {"choices": [{"message": {"content": "hi"}}]}
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps(body).encode()

        with patch("urllib.request.urlopen", return_value=mock_resp):
            from agent_api.providers.ollama import call
            _, tin, tout = call("sys", "user", "llama3", "http://localhost:11434", 100)
        assert tin == 0
        assert tout == 0
