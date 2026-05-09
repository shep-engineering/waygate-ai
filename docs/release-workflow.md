# Release Workflow

Waygate AI is distributed from GitHub until the project is explicitly moved to
PyPI. Treat GitHub distribution as a real release channel, not an informal
shortcut.

## Current Distribution Policy

- Use GitHub as the source of truth for releases until PyPI publishing is
  enabled.
- Consume Waygate AI from released Git tags, not floating branches.
- Keep release tags protected where the hosting platform supports it.
- Do not move, delete, or reuse a published release tag.
- Do not publish to PyPI until the release workflow is updated and the user
  explicitly approves PyPI publishing.

## Required Release Steps

1. Decide the semantic version bump:
   - Patch for backward-compatible fixes, documentation, and CI changes.
   - Minor for backward-compatible public API additions.
   - Major for breaking public API changes after `1.0.0`.
2. Update `pyproject.toml`.
3. Update `CHANGELOG.md`.
4. Run local validation:

```bash
python -m pip install -e ".[all,dev]"
pytest --tb=short -q
pytest tests/unit/test_security.py -v --tb=short --no-cov
ruff check .
mkdocs build --strict
bash ../archetype-orchestrator/scripts/validate.sh --all
```

5. Commit the release preparation.
6. Create an immutable semver tag, for example `v0.1.1`.
7. Push the branch and tag.
8. Confirm CI is green before telling consuming projects to update.
9. Update consuming projects to pin the tag.

## Consuming Project Dependency Format

Until PyPI publishing is enabled, consuming projects should depend on a tag:

```text
waygate-ai[all] @ git+ssh://git@github.com/shep-engineering/waygate-ai.git@v0.1.1
```

Use a commit SHA only for temporary emergency testing. Replace it with a semver
tag before merging or deploying the consuming project.

## PyPI Transition

When PyPI publishing is approved, keep the same semver discipline:

- The repository version, changelog, tag, and GitHub Release remain the source
  of truth.
- PyPI receives the built artifact after tests and release gates pass.
- Use PyPI Trusted Publishing from GitHub Actions.
- Never store long-lived PyPI API tokens in repository secrets unless the user
  explicitly approves that fallback.
