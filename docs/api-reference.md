# API Reference

## Public Imports

```python
from waygate_ai import (
    LLMClient,
    LLMResponse,
    Session,
    WaygateError,
    AuthError,
    ConfigError,
    RateLimitError,
    TransientError,
    MODEL_REGISTRY,
    TIERS,
    ModelSpec,
    Tier,
    estimate_cost,
    resolve,
    spec_for,
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

### `call`

```python
response = client.call(
    system="System prompt.",
    user="User prompt.",
    tier=None,      # "cheap" | "standard" | "premium" -- the normal path
    model=None,     # exact model id, bypassing the router (escape hatch)
)
```

Pass `tier` to let the router pick the cheapest capable model on the active
provider. Pass `model` only to pin an exact id.

Raises `ValueError` if **both** `tier` and `model` are given.

### `resolve_model`

```python
client.resolve_model(tier="premium")   # -> "claude-opus-4-8"
```

Returns the model id a `(model, tier)` pair selects, without making a call.
Resolution runs against the same backend the client dispatches to.

### `session`

```python
session = client.session(tier="premium")   # or model="..."
```

Returns a [`Session`](#session) pinned to one model. See
[Model Routing](model-routing.md#cache-aware-sessions).

## `Session`

A multi-turn conversation pinned to one model. Provider prompt caches are keyed
to the model, so switching mid-conversation discards the cached prefix and
re-bills it at full price. A session resolves its tier **once** and holds it.

| Member | Type | Meaning |
|---|---|---|
| `model` | `str` | The model every turn of this session runs on. |
| `call(system, user)` | `LLMResponse` | Run one turn on the pinned model. |

The session pins the model, not the history — the caller still owns the
transcript. Keep `system` byte-identical across turns; it is the head of the
cached prefix.

## `LLMResponse`

| Field | Type | Meaning |
|---|---|---|
| `text` | `str` | Scrubbed response text. |
| `provider` | `str` | Selected backend. |
| `model` | `str` | Effective model used for the call — what the tier resolved to. |
| `tokens_in` | `int` | Provider-reported input tokens, or `0`. |
| `tokens_out` | `int` | Provider-reported output tokens, or `0`. |
| `cost_usd` | `float` | Estimated cost. `0.0` for an unpriced model, which also logs a warning. |
| `latency_ms` | `float` | Provider call latency. |
| `attempts` | `int` | Attempt number that produced the response. |

## Router

See [Model Routing](model-routing.md) for the concepts.

| Name | Type | Purpose |
|---|---|---|
| `Tier` | `Literal["cheap", "standard", "premium"]` | The tier type. |
| `TIERS` | `tuple[Tier, ...]` | All tiers, cheapest first. |
| `MODEL_REGISTRY` | `dict[str, dict[Tier, ModelSpec]]` | `(provider, tier)` to model + price. |
| `resolve(tier, provider)` | `str` | The model id a tier selects on a provider. |
| `spec_for(model_id)` | `ModelSpec \| None` | The spec for a model, or `None` if unregistered. |
| `estimate_cost(model_id, tokens_in, tokens_out)` | `float` | Estimated USD cost. Warns once per unpriced model. |

### `ModelSpec`

| Field | Type | Meaning |
|---|---|---|
| `model_id` | `str` | Provider-native model identifier, sent to the SDK as-is. |
| `cost_in` | `float \| None` | USD per 1M input tokens. `None` when the price is unknown. |
| `cost_out` | `float \| None` | USD per 1M output tokens. `None` when unknown. |
| `is_priced` | `bool` | True when both prices are known. |

Overriding a tier per deployment:

```bash
LLM_<PROVIDER>_<TIER>_MODEL=<model-id>    # e.g. LLM_ANTHROPIC_PREMIUM_MODEL
```

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
| `WaygateError` | Base class for mapped Waygate AI failures. |
