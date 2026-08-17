---
name: init-harness
description: "Centralized workflow harness. Use only when the user mentions harness."
---

# Init Harness

## Purpose

Load this skill only when the user mentions harness.

This entry is the workflow execution router. Phase contracts, planning shape, TDD, and QA rules live under `harness/` and are not restated here.

## Facts

- Plan requires the named `plan` skill. Scale maps to mode: `Small`→`General`, `Medium`→`Consensus`, `Large`→`Strict`.
- Develop does not require a named skill.
- Test uses the named `/code-review` skill as its review entrypoint. API and Browser QA may retain their lane-specific execution surfaces when those lanes are required; those bindings do not add a second review authority.
- Those named bindings are intentional phase facts, not a general skill-to-phase router for every imported skill.
- Product code must not introduce fallback / defensive duplication. Skill-execution failover is a different layer and is allowed only where the applicable QA phase file explicitly defines it; it must not create a second review lane.
- `Small` is lightweight: no full TDD document and no dual review unless the user asks.
- `Medium` / `Large`: the TDD document must exist before Develop.

## Execution Rules

| Phase | Entrypoint |
| --- | --- |
| Plan | `harness/phases/plan.md` |
| Develop | `harness/phases/develop.md` |
| Test | `harness/phases/test.md` |
| Improve | `harness/phases/improve.md` |

1. Scale / mode / Control table / body headings / TDD rules are defined only in `harness/phases/plan.md`. Plan-phase execution runs through the `plan` skill in the mapped mode.
2. Other imported skills remain optional capabilities under a phase contract. Do not invent bindings beyond the facts above.

## Resources

- `harness/`: sole workflow authority
