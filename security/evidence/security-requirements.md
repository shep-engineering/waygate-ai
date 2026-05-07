# Security Requirements — agent-api

## SR-1: Secret handling
API keys must be read from environment variables only. Never hardcoded, logged, or included in exceptions.

## SR-2: Prompt injection defense
The library must provide `sanitize()`, `wrap()`, `check_response()`, and `is_safe()` as first-class importable tools. `DEFAULT_CANARY` must be applied to every system prompt by default.

## SR-3: Output scrubbing
`check_response()` must be applied to all LLM output before returning to callers (`scrub_output=True` default).

## SR-4: Dependency hygiene
All third-party dependencies must be scanned via `pip-audit` on every CI run. Findings block merge.

## SR-5: No secrets in source control
`.env`, `*.env`, and `.env.*` must be in `.gitignore`. CI secret scanning runs on every PR.

## SR-6: Injection test coverage
CI must run the full `test_security.py` suite. All 10 injection classes must have automated tests.
