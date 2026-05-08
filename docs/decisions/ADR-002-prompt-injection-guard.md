# ADR-002: Embedded Prompt Injection Guard

## Status

Accepted

## Context

The library is intended for agents and applications that may pass untrusted text
into model prompts. Relying on every caller to remember prompt-injection
defenses is fragile, especially when the library already owns the system prompt
handoff to providers.

## Decision

Embed prompt-injection guard behavior in `limen`:

- `LLMClient` appends `DEFAULT_CANARY` to every system prompt by default.
- `scrub_output=True` by default routes model output through `check_response`.
- `limen.security` exposes importable guard helpers: `sanitize`, `wrap`,
  `check_response`, `is_safe`, and `apply_canary`.
- Security tests cover known injection classes and safe-content passthrough.

## Alternatives Rejected

- Caller-only security responsibility: this would make secure usage optional in
  the most common path.
- Separate security package: this would increase integration friction and make
  it easier to forget the guard.
- Output scrubbing disabled by default: this would allow leaked instruction
  blocks to reach downstream systems unless every caller opted in.

## Consequences

- The default client path is guarded without extra caller code.
- Callers can still sanitize and wrap user-controlled content before calling the
  client.
- Any change that removes or weakens `DEFAULT_CANARY` must update the security
  evidence and tests.
