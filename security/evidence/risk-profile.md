# Risk Profile

**Date**: 2026-05-07  
**Review cadence**: Per release or on significant architecture change

## System summary

`waygate_ai` is a Python library that routes LLM calls to Anthropic, OpenAI, and Ollama.
It handles API keys from the environment and passes caller-supplied content to LLMs.
It does not expose a network service, persist data, or manage end-user authentication.

## Risk rating

| Dimension | Rating | Rationale |
|---|---|---|
| Overall | **Medium** | Handles API secrets; prompt injection surface; no auth/network service |
| Confidentiality | Medium | API keys in environment; could be leaked via logs or exceptions if misused |
| Integrity | Medium | Prompt injection could alter LLM behavior in consuming applications |
| Availability | Low | Library; no service to disrupt |

## Verification target

ASVS Level 1. The library itself provides injection defenses but cannot enforce caller adoption.
Consumer applications should target ASVS Level 2 where Waygate AI is in the call path.

## Exceptions and compensating controls

| Area | In Scope | Exception / Notes |
|---|---|---|
| API key handling | Yes | Env-var only, never logged — no exception |
| Prompt injection surface | Yes | `sanitize()`, `wrap()`, canary provided; caller adoption not enforced |
| Network service exposure | No | Library only — out of scope |
| Data persistence | No | Stateless — out of scope |
| End-user auth | No | Caller's responsibility — out of scope |
| Container scanning | N/A | No container image produced — trivy used for dep scanning only |
