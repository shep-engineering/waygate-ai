# Secure-by-Default Checklist

**Project**: limen  
**Date**: 2026-05-07  
**Reviewer**: Library maintainer

---

## Identity and access

| Check | Status | Notes |
|---|---|---|
| No unauthenticated network services exposed | ✅ Met | Library only — no network service |
| Least-privilege credentials used | ✅ Met | API keys scoped by provider; read from env only |
| No shared credentials between services | ✅ Met | Each provider key is independent |
| Authorization boundaries documented | ✅ Met | Documented in threat-model.md §Assets |

## Secrets

| Check | Status | Notes |
|---|---|---|
| No secrets hardcoded in source | ✅ Met | All keys from env vars only |
| `.env` and `*.env` in `.gitignore` | ✅ Met | Verified in `.gitignore` |
| Secrets not logged | ✅ Met | `_log()` never includes key values |
| Secrets not in exception messages | ✅ Met | Provider exceptions caught and re-raised as `LimenError` |
| CI secret scanning enabled | ✅ Met | gitleaks on every PR |

## Data protection

| Check | Status | Notes |
|---|---|---|
| PII not logged by default | ✅ Met | Library logs tokens/model/provider only |
| Data classification documented | ✅ Met | threat-model.md §Assets |
| Sensitive fields redacted in logs | ✅ Met | No user prompt content in logs |
| No data stored persistently | ✅ Met | Stateless library |

## Network exposure

| Check | Status | Notes |
|---|---|---|
| No network service bound to 0.0.0.0 | ✅ Met | Library, no server |
| External API calls use HTTPS | ✅ Met | Anthropic/OpenAI SDKs enforce TLS; Ollama localhost |
| No unvalidated redirects | ✅ Met | No HTTP redirect handling |

## Logging and telemetry

| Check | Status | Notes |
|---|---|---|
| Log level appropriate for environment | ✅ Met | DEBUG only when enabled by caller |
| No sensitive data in log messages | ✅ Met | Keys and prompt content excluded |
| Log output configurable | ✅ Met | Caller controls log level via standard Python logging |

## Supply chain

| Check | Status | Notes |
|---|---|---|
| Dependencies pinned in lock file | ✅ Met | `pyproject.toml` optional-deps with versions |
| Dependency vulnerability scan in CI | ✅ Met | pip-audit on every PR |
| SBOM generated per release | ✅ Met | CycloneDX via CI |
| No dev dependencies in production install | ✅ Met | Dev extras (`[dev]`) separate from runtime |

## Infrastructure and CI/CD

| Check | Status | Notes |
|---|---|---|
| Security workflow exists | ✅ Met | `.github/workflows/security.yml` |
| CI security gates fail-closed | ✅ Met | No `continue-on-error: true` |
| Secret scanning in CI | ✅ Met | gitleaks |
| Dependency audit in CI | ✅ Met | pip-audit |
| Vulnerability scan in CI | ✅ Met | trivy |
| Protected branches configured | ✅ Met | `main` protected per `archetype-orchestrator.yml` |
