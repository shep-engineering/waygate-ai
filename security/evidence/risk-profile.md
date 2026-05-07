# Risk Profile — agent-api

**Risk Classification**: Medium  
**ASVS Target Level**: Level 1 (library, not directly user-facing)  
**Date**: 2026-05-07

## Rationale

- Library handles API keys (secrets) but does not store them
- Library routes user-supplied content to external LLMs — prompt injection surface exists
- No network service exposed; no persistent data storage
- Blast radius limited to the consuming application

## Scope Boundaries

| Area | In Scope | Notes |
|---|---|---|
| API key handling | Yes | Env-var only, never logged |
| Prompt injection surface | Yes | `sanitize()`, `wrap()`, canary provided |
| Network service exposure | No | Library only |
| Data persistence | No | Stateless |
| End-user auth | No | Caller's responsibility |
