# Public Release Readiness

Waygate AI is being prepared for a public repository under Shep Engineering. These
items should be complete before a public launch announcement or PyPI release.

## Done

- Public package identity changed to `waygate_ai`.
- Import package changed to `waygate_ai`.
- The previous `agent_api` import path has been removed after updating the only
  known consumer to import `waygate_ai` directly.
- Trust model documented.
- MkDocs Material documentation site added.
- Provider support documented for Anthropic, OpenAI, and Ollama.

## Required Before Public Launch

- Choose and add a `LICENSE` file.
- Decide whether the project is truly open source or source-available.
- Create or transfer the GitHub repository under `shep-engineering`.
- Confirm PyPI ownership for `waygate_ai`.
- Add public project URLs to `pyproject.toml`.
- Review docs for any private-client or internal planning details before
  publishing.
- Decide whether to keep or remove internal planning files from the public repo.

## Required Before PyPI Publish

- Build and inspect source/wheel distributions.
- Verify package metadata with `twine check`.
- Publish first to TestPyPI.
- Install from TestPyPI in a clean environment.
- Tag the release with semver.

## Trust Gate

Do not publish until the project can pass:

```bash
pytest
ruff check .
mkdocs build --strict
```

Any known warning must be documented and explainable.
