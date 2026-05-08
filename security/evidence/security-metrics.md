# Security Metrics

**Project**: Waygate AI  
**Date**: 2026-05-07

---

## Goals

1. Zero unresolved Critical/High dependency vulnerabilities at time of release.
2. 100% of all 10 injection attack classes covered by automated tests.
3. CI security gates fail-closed on every PR — no bypasses.
4. SBOM produced and stored for every release.

## Metrics

| Metric | Target | Current | Trend |
|---|---|---|---|
| Open Critical/High CVEs | 0 | 0 | — |
| Injection test class coverage | 10 / 10 | 10 / 10 | Stable |
| CI security gate pass rate | 100% | 100% | Stable |
| Secret scan findings | 0 | 0 | — |
| Mean time to remediate Critical | ≤ 24h | N/A (no incidents) | — |
| Mean time to remediate High | ≤ 7 days | N/A (no incidents) | — |
| SBOM present for latest release | Yes | Pending first release | — |
| `continue-on-error` in security CI | 0 | 0 | Stable |

## Reporting cadence

- **Per PR**: CI security gates results visible in GitHub Checks
- **Per release**: SBOM generated and committed to `security/sbom/`; pip-audit report reviewed
- **Monthly**: Maintainer reviews open GitHub Issues with `security` label
- **Annually**: Full security evidence pack reviewed and updated
