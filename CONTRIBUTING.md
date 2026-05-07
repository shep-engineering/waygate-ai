# Contributing

This repository is a Python 3.11 library. Contributions should keep the public
LLM interface small, documented, tested, and routed through `LLMClient`.

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[all,dev]"
```

On Bash-compatible shells, activate with:

```bash
source .venv/bin/activate
```

## Workflow

1. Start from a feature branch such as `feat/documentation-update`.
2. Run the project pre-work gate:

   ```bash
   bash ../archetype-orchestrator/scripts/pre-work-check.sh
   ```

3. Make focused changes with tests or documentation updates that match the
   behavioral surface being changed.
4. Run checks locally before asking for review.
5. Open a pull request to `main` only after CI is green.

## Tests and Linting

```bash
pytest
pytest tests/unit/test_security.py -v
ruff check .
```

`pytest` enforces an 80% coverage threshold through `pyproject.toml`.

## Documentation

- Update `README.md` when setup, configuration, public API, or usage changes.
- Update `CHANGELOG.md` for release-visible changes.
- Add an ADR under `docs/decisions/` for decisions that affect the public API,
  security model, backend selection, or integration contract.
- Record unresolved facts in `docs/planning/DOCUMENTATION_UNKNOWNS.md`.

## Security Rules

- Do not hardcode API keys, passwords, tokens, or credential-bearing connection
  strings.
- Do not log or print API key values.
- Do not call Anthropic or OpenAI SDKs directly from application code; route LLM
  work through `LLMClient`.
- Do not remove or weaken `DEFAULT_CANARY` without updating security evidence.
- Do not add `continue-on-error: true` to CI security jobs.

## Pull Request Checklist

- Public behavior is documented.
- Tests pass locally.
- Security evidence remains untouched unless the change explicitly updates and
  validates it.
- New unknowns are captured in `docs/planning/DOCUMENTATION_UNKNOWNS.md`.
- The post-work and validation gates have been run before the work is declared
  complete.
