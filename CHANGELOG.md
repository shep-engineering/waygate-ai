# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses Semantic Versioning
for public API changes.

## [Unreleased]

## [0.3.0] - 2026-07-12

### Added

- **Tier-based model router** (`waygate_ai.router`). Callers declare a
  *tier* — `cheap`, `standard`, or `premium` — and the gateway resolves it
  to the cheapest capable model on the active provider:
  `client.call(system, user, tier="cheap")`. Applications no longer name
  models. Every tier is overridable per deployment via
  `LLM_<PROVIDER>_<TIER>_MODEL` (e.g. `LLM_ANTHROPIC_PREMIUM_MODEL`).
- **`MODEL_REGISTRY`** pairs each `(provider, tier)` with a `ModelSpec`
  carrying the model id *and its per-1M-token price*. Routing and pricing
  are now one table, so the model a tier selects and the price it bills at
  cannot drift apart.
- **Cache-aware session pinning** (`waygate_ai.Session`, via
  `client.session(tier=...)`). A session resolves its tier once and holds
  that model for every turn. Provider prompt caches are keyed to the
  model, and a cache read costs roughly a tenth of a fresh input token —
  so switching models mid-conversation discards the cached prefix and
  re-bills it at full price. Route *between* conversations, never *within*
  one.
- `LLMClient.resolve_model()` exposes the model a `(model, tier)` pair
  selects, without making a call.

### Fixed

- **Cost telemetry silently reported `$0.00`.** `estimate_cost()` returned
  `0.0` for any model absent from the price table, which is
  indistinguishable from a model that is genuinely free. Unknown and
  unpriced models now log a warning (once per model id) explaining that
  cost will read as zero. A cost dashboard can no longer show `$0.00` for
  a month of real traffic without saying why.
- **Claude Haiku 4.5 was mispriced** at `$0.80 / $4.00` per 1M tokens; the
  published rate is `$1.00 / $5.00`. Costs on the cheap tier were
  under-reported by ~20%.
- **Current Claude models were missing from the price table** — including
  `claude-opus-4-8` (`$5.00 / $25.00`), so every premium-tier call priced
  at `$0.00`. Added Opus 4.8/4.7/4.6, Sonnet 5, Fable 5, and the dated
  Haiku 4.5 alias. The stale `claude-opus-4` and `gpt-4-turbo` entries
  were removed.
- **Provider detection could disagree with provider dispatch.** Tier
  resolution now runs against the same `detect_backend()` result the
  client dispatches on, so a tier cannot resolve to a model belonging to a
  provider other than the one that gets called. (Consumers that
  reimplemented provider detection to do their own routing had drifted
  from `detect_backend` on both Anthropic-key validation and
  `FORCE_OLLAMA` parsing; routing in the gateway removes the second
  implementation entirely.)
- Mermaid diagrams in `README.md`, `docs/INTEGRATION_GUIDE.md`, and
  `docs/architecture.md` now render correctly. Mermaid 11.x rejected unquoted
  labels containing `()` and unquoted edge labels containing `!=`; both have
  been replaced with quoted-label syntax. Affected pages on the public docs
  site (`/release-readiness/`, `/integration-guide/`, `/architecture/`)
  previously displayed a "Syntax error in text" overlay where the diagrams
  should have rendered.

### Changed

- OpenAI tier models (`gpt-5.4-mini` / `gpt-5.4` / `gpt-5.5`) ship
  **unpriced**: they route correctly but report `$0.00` and log a warning,
  rather than carrying a guessed price. Populate `cost_in` / `cost_out` in
  `waygate_ai.router` from the provider's published pricing to enable cost
  telemetry on the OpenAI path.
- Prices moved from `config._COST_PER_1M` to `waygate_ai.router`.
  `from waygate_ai.config import estimate_cost` still works.

### Documentation

- New **Model Routing** page (`docs/model-routing.md`, in the site nav): the three
  tiers and their per-provider models, why routing carries prices, the
  `LLM_<PROVIDER>_<TIER>_MODEL` override, cache-aware sessions and why you route
  between conversations rather than within one, and how a tier becomes a model.
- `README.md`: routing and cache-aware sessions are now front-and-centre; the
  quick start declares a tier instead of naming a model; "Per-Call Model Override"
  is reframed as an escape hatch; env-var table documents the tier override; the
  architecture diagram shows the router.
- `docs/api-reference.md`: documents `Session`, `call(tier=)`, `resolve_model()`,
  `MODEL_REGISTRY`, `ModelSpec`, `Tier`, `TIERS`, `resolve`, `spec_for`, and
  `estimate_cost`.
- `docs/index.md`, `docs/getting-started.md`, `docs/integration-guide.md`,
  `docs/architecture.md`: examples pass `tier=`; new pitfalls call out naming
  models in application code and routing per-turn inside one conversation.

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

- Public project/package identity established as `waygate-ai`.
- Primary import package set to `waygate_ai`.
- Public base exception established as `WaygateError`.
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
