# Roadmap — agent-api

## Current State

**Version**: 0.1.0 (unreleased)  
**Branch**: `feat/apply-updated-archetypes`

### What's complete
- `LLMClient` unified interface (Anthropic, OpenAI, Ollama)
- Auto-backend detection from environment variables
- Exponential backoff retry (configurable)
- Cost/token logging per call
- Per-call model override
- Prompt injection guard: `sanitize`, `wrap`, `check_response`, `is_safe`, `apply_canary`, `DEFAULT_CANARY`
- Full security evidence pack (security-guardian validator passes)
- CI: dep-audit, secret-scan, injection-tests, trivy, SBOM generation, unit tests

### What's in progress
- Full documentation (documentation-champion): README, CHANGELOG, ADRs, AGENTS.md, INTEGRATION_GUIDE, SKILL

---

## v0.1.0 — Baseline Release

**Target**: Next PR merge to `main`

- [ ] Complete documentation plan (`C:\Users\DAVE\.windsurf\plans\agent-api-docs-61c733.md`)
- [ ] `README.md` — full rewrite with Mermaid diagrams
- [ ] `CHANGELOG.md` — v0.1.0 initial entry
- [ ] `CONTRIBUTING.md`
- [ ] 3 ADRs in `docs/decisions/`
- [ ] `AGENTS.md`
- [ ] `docs/INTEGRATION_GUIDE.md`
- [ ] `.claude/skills/integrate-agent-api/` (SKILL.md + skill.yaml)

---

## v0.2.0 — Async Support

- Async `LLMClient` variant (`AsyncLLMClient`) using `httpx` / async SDKs
- Backward-compatible — sync client unchanged
- New optional extra: `pip install agent-api[async]`

---

## v0.3.0 — Streaming

- `LLMClient.stream(system, user)` → async generator of text chunks
- Support: Anthropic (SSE), OpenAI (SSE), Ollama (streaming)
- `LLMResponse` extended with `is_streamed: bool`

---

## v0.4.0 — Extended Provider Support

- Azure OpenAI endpoint support (`AZURE_OPENAI_*` env vars)
- Google Gemini provider
- Provider-agnostic model alias table (`"fast"`, `"smart"`, `"local"`)

