# Test

## Purpose

Use this phase after development work is in place.

## Facts

- The named review entrypoint for this phase is `/code-review`. API and Browser QA retain their lane-specific execution surfaces when those lanes are required; this is intentional Test-lane binding, not a general skill-to-phase router.
- Product code must not introduce fallback / defensive duplication. QA lanes use the model routing defined by the governing `AGENTS.md`; if a required model or tool is unavailable, classify that lane as `blocked` without substitution.

## Progressive Disclosure

Read only the depth that applies to the current role and lane. The authority table below defines the lane files.

## Scale Rule

- `Small`: run programmer sanity only. Do not run `/code-review` unless the user explicitly asks.
- `Medium` / `Large`: run the mandatory procedure below for every applicable lane.

## Mandatory Procedure

For `Medium` / `Large`, run these procedures in order. None of them are optional when applicable.

| Step | Procedure | Authority |
| --- | --- | --- |
| 1 | Sanity | `harness/qa-test/sanity.md` |
| 2 | QA checklist refresh | `harness/qa-test/checklist-refresh.md` |
| 3 | API QA | `harness/qa-test/api-qa.md` |
| 4 | Browser UI QA | `harness/qa-test/browser-ui-qa.md` |
| 5 | QA report | `harness/qa-test/qa-report.md` |
| 6 | Fix and retest failed sanity or QA until the QA report passes | `harness/qa-test/retest-loop.md` |
| 7 | Code review | `harness/qa-test/code-review.md` |
| 8 | Fix and retest failed review until review passes | `harness/qa-test/retest-loop.md` |

## Required Actions

- require the programmer or main execution owner to run every applicable repository-provided lint, type-check, build, and unit-test command
- derive or refresh the required QA checklist from the governing spec before invoking the independent QA executor
- construct one bounded QA contract for each required API or Browser UI QA lane; the contract must contain the repository root, lane, exact allowed commands, forbidden operations, completion criteria, and required evidence
- the primary model creates and controls each QA and review conversation directly; keep each lane bounded and evidence-oriented
- start one bounded sub-agent for each required QA lane using the exact model and reasoning effort defined by the governing `AGENTS.md`
- give each QA sub-agent only its repository root, lane, checklist, exact allowed commands, forbidden operations, completion criteria, required evidence, and applicable tool instructions
- use `gpt-5.6-luna` with low reasoning for API QA
- use `google-antigravity/gemini-3.7-flash` with medium reasoning and `browser:control-in-app-browser` for Browser UI QA
- if the required model, browser surface, or other required tool is unavailable, classify the lane as `blocked`; do not silently substitute another model or execution surface
- collect QA evidence from the independent QA executor
- compile one QA report from the returned evidence
- classify each required QA lane as `pass`, `fail`, or `blocked`
- if sanity, a required QA lane, or the QA report fails, complete the fix and retest loop before code review
- run `/code-review` only after sanity and every required QA lane pass, using the exact scope, planning artifact, and passing QA report for the current change
- classify the `/code-review` result as `pass`, `fail`, or `blocked`
- after fixing issues, rerun sanity, every QA lane affected by the fix, rebuild the QA report, and rerun `/code-review` when review applies
- continue until every mandatory test procedure passes or a real blocker exists

## Phase Verification Rule

- verification must close against the planning artifact for the exact scope under test
- for inline `Small` changes, verify against the brief scope and acceptance criteria in the active execution context
- for `Medium` changes with a durable phase record, verify against that record and its TDD document
- for `Large` changes, verify against the current phase document and its TDD document first
- after a `Large` phase passes, write the phase status and returned evidence back into the global planning/implementation document
- do not treat initiative-level verification as complete until every required phase has passed its own verification contract

## Mandatory Rules

- sanity is mandatory for every scale
- for `Medium` / `Large`: programmer sanity and independent QA are cumulative when applicable; neither substitutes for the other
- for `Medium` / `Large`: required API QA / browser UI QA must use the exact model routes in the lane files
- QA report is mandatory whenever any independent QA lane runs
- for `Medium` / `Large`: run the named `/code-review` skill as the single review authority
- for `Small`: do not run `/code-review` unless the user explicitly asks
- none of the required procedures for the current scale are replaceable by self-reasoning

## Required Output

1. programmer sanity commands run: lint, type check, build, and unit tests
2. programmer sanity pass/fail/blocked, including evidence for commands not configured or not runnable
3. API QA required: `yes` / `no`
4. browser UI QA required: `yes` / `no`
5. API QA result
6. browser UI QA result
7. QA report status
8. `/code-review` result
9. returned evidence
10. whether a QA loop was required
11. which boundary failed, if any
12. planning artifact verified
13. current phase status update, if the change is `Large`

## Completion Rule

Test passes only when all applicable mandatory procedures pass with fresh evidence.

Process success is not QA success. The returned evidence must satisfy every checklist item. If `/code-review` is unavailable, classify review as `blocked`; do not invoke a second review authority or claim a passing review.

For a `Large` change, a phase passes only when:

- the current phase verification contract passes with fresh evidence
- the phase status is updated in the global planning/implementation document
- no required lane for that phase remains unresolved

## Error Track

Observed failure patterns:

- repeated QA runs stayed on the same already-passing boundary instead of moving to the first failing boundary
- live runtime mismatches were not checked before editing code
- tool failures were not treated as signals to switch tools or validate the environment

Corrected future behavior:

- if auth fails, verify the active auth client, secret, and environment before editing auth code
- if health checks or service discovery fail, verify the real runtime port or endpoint before changing client configuration
- if create succeeds but the UI state is stale, verify persistence and read-model alignment before rerunning the same create flow
- if a downstream request times out, inspect the first failing downstream boundary instead of rewriting already-proven upstream code
- if a model or external dependency fails, classify it as a downstream runtime failure rather than misattributing it to the browser-facing layer
- if browser QA fails after an earlier step passed, inspect the actual visible state and selector path before assuming an API failure
- programmer sanity checks were previously treated as sufficient validation; keep sanity evidence completely separate from independent QA evidence while requiring both procedures
- review must use `/code-review` as the single review authority; QA executors are evidence-producing test lanes, not review lanes
