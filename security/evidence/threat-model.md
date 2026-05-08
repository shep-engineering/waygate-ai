# Threat Model

**Version**: 0.1.0  
**Date**: 2026-05-07  
**Classification**: Internal

---

## Overview

`waygate_ai` is a Python library consumed by application code. It routes LLM calls
to Anthropic Claude, OpenAI, or local Ollama. It does **not** expose any network
service, store data persistently, or handle end-user authentication.

## Data flows

```
Caller application
  → Waygate AI.LLMClient.call(system, user)
    → [provider SDK or urllib]
      → Anthropic API / OpenAI API / Ollama (localhost)
        → LLM response text
      → check_response() scrub
    → LLMResponse returned to caller
```

---

## Assets

| Asset | Classification | Owner |
|---|---|---|
| `ANTHROPIC_API_KEY` | Secret | Caller environment |
| `OPENAI_API_KEY` | Secret | Caller environment |
| LLM prompt content | Varies — may contain PII if caller passes it | Caller |
| LLM response text | Varies | Provider |
| Cost/token logs | Internal operational | Library |

**Trust boundary**: The library trusts its caller completely. The caller is
responsible for sanitizing user-supplied content before passing it to `LLMClient.call()`.
The library provides `sanitize()`, `wrap()`, and `check_response()` as tools but
does not enforce their use.

---

## Threat enumeration

| # | Threat | Attack Vector | Likelihood | Impact | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|
| T1 | Prompt injection via `user` arg | Caller passes unsanitized user input | Medium | High | `sanitize()` + `wrap()` provided; `DEFAULT_CANARY` applied to every call | Medium — caller must adopt sanitize/wrap |
| T2 | System prompt exfiltration | Adversarial `user` content triggers model to echo system prompt | Medium | Medium | `DEFAULT_CANARY` instructs model not to reproduce instructions; `check_response()` strips echo patterns | Low |
| T3 | API key leakage via logs | Key accidentally logged | Low | High | Keys read from env only; `_log()` logs provider/model/tokens, never key values | Low |
| T4 | API key leakage via exception messages | SDK exception includes key in message | Low | High | Provider exceptions are caught and re-raised as typed `WaygateError`; raw SDK exceptions do not propagate | Low |
| T5 | Supply chain — malicious provider SDK | Compromised `anthropic` or `openai` package | Low | Critical | `pip-audit` in CI; pinned in `pyproject.toml` optional-deps | Low |
| T6 | Denial of wallet — runaway LLM calls | Bug causes infinite retry loop | Low | Medium | `max_retries` cap (default 3); exponential backoff | Low |
| T7 | Indirect injection via RAG content | Caller retrieves poisoned documents and passes them as `user` | Medium | High | `sanitize()` + `wrap()` provided; caller must apply before RAG content enters prompt | Medium — outside library's control |

---

## Out of Scope

- Authentication and authorization of the caller
- Network security of the Anthropic/OpenAI/Ollama endpoints
- Storage of LLM outputs by the caller
- PII handling within LLM response content

---

## Top risks summary

| Rank | Threat | Severity | Status |
|---|---|---|---|
| 1 | T1 — Prompt injection via `user` arg | High | Mitigated (sanitize/wrap/canary provided; residual: caller must adopt) |
| 2 | T7 — Indirect injection via RAG content | High | Mitigated (same tools; residual: outside library control) |
| 3 | T3 — API key leakage via logs | High | Low residual — keys never passed to logger |
| 4 | T5 — Supply chain (compromised SDK) | Critical | Low residual — pip-audit in CI, pinned deps |

---

## Decision log

| Risk | Decision | Owner | Date |
|---|---|---|---|
| T1/T7 caller must sanitize | Accepted — library is a tool provider, not an application. Document requirement clearly in README. | Library maintainer | 2026-05-07 |
