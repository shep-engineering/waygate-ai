# API Reference

## Public Imports

```python
from limen import (
    LLMClient,
    LLMResponse,
    LimenError,
    AuthError,
    ConfigError,
    RateLimitError,
    TransientError,
    sanitize,
    wrap,
    check_response,
    is_safe,
    apply_canary,
    detect_backend,
)
```

## `LLMClient`

Main client used to call the configured provider.

### Constructor

```python
LLMClient(
    api_key=None,
    model=None,
    max_tokens=8192,
    max_retries=3,
    system_canary=DEFAULT_CANARY,
    scrub_output=True,
)
```

### Call

```python
response = client.call(
    system="System prompt.",
    user="User prompt.",
    model=None,
)
```

## `LLMResponse`

| Field | Type | Meaning |
|---|---|---|
| `text` | `str` | Scrubbed response text. |
| `provider` | `str` | Selected backend. |
| `model` | `str` | Effective model used for the call. |
| `tokens_in` | `int` | Provider-reported input tokens, or `0`. |
| `tokens_out` | `int` | Provider-reported output tokens, or `0`. |
| `cost_usd` | `float` | Estimated cost for known models. |
| `latency_ms` | `float` | Provider call latency. |
| `attempts` | `int` | Attempt number that produced the response. |

## Security Helpers

| Helper | Purpose |
|---|---|
| `sanitize(text, content_type="generic")` | Normalizes, caps, and redacts known injection patterns. |
| `wrap(label, content)` | Wraps content inside `<data label="...">` boundaries. |
| `check_response(text)` | Scrubs leaked instruction markers from model output. |
| `is_safe(text)` | Audits text without modifying it. |
| `apply_canary(system, canary=DEFAULT_CANARY)` | Appends the system-prompt canary. |

## Exceptions

| Exception | Retry behavior |
|---|---|
| `ConfigError` | Not retried. |
| `AuthError` | Not retried. |
| `RateLimitError` | Retried. |
| `TransientError` | Retried. |
| `LimenError` | Base class for mapped Limen failures. |
