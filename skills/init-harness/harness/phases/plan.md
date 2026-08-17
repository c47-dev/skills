# Plan

## Purpose

Use this phase after the request is clear enough to proceed.

Plan produces an actionable, evidence-backed execution contract. It does not silently start production implementation.

Plan-phase execution uses the named `plan` skill. Classify scale first, then run `plan` in the mapped mode:

| Scale | `plan` skill mode |
| --- | --- |
| `Small` | `General` |
| `Medium` | `Consensus` |
| `Large` | `Strict` |

This file adds harness-specific contracts the `plan` skill run must satisfy (Control table, artifact rules, TDD-before-Develop). Do not re-implement a second planner beside `plan`.

If the request is ambiguous rather than merely under-planned, ask the minimum blocking questions first. Do not run a full requirements interview inside Plan.

## Required Actions

- identify the target system and primary changed surface
- set `Affected System` to real codebase system names (see Control)
- locate the governing `docs/spec/*` file
- locate the governing `harness/*` file when the change is workflow-only or QA-process-only
- identify secondary specs only if they directly constrain the change
- read the governing contract before implementation decisions
- extract the concrete delivery rules that control correctness
- classify whether API QA, browser UI QA, both, or neither are required
- classify the change as `Small`, `Medium`, or `Large`
- run the `plan` skill in the matching mode: `General`, `Consensus`, or `Strict`
- determine whether one executable phase is sufficient or whether multiple ordered phases are required
- determine the smallest planning artifact that preserves correct execution
- for `Medium` and `Large`, write the TDD document before Develop
- for `Small`, keep planning lightweight; do not require a full TDD document or review ceremony

Planning must not write production / feature implementation code.

## Control Table

Every durable plan document begins with `# <title>` then `## Control` and this table.
Inline `Small` / `Medium` plans use the same fields at the top of the planning output.

| Field | Required content |
| --- | --- |
| Initiative | Short change or feature name shared by related documents |
| Kind | `global`, `phase`, `index`, or `evidence` |
| Phase | `n/a` for global/index/evidence; otherwise `N — title` |
| Scale | `Small` / `Medium` / `Large` |
| Status | `draft` / `active` / `blocked` / `completed` / `superseded` |
| Affected System | Real codebase system name(s), comma-separated |

Rules for `Affected System`:

- use the repository's real system names (spec stem, package, module, or ownership boundary already used in the codebase — e.g. `character`, `llm-model`, `chat`)
- do not invent marketing labels or vague buckets such as `API` / `UI` alone
- if the change introduces a brand-new system with no existing name, stop and confirm the system name with the user before writing Control
- long status narratives, scope lists, dependencies, governing-spec paths, exit criteria, and next actions belong in markdown body sections — not in Control cells

Rules for `Kind`:

- `global` owns initiative-wide phase order, dependencies, aggregate status, and
  cross-phase contracts.
- `phase` owns one independently executable scope and its own acceptance,
  validation, and completion evidence.
- `index` navigates the records in an initiative; it is not an execution or
  product authority document.
- `evidence` reports QA or verification results; it is not an implementation
  plan and must not replace a phase record.
- `index` and `evidence` still use the complete Control table. Their `Phase` is
  `n/a`, and their `Scale`, `Status`, and `Affected System` describe the parent
  initiative or evidence scope.

## Scale ↔ `plan` skill mode

Every change is exactly one scale and therefore exactly one `plan` skill mode:

| Scale | `plan` mode | When | Artifact | Planning rigor |
| --- | --- | --- | --- | --- |
| `Small` | `General` | one primary surface, one ownership boundary, no schema/workflow restructuring, one verification cycle | inline by default; durable only if user asks or workflow authority itself changes | lightweight; brief scope + verification intent; no full TDD document; no dual review |
| `Medium` | `Consensus` | multiple files/subcomponents in a tightly related surface; one or two ownership boundaries; still one phase | single-phase durable record when reasoning must be preserved; otherwise inline with explicit open questions | run `plan` Consensus (Planner → Architect → Critic; Consensus-DR; ADR); TDD document before Develop |
| `Large` | `Strict` | multiple surfaces/boundaries; sequenced schema/API/UI/workflow/migration; later work depends on earlier verified work; or any Strict risk trigger below | one global document + one document per executable phase | run `plan` Strict; TDD document per phase before that phase Develop; never collapse into one undifferentiated plan |

If the change matches two or more `Large` signals, treat it as `Large` / `Strict`.

### Strict risk triggers

Treat as `Large` / `Strict` when any of these apply, even if surface count looks medium:

- authentication or security boundary changes
- database migration or data integrity risk
- destructive or difficult-to-reverse operation
- production incident or external production action
- compliance, PII, or credential handling
- public API or protocol breakage
- multiple subsystem boundaries with independent acceptance tracks
- unclear rollback or materially competing interpretations

Do not run Consensus and Strict serially for the same change. Strict is the high-rigor superset.

## Planning Artifact Rule

- use the smallest planning artifact that preserves correct execution
- do not write a durable planning record unless scale, risk, or workflow authority requires it
- while development is active, a durable implementation record is both the factual execution contract and the progress log
- update an active record when confirmed requirements, phase status, decisions, evidence, or scope change; preserve dated factual changes
- after completion or supersession, the record is historical reference only and must not override `docs/spec/*` or harness authority
- `Large` must not be controlled by one phase-collapsed plan
- each phase document owns its own PRD, design contract, TDD, validation plan, test-and-verify contract, and completion criteria
- the global document owns phase order, dependency, status, and aggregate changelog

## Naming and Location

Durable planning records live only under:

```text
docs/implementation-records/
```

Do not invent an alternate planning directory.

All initiative records stay flat directly under `docs/implementation-records/`.
The filename patterns below apply directly in that directory; do not use role-ambiguous
`README.md`, `00-global.md`, `00-plan.md`, or legacy `P*` filenames for new or
migrated record artifacts.

Filename pattern:

```text
YYMMDD_<initiative-slug>.md                 # Medium single-phase durable record
YYMMDD_<initiative-slug>-global.md          # Large global control document
YYMMDD_<initiative-slug>-phase-N.md         # Large phase document (N starts at 1)
YYMMDD_<initiative-slug>-index.md           # initiative index
YYMMDD_<initiative-slug>-phase-N-qa-report.md # phase QA report
YYMMDD_<initiative-slug>-phase-N-qa-<sequence>.<ext> # phase evidence asset
```

Rules:

- `YYMMDD` is the plan-creation date
- `<initiative-slug>` is lowercase kebab-case and must match across global and phase files for the same initiative
- `N` is a contiguous, one-based phase sequence within one initiative. Legacy
  phase labels remain in body mappings and historical evidence, but are not
  reused as canonical artifact filenames.
- `Small`: default to no durable file (inline in the active context)
- `Medium`: at most one durable file `YYMMDD_<initiative-slug>.md` with Control `Kind=phase`
- `Large`: one `…-global.md` plus one `…-phase-N.md` per executable phase; keep them flat in the same directory
- QA checklists, QA reports, and evidence use the same slug with an explicit suffix, for example `…-phase-1-qa-report.md` — never reuse the plan filename for evidence
- Initiative indexes use `…-index.md` and `Kind=index`; QA reports/evidence use
  their phase suffix and `Kind=evidence`.

Every durable file starts with `# <title>` then `## Control`.

## Mode Procedures

Execute these through the `plan` skill in the mapped mode. Harness still requires the Control / artifact / TDD rules in this file.

### General (`Small`) — `plan` mode `General`

1. Restate target result, constraints, and stop condition.
2. Inspect the repository and relevant conventions.
3. Emit the smallest inline plan: problem, scope in/out, acceptance criteria, brief verification intent.
4. Do not write a full TDD document, Control-heavy durable record, or dual-review plan unless the user asks.
5. Stop after the plan unless the user explicitly requests execution.

Do not invent a heavy plan for a trivial one-file change when direct execution is safer.

### Consensus (`Medium`) — `plan` mode `Consensus`

The main model owns the plan document. Independent roles run sequentially:

1. **Planner** creates the initial plan and Consensus-DR summary.
2. **Architect** reviews with a steelman counterargument, real tradeoff tension, and architectural findings.
3. **Critic** reviews only after Architect completes; checks alternatives, risks, testability, and verification.

Consensus-DR summary must contain:

- 3–5 principles
- top decision drivers
- at least two viable options with bounded pros and cons
- invalidation rationale when only one option remains
- pre-mortem plus expanded unit / integration / e2e / observability coverage for high-risk review

If Critic does not approve, revise and repeat up to five iterations. If still unapproved, stop with the best plan plus unresolved objections. Do not silently execute an unapproved plan.

Final consensus plan must include an ADR:

- Decision
- Drivers
- Alternatives considered
- Why chosen
- Consequences
- Follow-ups

Write the TDD document before Develop.

### Strict (`Large`) — `plan` mode `Strict`

1. Create the global Control + Overview document and the phase map before any phase body is treated as executable.
2. Create one phase document per executable phase with its own Control and full phase body.
3. Apply the complete adversarial verification contract to every acceptance criterion.
4. Prefer independent challenge equivalent to Strict planning rigor; do not weaken to General because a phase looks locally small.
5. Write that phase's TDD document before the phase enters Develop.
6. Do not start a later phase's production code until earlier required exit criteria are explicit.

## Shared Planning Contract

Scale the depth to the mode. `Small` uses only the lightweight General output above.
`Medium` and `Large` must contain the sections below at the correct depth.
Claims about an existing repository must cite concrete files, symbols, commands, or other evidence.
Acceptance criteria must describe observable behavior, not implementation activity alone.

### Body headings for phase documents and durable / Consensus plans

After `## Control`:

1. `## PRD`
   - Problem / requirements summary
   - Goals / desired outcome
   - Non-goals
   - Scope in and scope out
   - Actors / permissions
   - User stories
   - Acceptance criteria that can be tested or observed
   - Assumptions and decision boundaries
   - Why a durable record is or is not needed (`Small` / inline `Medium`)
2. `## Design contract`
   - Component breakdown
   - Ownership boundaries
   - Data flow
   - Technical decisions forced by repo evidence
   - Right-sized implementation steps with file references
   - Failure modes
   - Risks and mitigations
   - Stop or rollback conditions
3. `## TDD` — required for `Medium` / `Large`; see TDD Contract below; not technical architecture. Omit full TDD for `Small`.
4. `## System architecture`
   - Text description
   - Mermaid diagram when useful
   - Browser → API → service → DB flow when applicable
   - Permission flow
   - Read/write ownership
5. `## API contract` — only for affected endpoints
6. `## Database contract` — only for affected collections/tables
7. `## UI contract` — only for affected screens
8. `## Operational concerns`
   - audit, observability, concurrency, retry/idempotency, retention/deletion, performance, security/authz
9. `## Edge cases`
   - missing references, duplicates, stale data, partial failure, malformed payloads, unauthorized access, deletion effects
10. `## Validation plan`
11. `## Test and verify`
    - frozen executor-facing steps derived from TDD; downstream executor must run without reading full plan prose
12. `## Open questions`
    - every unspecified decision; blocking or not; never hide gaps behind "none blocking" without a completeness check
13. `## Completion criteria`
14. `## Phase changelog` — durable phase records only

Omit a surface contract section only when that surface is truly unaffected.
For `Medium` / `Large`, do not omit `## TDD` or acceptance criteria.
For `Small`, keep acceptance criteria; omit full `## TDD` and unused surface contracts.

`Kind=index` and `Kind=evidence` documents use role-specific bodies. They must
retain their navigation or evidence sections, but they do not require PRD,
design, TDD, or implementation completion sections that belong to `global` or
`phase` documents.

### Additional headings for `Large` global documents

After `## Control`:

1. `## Overview`
   - Problem
   - Goals / non-goals
   - Scope in / out
   - Success criteria
2. `## Scale assessment`
   - why `Large` / `Strict`
   - which signals or risk triggers forced decomposition
3. `## Phase map`
   - ordered phases with objective, scope boundary, owner boundary, dependency, exit criteria
4. `## Cross-phase contract`
   - dependency matrix
   - shared data or API contracts
   - sequencing risks
   - rollback boundaries
5. `## Global verification`
   - which verification belongs to each phase
   - initiative-level evidence required before final delivery
6. `## Aggregate changelog`
   - planned / completed / deferred by phase
7. `## Open questions`

### API / Database / UI contract fields

API — for every affected endpoint:

- method and path, purpose, auth
- request schema + example
- success schema + example
- error schema, validation rules, status codes
- side effects, idempotency / conflict behavior

Database — for every affected collection/table:

- name; every field with type, required/optional, default, nullability, unique/index
- read/write source
- migration / normalization / backfill
- rollback and compatibility impact

UI — for every affected screen:

- route, purpose
- visible states: loading / empty / error / ready
- create / edit / delete, save flow, validation feedback, disabled states
- behavior when related API is unavailable

## TDD Contract

Applies to `Medium` and `Large` only. `Small` does not require a full TDD document.

TDD means test design and verification intent, not the full technical approach.

### Required before Develop (`Medium` / `Large`)

The TDD document must be written before Develop starts for that scope.

Complete the verification contract before production implementation. `Consensus` and `Strict` require a complete adversarial contract.

For every acceptance criterion, define:

| Field | Requirement |
| --- | --- |
| `id` | Stable unique test ID |
| proves | Acceptance criterion or requirement ID |
| level | `unit` / `integration` / `api` / `browser` / `computer-use` / `end-to-end` |
| preconditions | Environment, service, fixture, auth, data |
| steps or command | Exact bounded actions |
| expect | Machine-checkable oracle: exit code, status, schema, selector, or checkpoint |
| timeout | Maximum duration |
| cleanup | Process, fixture, data, and temp-artifact cleanup |
| mutation_policy | Usually `read-only`; any allowed mutation named |
| expected_initial_failure | What must fail before production code exists |
| artifact | Test file or fixture path named by the plan |
| evidence | Where result/log will be recorded |
| residual_unknowns | Gaps that remain |

Also cover normal, boundary, malformed, authorization, interruption, failure, rollback, and concurrency scenarios when relevant.

Do not use prose such as "test thoroughly" as a contract. The Test phase must be able to execute against this document without re-deriving acceptance criteria from plan prose.

### Iron Law (`Medium` / `Large`)

No production code without a failing test first for the acceptance slice being implemented.

- RED → GREEN → REFACTOR during Develop against the TDD document written in Plan
- if production code appears before the TDD document exists, stop and write the TDD document first

## Hard Rules

- Do not assume missing requirements.
- Do not compress unknowns into general statements.
- If a detail is not confirmed by repo evidence or user instruction, write it as an open question.
- Do not mark Open Questions as "none blocking" unless every required section was checked.
- Treat the plan as a contract document, not a summary.
- Do not ask the user for facts that repository inspection can establish.
- Do not treat a plan document as Consensus or Strict evidence by itself; the mode procedure must actually run.
- Before finalizing `Medium` / `Large`, audit completeness at the correct level.
- For `Large`, both the global document and every phase document must be internally complete.

## Record Lifecycle

Control `Status` values:

1. `draft` — planning in progress; not yet an execution authority
2. `active` — governs current long-running development and records factual progress, decisions, phase state, and verification evidence
3. `blocked` — cannot proceed until a named blocker is resolved
4. `completed` — historical reference with final evidence; not current product authority
5. `superseded` — preserved earlier reasoning; points at the newer governing spec or record

Reviews and Test-stage activity update an existing `active` record when one already governs the work. They do not create a new record merely to narrate review activity.

## Gate Rule

- `Small`: do not start production edits until scope, constraints, and brief verification intent are explicit in the active context
- `Medium` / `Large`: do not start production edits until the required planning artifacts and TDD document for the current scope exist

## Error Track

- Implementation records are both pre-development reasoning and active progress control during long-term development. Completed records must not become permanent product authority over `docs/spec/*` or harness.
