# Security Requirements

## System

`waygate_ai` — Python library providing a unified LLM client (Anthropic, OpenAI, Ollama) with
built-in prompt injection defenses (`sanitize`, `wrap`, `check_response`, `is_safe`, `DEFAULT_CANARY`).

## Verification target

ASVS Level 1 (library, not directly user-facing). No network service exposed. No persistent storage.

## Requirements (minimum)

| ID | Requirement | Archetype source |
|---|---|---|
| SR-1 | API keys read from environment variables only — never hardcoded, logged, or included in exceptions | security-guardian §1.1 |
| SR-2 | `sanitize()`, `wrap()`, `check_response()`, `is_safe()` provided as importable tools; `DEFAULT_CANARY` applied to every system prompt by default | prompt-injection-guard §I |
| SR-3 | `check_response()` applied to all LLM output before returning to callers (`scrub_output=True` default) | prompt-injection-guard §1.4 |
| SR-4 | All third-party dependencies scanned via `pip-audit` on every CI run; findings block merge | security-guardian §2.6 |
| SR-5 | `.env`, `*.env`, `.env.*` in `.gitignore`; CI secret scanning on every PR | security-guardian §1.1 |
| SR-6 | CI runs full `test_security.py` suite; all 10 injection classes have automated tests | prompt-injection-guard §1.6 |
| SR-7 | SBOM generated on every release and stored under `security/sbom/` | security-guardian §2.6 |
| SR-8 | Dependency vulnerability scan (pip-audit) + secret scan (gitleaks) + sbom gate in CI — all fail-closed | security-guardian §2.8 |

## Exceptions

| Exception | Risk | Compensating control | Owner | Review date |
|---|---|---|---|---|
| ASVS Level 1 only (not Level 2) | Low — library has no auth surface, no network exposure | Consumer applications must implement Level 2+ where Waygate AI is used | Library maintainer | 2026-05-07 |
