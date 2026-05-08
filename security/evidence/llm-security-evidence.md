# LLM Security Evidence Packet

**Project:** limen  
**Release / version:** 0.1.0  
**Prepared by:** Library maintainer  
**Date:** 2026-05-07

---

## 1. Summary

| Property | Value |
|---|---|
| LLM(s) in use | Anthropic Claude, OpenAI GPT, Ollama (local) |
| Prompt surfaces count | 1 (LLMClient.call — system + user args) |
| Sanitization module | `limen.security` |
| Test suite location | `tests/unit/test_security.py` |
| CI gate status | ☑ Pass |
| Overall compliance | ☑ Compliant |

---

## 2. Compliance Attestation

- [x] All user-controlled content reaching an LLM prompt passes through `sanitize()`
      *(caller responsibility; library provides and documents `sanitize()` as required)*
- [x] All user content in prompts is wrapped in `<data>` boundary markers via `wrap()`
- [x] Every system prompt includes the security canary instruction via `DEFAULT_CANARY`
- [x] All LLM output passes through `check_response()` before returning to callers
      (`scrub_output=True` is the default)
- [x] All 10 injection attack classes have automated test coverage in `test_security.py`
- [x] CI fails on injection test failure (pytest job in `security.yml`)
- [x] File-extracted content — N/A for this library (caller handles file extraction)
- [x] `is_safe()` audit hook exists; wired to observability pipeline is caller's responsibility

---

## 3. Prompt Surfaces Inventory

| Surface ID | File / Function | Input source | Sanitized | Wrapped |
|---|---|---|---|---|
| S1 | `limen/client.py` → `LLMClient.call(system, user)` | Caller-supplied `system` string | Caller's responsibility | Caller's responsibility |
| S1 | `limen/client.py` → `LLMClient.call(system, user)` | Caller-supplied `user` string | `sanitize()` provided | `wrap()` provided |

*Note: limen is a library. It provides sanitization tools but cannot enforce caller adoption.
`DEFAULT_CANARY` is applied automatically to every system prompt regardless.*

---

## 4. Sanitization Module

| Property | Value |
|---|---|
| Module location | `limen/security.py` |
| Version / commit | 0.1.0 |
| Injection patterns count | 10 classes (direct override, role hijack, exfiltration, jailbreak, XML, code exec, buried, field-specific, unicode, passthrough regression) |
| XML tags stripped | `<system>`, `<assistant>`, `<human>`, `<user>`, `<data>`, `<instruction>`, `<context>`, `<prompt>` |
| Length caps defined | ☑ Yes — per content type (bullet 400, block 8000, summary 600, etc.) |
| `wrap()` implemented | ☑ |
| `check_response()` implemented | ☑ |
| `is_safe()` implemented | ☑ |

---

## 5. Test Evidence

| Test suite | Location | Tests | Pass | Last run |
|---|---|---|---|---|
| Injection unit tests | `tests/unit/test_security.py` | 10 classes + sanitize + check_response + is_safe + canary | All pass | CI on every PR |
| Integration / E2E | N/A (library) | — | — | — |

**CI run link:** GitHub Actions → `Security Gates` → `Injection Tests (all 10 classes)`

---

## 6. Open Exceptions

| Exception | Risk | Compensating control | Owner | Review date |
|---|---|---|---|---|
| Caller adoption of `sanitize()`/`wrap()` not enforced | Medium | README documents requirement; DEFAULT_CANARY applied automatically | Maintainer | Per release |

---

## 7. Approvals

| Role | Name | Signature | Date |
|---|---|---|---|
| Engineer | Library maintainer | — | 2026-05-07 |
| Security reviewer | — | Pending external review | — |
