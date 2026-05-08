# Security Test Matrix

## Scope

`limen` v0.1.0 — Python LLM client library.
Test owner: Library maintainer.
Coverage target: All 10 injection classes + API key safety + supply chain.

## Test categories

| Category | Test Location | When | Owner |
|---|---|---|---|
| Injection Class 1–10 | `tests/unit/test_security.py` | Every PR + push | Maintainer |
| `sanitize()` length caps | `tests/unit/test_security.py::TestSanitizeLengthCaps` | Every PR | Maintainer |
| `check_response()` scrubbing | `tests/unit/test_security.py::TestCheckResponse` | Every PR | Maintainer |
| `is_safe()` audit hook | `tests/unit/test_security.py::TestIsSafe` | Every PR | Maintainer |
| Canary application | `tests/unit/test_client.py::TestCanaryInjection` | Every PR | Maintainer |
| API key not logged | `tests/unit/test_client.py` | Every PR | Maintainer |
| Dependency vulnerability scan | `pip-audit` via CI | Every PR + nightly | CI |
| Secret scanning | `gitleaks` via CI | Every PR + push | CI |
| SBOM generation | `cyclonedx-bom` via CI | Every release | CI |
| Trivy dependency scan | `trivy` via CI | Every PR | CI |

## Evidence

| Evidence type | Location | Retained |
|---|---|---|
| pytest injection test results | CI run logs (GitHub Actions) | 90 days |
| pip-audit report | CI run logs | 90 days |
| gitleaks report | CI run logs | 90 days |
| SBOM (CycloneDX JSON) | `security/sbom/` | Indefinite (per release) |
| trivy scan report | CI run logs | 90 days |
