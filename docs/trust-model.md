# Trust Model

Trust and reputation are the only durable currency for an AI infrastructure
library. Waygate AI earns trust by making narrow promises and keeping them visible.

## The Promise

Waygate AI is the guarded gateway between application code and AI providers.

That means:

- Provider selection is deterministic and documented.
- Credentials are never logged or intentionally exposed.
- Prompt-injection defenses are enabled by default in the client path.
- Untrusted data can be sanitized and wrapped before reaching a model.
- Provider-specific errors are mapped into a stable exception hierarchy.
- Responses carry metadata that helps teams reason about cost and reliability.

## What We Do Not Claim

Waygate AI does not make LLM usage risk-free.

It does not guarantee that every prompt-injection attack is impossible, that
providers will never change behavior, or that generated content is correct. It
provides a consistent defensive baseline and makes the remaining responsibilities
clear.

## Caller Responsibilities

Applications using Waygate AI should:

- Keep API keys in environment variables or deployment secret stores.
- Sanitize and wrap untrusted user content.
- Tell models to treat `<data>` blocks as data.
- Avoid logging raw prompts when they may contain sensitive content.
- Handle `ConfigError`, `AuthError`, and `WaygateError` without exposing secrets.
- Pin versions for production deployments.
- Re-run tests when provider, model, or prompt behavior changes.

## Maintainer Responsibilities

Changes to Waygate AI should preserve these rules:

- No credential-bearing values in source, tests, docs, or logs.
- No direct provider SDK calls in consuming application examples.
- No weakening `DEFAULT_CANARY` without security evidence and tests.
- No backend priority changes without an ADR.
- No public API breaks without changelog and semver review.
- No marketing copy that overstates safety.

## Security Defaults

| Default | Reason |
|---|---|
| `DEFAULT_CANARY` appended to system prompts | Reminds the model not to follow instructions inside user data. |
| `scrub_output=True` | Removes common leaked instruction markers before output returns. |
| Typed exceptions | Keeps callers away from provider-specific SDK error handling. |
| Explicit `sanitize` and `wrap` helpers | Makes instruction/data separation easy to adopt. |

## Verification

The project currently validates with:

```bash
pytest
ruff check .
mkdocs build --strict
```

Security evidence lives under `security/evidence/`, and prompt-injection tests
cover direct override attempts, role hijacking, exfiltration requests,
jailbreak markers, structural tags, code execution payloads, buried injections,
field-specific payloads, Unicode obfuscation, and safe-content passthrough.
