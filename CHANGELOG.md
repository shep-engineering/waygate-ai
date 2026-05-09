# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses Semantic Versioning
for public API changes.

## [Unreleased]

### Fixed

- Mermaid diagrams in `README.md`, `docs/INTEGRATION_GUIDE.md`, and
  `docs/architecture.md` now render correctly. Mermaid 11.x rejected unquoted
  labels containing `()` and unquoted edge labels containing `!=`; both have
  been replaced with quoted-label syntax. Affected pages on the public docs
  site (`/release-readiness/`, `/integration-guide/`, `/architecture/`)
  previously displayed a "Syntax error in text" overlay where the diagrams
  should have rendered.

## [0.2.0] - 2026-05-08

### Added

- Premium MkDocs Material documentation site for the public Waygate AI launch.
- Trust model documentation that defines what Waygate AI does and does not promise.
- Public release readiness checklist.
- GitHub Pages documentation deployment workflow.
- MIT open-source license.
- Required GitHub tag release workflow documentation for Codex, Claude,
  Windsurf/Cascade, Copilot-style agents, and the Waygate integration skill.

### Changed

- Renamed the public project/package identity from `agent-api` to `waygate-ai`.
- Renamed the primary import package from `agent_api` to `waygate_ai`.
- Removed compatibility shims after updating the only known consumer to import
  `waygate_ai` directly.
- Renamed the public base exception to `WaygateError`.
- Hardened CI: pinned `pip>=26.1` and `setuptools>=78.1.1` in dep-audit, replaced
  the deprecated gitleaks Node action with the native binary, fixed SBOM
  retention to 90 days, suppressed the MkDocs Material upstream warning, and
  updated package license metadata to current SPDX style.

### Security

- Adjusted intentional security-test payload names so the local validator no
  longer flags them as code-execution risks.

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
