# Security Test Matrix — agent-api

| Category | Test Location | When | Evidence |
|---|---|---|---|
| Injection Class 1–10 (prompt injection) | `tests/unit/test_security.py` | Every PR + push | pytest output |
| `sanitize()` length caps | `tests/unit/test_security.py::TestSanitizeLengthCaps` | Every PR | pytest output |
| `check_response()` scrubbing | `tests/unit/test_security.py::TestCheckResponse` | Every PR | pytest output |
| `is_safe()` audit hook | `tests/unit/test_security.py::TestIsSafe` | Every PR | pytest output |
| Canary application | `tests/unit/test_client.py::TestCanaryInjection` | Every PR | pytest output |
| API key not logged | `tests/unit/test_client.py` | Every PR | pytest output |
| Dependency vulnerability scan | `pip-audit` via CI | Every PR + nightly | `pip-audit` report |
| Secret scanning | `gitleaks` via CI | Every PR + push | gitleaks report |
