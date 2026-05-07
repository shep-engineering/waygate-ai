"""Anthropic Claude provider."""

from __future__ import annotations

from agent_api.exceptions import AuthError, RateLimitError, TransientError


def call(
    system: str,
    user: str,
    model: str,
    api_key: str,
    max_tokens: int,
) -> tuple[str, int, int]:
    """Call Anthropic and return ``(text, tokens_in, tokens_out)``.

    Args:
        system: System prompt sent through the Anthropic messages API.
        user: User message content.
        model: Anthropic model name.
        api_key: Anthropic API key.
        max_tokens: Completion token cap.

    Returns:
        Tuple of response text, input tokens, and output tokens.

    Raises:
        ImportError:     anthropic package not installed.
        AuthError:       invalid or revoked API key (401 / 403).
        RateLimitError:  rate limit exceeded (429).
        TransientError:  server error or network failure (5xx).
    """
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "anthropic package not installed. Run: pip install 'agent-api[anthropic]'"
        ) from exc

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.AuthenticationError as exc:
        raise AuthError(str(exc)) from exc
    except anthropic.RateLimitError as exc:
        raise RateLimitError(str(exc)) from exc
    except anthropic.APIStatusError as exc:
        if exc.status_code >= 500:
            raise TransientError(str(exc)) from exc
        raise
    except anthropic.APIConnectionError as exc:
        raise TransientError(str(exc)) from exc

    text = message.content[0].text.strip()
    tokens_in = message.usage.input_tokens
    tokens_out = message.usage.output_tokens
    return text, tokens_in, tokens_out
