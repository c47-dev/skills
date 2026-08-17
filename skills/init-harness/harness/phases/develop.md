# Develop

## Purpose

Use this phase only after Plan is complete and its gate rules are satisfied.

## Authority

Planning shape, Control table, scale/mode, and TDD-document rules are defined only in `harness/phases/plan.md`. Do not restate them here.

## Required Actions

- confirm the Plan gate for the current scale has passed
- for `Medium` / `Large`, confirm the TDD document for the current scope exists before production edits
- update the governing spec first when contract changes
- make production code changes grouped by ownership boundary
- keep unrelated boundaries out of the same patch
- own coupled execution in the main model; use native tools or subagents only for explicitly independent lanes
- for `Medium` / `Large`, implement against the TDD document (RED → GREEN → REFACTOR)
- keep the same task open until the requested scope is finished
- for `Large` work, execute only the current phase scope unless the governing plan allows parallel independent phases

## Stop Conditions

- planning artifacts required by `harness/phases/plan.md` are missing for the current scale
- `Medium` / `Large` production code would start without a TDD document for the current scope

## Required Output

1. changed files
2. changed boundaries
3. execution owner, with any independent native lanes named
4. development status
5. planning artifact used: `inline` / `phase record` / `global + phase`
6. current phase when `Large`
7. for `Medium` / `Large`, pointer to the TDD document used
