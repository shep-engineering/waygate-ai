# Agents / Codex: Archetype Orchestrator Behavioral Contract
# agent-api Project

## Mandatory Session-Start Sequence

Every session MUST begin with these steps in order:

1. **MANDATORY: Search open-brain at the START of EVERY task. No exceptions.** Do this BEFORE your first action. Run two searches: one for the task topic, one for "user preferences formatting rules". This applies to every task: coding, debugging, docs, research, refactoring, reviews, questions. Every task. Period.
2. Read `docs/planning/CONTEXT_CHECKPOINTS.md`
3. `python ../archetype-orchestrator/engine/discover.py --scan`
4. `git rev-parse --abbrev-ref HEAD` — must be on a feature branch

## Absolute Prohibitions

- NEVER commit directly to `main`, `master`, or `develop`
- NEVER hardcode API keys, passwords, tokens, or connection strings with credentials
- NEVER use `eval()` or `exec()` with user-supplied data
- NEVER call provider SDKs (anthropic, openai) directly — always go through `LLMClient`
- NEVER remove or weaken `DEFAULT_CANARY` without updating `security/evidence/`
- NEVER log or print API key values — not even partial keys
- NEVER add `continue-on-error: true` to any CI security job
- NEVER skip pre-work or post-work gates

## Required Task Lifecycle

```bash
# Before every task
bash ../archetype-orchestrator/scripts/pre-work-check.sh

# Route to matching archetype
python ../archetype-orchestrator/engine/discover.py --query "task description"

# Checkpoint at meaningful milestones
bash ../archetype-orchestrator/scripts/context-checkpoint.sh "milestone description"

# Before declaring done
bash ../archetype-orchestrator/scripts/post-work-check.sh

# Validate all changes
bash ../archetype-orchestrator/scripts/validate.sh --all
```

## Discovered Archetypes (../my-archetypes)

| Archetype | Keywords |
|-----------|----------|
| security-guardian | security, devsecops, governance, compliance, risk |
| prompt-injection-guard | prompt injection, LLM security, sanitization |
| code-quality | clean-code, maintainability, refactoring, complexity |
| debug-detective | debugging, root-cause-analysis, regression, bug-fixing |
| documentation-champion | documentation, api-docs, readme, adr, changelog |
| owasp-devguide | OWASP, security guidelines |
| semver | semantic versioning, releases |

## Project Context

- **Root**: `F:\agent-api`
- **Library**: `agent_api/` — Python 3.11 standalone LLM client library
- **Public API**: `agent_api/__init__.py`
- **Client**: `agent_api/client.py` — `LLMClient`, `LLMResponse`
- **Security guard**: `agent_api/security.py` — `sanitize`, `wrap`, `check_response`, `is_safe`, `apply_canary`
- **Config**: `agent_api/config.py` — `detect_backend()`, cost estimation, defaults
- **Exceptions**: `agent_api/exceptions.py` — `AgentAPIError` hierarchy
- **Providers**: `agent_api/providers/` — anthropic, openai, ollama
- **Tests**: `tests/unit/` — pytest, 80% coverage threshold
- **Security evidence**: `security/evidence/` — do not modify without running validator
- **Pending task**: Full documentation — see `docs/planning/DOCUMENTATION_IMPLEMENTATION_BRIEF.md`
