# Context Loop — Waygate AI

## Purpose

The Context Loop is an iterative refinement protocol for AI-assisted
development. It ensures that each cycle of work builds on the previous
one without losing context.

## Loop Structure

```
┌─────────────────────────────────────────┐
│  1. LOAD CONTEXT                        │
│     - Read CONTEXT_CHECKPOINTS.md       │
│     - Read archetype-orchestrator.yml   │
│     - Run discover.py --scan            │
├─────────────────────────────────────────┤
│  2. UNDERSTAND                          │
│     - What was done last session?       │
│     - What's the current state?         │
│     - What needs to happen next?        │
├─────────────────────────────────────────┤
│  3. PLAN                                │
│     - Break work into small steps       │
│     - Identify which spec applies       │
│     - Set success criteria              │
├─────────────────────────────────────────┤
│  4. EXECUTE                             │
│     - Work incrementally                │
│     - Validate after each step          │
│     - Checkpoint at milestones          │
├─────────────────────────────────────────┤
│  5. CHECKPOINT                          │
│     - Save state to checkpoints file    │
│     - Note what's done and what remains │
│     - Include relevant file paths       │
└─────────────────────────────────────────┘
         │                    ▲
         └────────────────────┘
              Next cycle
```

## Rules

1. Never start work without loading context first
2. Always checkpoint before ending a session
3. Checkpoints must be actionable — not just descriptions
4. Include file paths in checkpoints
5. Note blockers and open questions explicitly

## Waygate AI Context Sources

| Source | Path |
|--------|------|
| Prior checkpoints | `docs/planning/CONTEXT_CHECKPOINTS.md` |
| Project config | `archetype-orchestrator.yml` |
| Public API | `waygate_ai/__init__.py` |
| Client logic | `waygate_ai/client.py` |
| Security guard | `waygate_ai/security.py` |
| Security evidence | `security/evidence/` |
| Discovered specs | `python ../archetype-orchestrator/engine/discover.py --scan` |
