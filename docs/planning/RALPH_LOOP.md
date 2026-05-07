# RALPH Loop — agent-api

## Purpose

RALPH is an iterative improvement protocol for multi-session work.

## Acronym

| Step        | Action                                              |
|-------------|-----------------------------------------------------|
| **R**eview  | Assess the current state of the codebase            |
| **A**djust  | Make targeted changes based on the review           |
| **L**earn   | Capture what worked and what didn't                 |
| **P**lan    | Outline what should happen in the next iteration    |
| **H**andoff | Pass complete context to the next session           |

## Protocol

### Review
- Read `docs/planning/CONTEXT_CHECKPOINTS.md`
- Run `python ../my-archetypes/security-guardian/scripts/validate-security-guardian.py --path .` and note failures
- Run `pytest --tb=short -q` and note failures
- Check git log for recent changes
- Identify gaps between intended and actual state

### Adjust
- Fix validation failures
- Address technical debt noted in previous sessions
- Refine implementations based on new understanding
- Keep changes small and focused

### Learn
- What patterns are emerging?
- What mistakes keep recurring?
- What tools/approaches are most effective?
- Document lessons in the checkpoint

### Plan
- What are the next 3–5 concrete steps?
- Which specs/constitutions will be needed?
- Are there blockers or dependencies?
- Set realistic scope for next session

### Handoff
- Write a detailed context checkpoint
- Include:
  - Current branch and commit
  - Files changed and why
  - What's working and what's not
  - Clear next steps with file paths
  - Open questions and decisions needed

## agent-api Checkpoints File

Always update: `docs/planning/CONTEXT_CHECKPOINTS.md`

Key areas to track:
- Public API completeness (`LLMClient`, providers, security tools)
- Injection guard coverage (target: all 10 classes)
- Test coverage (threshold: 80% — enforced in CI)
- Security evidence pack (validator: `OK security-guardian`)
- Documentation completeness (documentation-champion constitution)
