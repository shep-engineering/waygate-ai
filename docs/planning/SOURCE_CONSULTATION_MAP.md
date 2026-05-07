# Source Consultation Map — agent-api

## Purpose

This map defines authoritative sources for different topics,
preventing hallucination and ensuring accurate information.

## How to Use

Before answering a domain-specific question or making a decision:

1. Check this map for the relevant topic
2. Consult the listed source
3. Cite the source in your response

## Map

| Topic | Authoritative Source |
|-------|----------------------|
| Project configuration | `archetype-orchestrator.yml` in project root |
| Spec/archetype rules | The spec's `*-constitution.md` file in `F:\my-archetypes\` |
| Validation rules | `F:\my-archetypes\security-guardian\scripts\validate-security-guardian.py` |
| Discovered specs | `python ../archetype-orchestrator/engine/discover.py --scan` |
| Context history | `docs/planning/CONTEXT_CHECKPOINTS.md` |
| Public API exports | `agent_api/__init__.py` |
| LLMClient + LLMResponse | `agent_api/client.py` |
| Backend detection + cost | `agent_api/config.py` |
| Injection guard functions | `agent_api/security.py` |
| Exception hierarchy | `agent_api/exceptions.py` |
| Anthropic provider | `agent_api/providers/anthropic.py` |
| OpenAI provider | `agent_api/providers/openai.py` |
| Ollama provider | `agent_api/providers/ollama.py` |
| Install / dependencies | `pyproject.toml` |
| Security evidence | `security/evidence/` |
| SBOM | `security/sbom/` |
| CI gates | `.github/workflows/security.yml` |
| Security rules | `F:\my-archetypes\security-guardian\security-guardian-constitution.md` |
| Injection guard rules | `F:\my-archetypes\prompt-injection-guard\prompt-injection-guard-constitution.md` |
| Documentation rules | `F:\my-archetypes\documentation-champion\documentation-champion-constitution.md` |
| Agentic skill security | `F:\my-archetypes\agentic-skill-security\agentic-skill-security-constitution.md` |
| Environment variables | `README.md` §Environment Variables (or `.env.example` when created) |
| Test suite | `tests/unit/` |

## Rules

1. Never fabricate information about project structure
2. Always run discovery before assuming what specs exist
3. Cite file paths when referencing project-specific information
4. If a source is unavailable, say so — don't guess
