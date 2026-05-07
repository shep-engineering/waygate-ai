# Context Checkpoints — agent-api

## Purpose

Running log of session milestones. Each entry captures what was done,
what changed, and what comes next. Always read this at session start.

---

## [2026-05-07] — Initial Security Compliance + Docs Planning

**Branch**: `feat/apply-updated-archetypes`  
**Who**: Windsurf (Cascade)

### What was done

1. Applied updated security archetypes from `F:\my-archetypes`:
   - Restructured all 5 `security/evidence/` files to match `security-guardian` validator headings
   - Created `security/evidence/secure-by-default-checklist.md`
   - Created `security/evidence/security-metrics.md`
   - Created `security/sbom/` with CycloneDX placeholder
   - Added `trivy` + `sbom` (CycloneDX) jobs to `.github/workflows/security.yml`
   - Created `security/evidence/llm-security-evidence.md` (prompt-injection-guard)
   - Created `security/evidence/prompt-guard-checklist.md` (prompt-injection-guard)
   - Fixed `validate-security-guardian.py` to accept Python-stack tools (pip-audit, gitleaks)
   - Validator: `OK security-guardian` (exit 0)
2. Created `docs/planning/` with standard AO planning files

### Current project state

- **Core library**: Complete — `LLMClient`, 3 providers (Anthropic, OpenAI, Ollama), injection guard, retry/backoff, cost logging
- **Security evidence**: Complete — validator passes
- **Documentation**: **IN PROGRESS** — brief at `docs/planning/DOCUMENTATION_IMPLEMENTATION_BRIEF.md`
- **Tests**: `tests/unit/` — 4 test files covering client, config, providers, security (all 10 injection classes)
- **CI**: `.github/workflows/security.yml` — dep-audit, secret-scan, injection-tests, trivy, sbom, unit-tests

### Next steps

1. Implement documentation plan (`docs/planning/DOCUMENTATION_IMPLEMENTATION_BRIEF.md`):
   - Replace `README.md` with full documentation-champion-compliant version
   - Create `CHANGELOG.md`
   - Create `CONTRIBUTING.md`
   - Create 3 ADRs in `docs/decisions/`
   - Create `AGENTS.md`
   - Create `docs/INTEGRATION_GUIDE.md`
   - Create `.claude/skills/integrate-agent-api/SKILL.md` + `skill.yaml`
2. Commit all documentation on `feat/apply-updated-archetypes`
3. Open PR to `main`

### Open questions

- Should `agent-api` be published to PyPI eventually, or remain a local library?
- Async (`asyncio`) client support — planned for a future version?
- Streaming response support needed?

---

<!-- Add new checkpoints above this line -->
