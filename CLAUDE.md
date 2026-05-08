# Claude: Archetype Orchestrator Behavioral Contract
# Waygate AI Project

## Mandatory Session-Start Sequence

Every session MUST begin with these steps in order:

1. **MANDATORY: Search open-brain at the START of EVERY task. No exceptions.** Do this BEFORE your first action. Run two searches: one for the task topic, one for "user preferences formatting rules". This applies to every task: coding, debugging, docs, research, refactoring, reviews, questions. Every task. Period.
2. Read `docs/planning/CONTEXT_CHECKPOINTS.md` (prior session state)
3. Run discovery: `python ../archetype-orchestrator/engine/discover.py --scan`
4. Check branch: `git rev-parse --abbrev-ref HEAD`
5. If on protected branch (main/master/develop), create a feature branch first

## Non-Negotiable Rules

- **Never commit directly to main, master, or develop**
- **Never hardcode secrets, API keys, passwords, or tokens**
- **Never use `eval()` or `exec()` with user-supplied input**
- **Never call provider SDKs directly — all LLM calls go through `LLMClient`**
- **Never remove or weaken `DEFAULT_CANARY` without updating `security/evidence/`**
- **Never log or print API key values**
- **Never add `continue-on-error: true` to any CI security job**
- **Always run validation before declaring a task complete**
- **Always create a task-start marker before work begins**
- **Always create a task-end marker when work completes**

## Task Lifecycle (Required for Every Task)

```bash
# 1. Pre-work gate
bash ../archetype-orchestrator/scripts/pre-work-check.sh

# 2. Discover specs
python ../archetype-orchestrator/engine/discover.py --scan

# 3. Route to matching spec
python ../archetype-orchestrator/engine/discover.py --query "describe your task"

# 4. Work on feature branch only

# 5. Checkpoint at milestones
bash ../archetype-orchestrator/scripts/context-checkpoint.sh "milestone description"

# 6. Post-work gate
bash ../archetype-orchestrator/scripts/post-work-check.sh

# 7. Validation
bash ../archetype-orchestrator/scripts/validate.sh --all
```

## Discovered Archetypes (../my-archetypes)

| Archetype | Domain |
|-----------|--------|
| `security-guardian` | Security guardrails, SDLC gates, threat modeling |
| `prompt-injection-guard` | Prompt injection defense, LLM input/output sanitization |
| `code-quality` | Readability, maintainability, complexity, clean code |
| `debug-detective` | Root-cause debugging, regression tests |
| `documentation-champion` | API docs, README, ADRs, changelog |
| `owasp-devguide` | OWASP security controls |
| `semver` | Version management, releases |

## Project Stack

- **Language**: Python 3.11
- **Type**: Standalone library (no server, no frontend, no database)
- **Providers supported**: Anthropic Claude, OpenAI, Ollama (local)
- **Install extras**: `[anthropic]`, `[openai]`, `[all]`, `[dev]`
- **Tests**: `pytest` — `tests/unit/` — 80% coverage threshold enforced in CI
- **Linting**: `ruff`

## Key Invariants

- `sanitize()`, `wrap()`, `check_response()`, `is_safe()`, `apply_canary()` are pure functions — no side effects
- `scrub_output=True` on `LLMClient` by default — never disable without justification
- Backend detection priority: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY` → `OLLAMA_MODEL` → `ConfigError`
- This priority order must not change without an ADR in `docs/decisions/`
- Security evidence in `security/evidence/` must remain validator-passing at all times

## Pending Work

Full documentation task: see `docs/planning/DOCUMENTATION_IMPLEMENTATION_BRIEF.md`

## Validation Command

```bash
bash ../archetype-orchestrator/scripts/validate.sh --all
```

## Open Brain Memory

Use the `open-brain` MCP server to:
- Retrieve prior context at session start
- Store decisions, bugs fixed, and milestones at session end
- Always pass `source: "windsurf"` (or your agent name) on capture calls
