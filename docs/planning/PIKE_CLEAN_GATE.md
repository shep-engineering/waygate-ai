# Pike/Clean Code Quality Gate

## Purpose

A mandatory quality gate integrated into the RALPH loop's Review phase. It helps
ensure work is measured, verified, and minimal before being accepted.

Based on:

- Rob Pike's 5 Rules for Effective Programming
- Clean Code / SOLID principles
- The Programmer's Oath

## When to Run

- At the Review step of every RALPH loop iteration
- Before any pull request is created or merged
- Before declaring any feature done

## The Gate

### 1. Measure, Do Not Guess

| Check | Question |
|---|---|
| Constants verified | Are magic numbers, conversion factors, and formulas sourced from authoritative references? |
| Realistic test data | Did tests use inputs a real user would provide? |
| No premature optimization | If something was optimized, was the bottleneck measured first? |
| Precision verified | Are display precisions, rounding, and significant figures verified? |

Failure mode this prevents: shipping code with values that only seemed right.

### 2. Simplicity Gate

| Check | Question |
|---|---|
| Simplest approach | Could a simpler algorithm or structure do the same job? |
| No premature abstraction | Are there abstractions with only one implementation? |
| No impossible error handling | Are errors handled at the boundary where they can actually occur? |
| Data structure fits | Does the data model naturally support the operations? |

Failure mode this prevents: over-engineered code that is harder to debug, test,
and maintain.

### 3. Integration Testing

| Check | Question |
|---|---|
| Tested as the user sees it | Did tests cover the workflow the user or caller exercises? |
| Round trip tested | If data transforms or serializes, was the full path tested? |
| Edge cases covered | Were empty, boundary, maximum, and invalid values considered? |
| No mock-only confidence | Is there enough coverage beyond isolated mocks for the risk level? |

Failure mode this prevents: unit tests passing while the integrated feature is
broken.

### 4. Single Responsibility

| Check | Question |
|---|---|
| One reason to change | Does each module or class change for one clear reason? |
| Cohesion | Are related concerns grouped and unrelated concerns separated? |
| Dependencies inward | Does core logic avoid depending on outer frameworks or tools? |

Failure mode this prevents: changes in one area breaking unrelated behavior.

## Integration with RALPH Loop

In the Review phase of RALPH:

```text
Review
- Read CONTEXT_CHECKPOINTS.md.
- Run validate.sh --all and note failures.
- Run this Pike/Clean Code gate.
- Add violations to the Adjust phase as required fixes.
- Check recent git history.
- Identify gaps between intended and actual state.
```

## Integration with CI

```yaml
- name: Quality Gate Documentation
  run: |
    if [ ! -f docs/planning/PIKE_CLEAN_GATE.md ]; then
      echo "Missing Pike/Clean Code quality gate"
      exit 1
    fi
```

## Governance Configuration

```yaml
planning:
  require_pike_clean_gate: true
```
