"""Unit tests for the OpenAI provider call shape."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from waygate_ai.providers import openai as openai_provider


def _fake_openai_client(content: str = "ok"):
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    completion.usage = MagicMock(prompt_tokens=11, completion_tokens=7)
    client = MagicMock()
    client.chat.completions.create.return_value = completion
    return client


def test_openai_call_uses_max_completion_tokens_not_max_tokens():
    """Regression: gpt-5/o-series reject ``max_tokens`` (HTTP 400). The provider
    must send ``max_completion_tokens`` instead."""
    client = _fake_openai_client()
    with patch("openai.OpenAI", return_value=client):
        text, tokens_in, tokens_out = openai_provider.call(
            system="sys", user="usr", model="gpt-5.4", api_key="sk-test", max_tokens=256
        )

    assert (text, tokens_in, tokens_out) == ("ok", 11, 7)
    kwargs = client.chat.completions.create.call_args.kwargs
    assert kwargs.get("max_completion_tokens") == 256
    assert "max_tokens" not in kwargs, "legacy max_tokens must not be sent"
    assert kwargs["model"] == "gpt-5.4"
