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
## 2026-05-07T17:45:31Z — documentation draft created and reviewing

- **Branch:** feat/documentation-update
- **Commit:** bcc270e
- **Changed files:**
  - AGENTS.md
  - README.md
  - agent_api/client.py
  - agent_api/config.py
  - agent_api/providers/anthropic.py
  - agent_api/providers/ollama.py
  - agent_api/providers/openai.py
  - agent_api/security.py

---

## 2026-05-07T17:49:05Z — task-end checkpoint

- **Branch:** feat/documentation-update
- **Commit:** bcc270e
- **Changed files:**
  - AGENTS.md
  - docs/planning/CONTEXT_CHECKPOINTS.md
  - docs/planning/DOCUMENTATION_UNKNOWNS.md

---

## 2026-05-07T17:50:15Z — documentation pass complete validation passed

- **Branch:** feat/documentation-update
- **Commit:** bcc270e
- **Changed files:**
  - AGENTS.md
  - docs/planning/CONTEXT_CHECKPOINTS.md
  - docs/planning/DOCUMENTATION_UNKNOWNS.md

---

## 2026-05-07T17:50:33Z — task-end checkpoint

- **Branch:** feat/documentation-update
- **Commit:** bcc270e
- **Changed files:**
  - .claude/skills/integrate-agent-api/SKILL.md
  - .claude/skills/integrate-agent-api/skill.yaml
  - AGENTS.md
  - CHANGELOG.md
  - CONTRIBUTING.md
  - README.md
  - agent_api/client.py
  - agent_api/config.py
  - agent_api/providers/anthropic.py
  - agent_api/providers/ollama.py
  - agent_api/providers/openai.py
  - agent_api/security.py
  - docs/INTEGRATION_GUIDE.md
  - docs/decisions/ADR-001-unified-llm-client.md
  - docs/decisions/ADR-002-prompt-injection-guard.md
  - docs/decisions/ADR-003-backend-priority.md
  - docs/planning/CONTEXT_CHECKPOINTS.md
  - docs/planning/DOCUMENTATION_UNKNOWNS.md
  - docs/planning/PIKE_CLEAN_GATE.md
  - pyproject.toml

---

## 2026-05-07T18:31:34Z — created private GitHub remote for agent-api and pushed feature branch

- **Branch:** feat/documentation-update
- **Commit:** 7d0388b
- **Changed files:**
  - 

---

## 2026-05-07T18:31:41Z — task-end checkpoint

- **Branch:** feat/documentation-update
- **Commit:** 7d0388b
- **Changed files:**
  - docs/planning/CONTEXT_CHECKPOINTS.md

---

