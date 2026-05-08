"""OpenAI provider."""

from __future__ import annotations

from waygate_ai.exceptions import AuthError, RateLimitError, TransientError


def call(
    system: str,
    user: str,
    model: str,
    api_key: str,
    max_tokens: int,
) -> tuple[str, int, int]:
    """Call OpenAI and return ``(text, tokens_in, tokens_out)``.

    Args:
        system: System prompt sent in the chat completion request.
        user: User message content.
        model: OpenAI model name.
        api_key: OpenAI API key.
        max_tokens: Completion token cap.

    Returns:
        Tuple of response text, input tokens, and output tokens.

    Raises:
        ImportError:     openai package not installed.
        AuthError:       invalid or revoked API key (401 / 403).
        RateLimitError:  rate limit exceeded (429).
        TransientError:  server error or network failure (5xx).
    """
    try:
        import openai
    except ImportError as exc:
        raise ImportError(
            "openai package not installed. Run: pip install 'waygate-ai[openai]'"
        ) from exc

    try:
        client = openai.OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
    except openai.AuthenticationError as exc:
        raise AuthError(str(exc)) from exc
    except openai.RateLimitError as exc:
        raise RateLimitError(str(exc)) from exc
    except openai.APIStatusError as exc:
        if exc.status_code >= 500:
            raise TransientError(str(exc)) from exc
        raise
    except openai.APIConnectionError as exc:
        raise TransientError(str(exc)) from exc

    text = completion.choices[0].message.content.strip()
    tokens_in = completion.usage.prompt_tokens
    tokens_out = completion.usage.completion_tokens
    return text, tokens_in, tokens_out
