# GitHub Copilot: Archetype Orchestrator Instructions
# limen Project

## Mandatory Session-Start Sequence

Every session MUST begin with:
1. Read `docs/planning/CONTEXT_CHECKPOINTS.md`
2. Run: `python ../archetype-orchestrator/engine/discover.py --scan`
3. Verify current branch is NOT main/master/develop

## Absolute Rules

- NEVER commit directly to main, master, or develop
- NEVER hardcode secrets, API keys, passwords, or tokens in source code
- NEVER use `eval()` or `exec()` with user-supplied input
- NEVER call provider SDKs directly — all LLM calls go through `LLMClient`
- NEVER remove or weaken `DEFAULT_CANARY` without updating `security/evidence/`
- NEVER log or print API key values
- ALWAYS run `pre-work-check.sh` before starting any task
- ALWAYS run `post-work-check.sh` before declaring a task complete
- ALWAYS run `validate.sh --all` before committing

## Task Lifecycle

```bash
bash ../archetype-orchestrator/scripts/pre-work-check.sh
python ../archetype-orchestrator/engine/discover.py --query "describe your task"
# ... work on feature branch only ...
bash ../archetype-orchestrator/scripts/context-checkpoint.sh "milestone"
bash ../archetype-orchestrator/scripts/post-work-check.sh
```

## Available Archetypes (../my-archetypes)

| Archetype | Best For |
|-----------|----------|
| `security-guardian` | Security reviews, threat modeling, SDLC gates |
| `prompt-injection-guard` | Prompt injection defense, LLM input/output sanitization |
| `code-quality` | Refactoring, complexity reduction, clean code |
| `debug-detective` | Root-cause debugging, fix validation |
| `documentation-champion` | API docs, README, ADRs, changelog |
| `owasp-devguide` | OWASP security controls |
| `semver` | Version management, releases |

## limen Stack

- **Type**: Python 3.11 standalone library — no server, no frontend, no database
- **Public API**: `limen/__init__.py`
- **Providers**: Anthropic Claude, OpenAI, Ollama
- **Security guard**: `limen/security.py`
- **Tests**: `pytest tests/unit/` — 80% coverage threshold enforced
- **Pending**: Full documentation — see `docs/planning/DOCUMENTATION_IMPLEMENTATION_BRIEF.md`
