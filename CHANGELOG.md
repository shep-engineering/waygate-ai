# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses Semantic Versioning
for public API changes.

## [Unreleased]

### Added

- Premium MkDocs Material documentation site for the public Waygate AI launch.
- Trust model documentation that defines what Waygate AI does and does not promise.
- Public release readiness checklist.
- GitHub Pages documentation deployment workflow.
- Backward-compatible `agent_api` import shim for pre-rename internal consumers.

### Changed

- Renamed the public project/package identity from `agent-api` to `waygate-ai`.
- Renamed the primary import package from `agent_api` to `waygate_ai`.
- Renamed the public base exception to `WaygateError`, with `AgentAPIError` kept
  as a compatibility alias.

## [0.1.0] - 2026-05-07

### Added

- Unified `LLMClient` interface for Anthropic, OpenAI, and local Ollama.
- `LLMResponse` dataclass with text, provider, model, token, cost, latency, and
  retry metadata.
- Environment-based backend detection with deterministic provider priority.
- Prompt-injection guard functions: `sanitize`, `wrap`, `check_response`,
  `is_safe`, and `apply_canary`.
- Provider adapters that map supported SDK failures to the `WaygateError`
  hierarchy.
- Unit tests for client behavior, backend detection, provider adapters, and all
  documented prompt-injection test classes.
- Security evidence, initial SBOM file, and CI security gates.
- Documentation set: README, contributing guide, ADRs, integration guide, agent
  guidance, and Claude integration skill.

### Security

- `DEFAULT_CANARY` is applied by default to `LLMClient` system prompts.
- `scrub_output=True` is the default client behavior.
- Prompt-injection tests cover direct overrides, role hijacking, instruction
  exfiltration, jailbreak markers, structural tags, code execution payloads,
  buried injections, field-specific payloads, Unicode obfuscation, and safe
  passthrough content.
