# ADR-003: Backend Priority Order

## Status

Accepted

## Context

Users may have more than one provider configured in their environment. The
library needs deterministic backend selection without requiring each caller to
pass a backend option into application code.

## Decision

Use this priority order in `detect_backend()`:

1. Valid `ANTHROPIC_API_KEY`, unless `FORCE_OLLAMA=1`
2. `OPENAI_API_KEY`, unless `FORCE_OLLAMA=1`
3. `OLLAMA_MODEL`
4. No backend, represented as `("none", "")` until `LLMClient.call()` raises
   `ConfigError`

`FORCE_OLLAMA=1` is the explicit local-only escape hatch. It does not invent an
Ollama model; `OLLAMA_MODEL` must still be set.

## Alternatives Rejected

- Explicit backend constructor parameter: this would work against the goal of
  environment-only configuration for most callers.
- First installed optional dependency wins: installed packages do not indicate
  intended runtime provider.
- Random or provider-balanced selection: non-determinism makes debugging,
  cost tracking, and test expectations harder.

## Consequences

- Backend selection is predictable and easy to document.
- Changing the priority order requires a new ADR and documentation updates.
- Environments that need local-only behavior can set `FORCE_OLLAMA=1` and
  `OLLAMA_MODEL`.
