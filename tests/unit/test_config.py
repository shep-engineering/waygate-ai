"""Tests for limen.config — key validation and backend detection."""

import pytest

from limen.config import detect_backend, estimate_cost, is_valid_anthropic_key

# ---------------------------------------------------------------------------
# is_valid_anthropic_key
# ---------------------------------------------------------------------------

VALID_KEY = "sk-ant-api03-" + "A" * 80


def test_valid_anthropic_key_passes():
    assert is_valid_anthropic_key(VALID_KEY) is True


def test_placeholder_key_fails():
    assert is_valid_anthropic_key("sk-ant-api03-...") is False


def test_empty_key_fails():
    assert is_valid_anthropic_key("") is False


def test_openai_key_fails():
    assert is_valid_anthropic_key("sk-proj-abc123") is False


def test_key_with_leading_whitespace_passes():
    assert is_valid_anthropic_key("  " + VALID_KEY) is True


# ---------------------------------------------------------------------------
# detect_backend
# ---------------------------------------------------------------------------

def test_detect_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", VALID_KEY)
    monkeypatch.delenv("FORCE_OLLAMA", raising=False)
    backend, model = detect_backend()
    assert backend == "anthropic"
    assert model != ""


def test_detect_openai_when_no_anthropic(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")
    monkeypatch.delenv("FORCE_OLLAMA", raising=False)
    backend, model = detect_backend()
    assert backend == "openai"


def test_detect_ollama_fallback(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")
    backend, model = detect_backend()
    assert backend == "ollama"
    assert model == "llama3"


def test_detect_none_when_nothing_configured(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    backend, model = detect_backend()
    assert backend == "none"
    assert model == ""


def test_force_ollama_overrides_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", VALID_KEY)
    monkeypatch.setenv("FORCE_OLLAMA", "1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")
    backend, _ = detect_backend()
    assert backend == "ollama"


def test_invalid_anthropic_key_logs_warning_and_falls_through(monkeypatch, caplog):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-tooshort")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import logging
    with caplog.at_level(logging.WARNING, logger="limen.config"):
        backend, _ = detect_backend()
    assert backend == "ollama"
    assert "does not match the expected format" in caplog.text


# ---------------------------------------------------------------------------
# estimate_cost
# ---------------------------------------------------------------------------

def test_cost_known_model():
    cost = estimate_cost("gpt-4o-mini", tokens_in=1_000_000, tokens_out=1_000_000)
    assert cost == pytest.approx(0.75)  # $0.15 in + $0.60 out


def test_cost_unknown_model_returns_zero():
    assert estimate_cost("unknown-model-xyz", 1000, 1000) == 0.0


def test_cost_zero_tokens():
    assert estimate_cost("gpt-4o-mini", 0, 0) == 0.0
