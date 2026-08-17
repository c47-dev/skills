---
name: deep-interview
description: "Intent-first requirements interview with high-value questions before planning or implementation"
---

# Deep Interview

Deep Interview turns an ambiguous request into an execution-ready brief. Its job is
to clarify user intent and decision boundaries, not to make the user provide facts
that the model can discover from the repository or reliable research.

## Use when

- The request is broad, ambiguous, or missing acceptance criteria.
- The user wants to be interviewed, challenged, or prevented from accidental scope drift.
- The next implementation decision depends on user intent, tradeoffs, or non-goals.

## Do not use when

- The request already names the target files, behavior, and acceptance criteria.
- The user explicitly asks for immediate execution.
- The user only wants lightweight brainstorming.

## Core contract

1. Work in the current conversation and current requirements document.
2. Ask only questions whose answers can materially change execution.
3. Ask between one and three questions per interview turn.
4. Never fill the three-question allowance merely for symmetry.
5. Stop early when another question would only polish wording rather than change execution.
6. Stop after at most ten interview turns. If critical uncertainty remains, report it as an unresolved blocker instead of pretending the brief is ready.
7. Do not hand off while a critical non-goal, decision boundary, safety constraint, or acceptance criterion is unresolved.

One interview turn means one assistant question batch followed by the user's answer.
Questions in one batch must be independent. If the answer to Q1 determines Q2, ask Q2
in the next turn.

## Question value gate

Before asking a question, classify it:

| Check | Required result |
| --- | --- |
| Execution impact | The answer could change outcome, scope, architecture, acceptance, safety, or handoff. |
| Uncertainty | The answer is not already established by the current conversation, repository, or research. |
| Decision owner | The answer is a user judgment, preference, business rule, or explicit risk choice. |
| Dependency | The question does not depend on an answer being requested in the same batch. |

Ask the question only when execution impact, uncertainty, and user ownership are all
true. If the information is discoverable, inspect it. If it is merely interesting,
defer it. When several questions qualify, rank them by scope/safety impact, then by
irreversibility, then by how many downstream decisions they unlock.

## Interview document

Maintain one visible working brief in the conversation or in the document the user
has designated. Keep these sections current:

- Objective and intended outcome
- Scope in
- Scope out / non-goals
- Constraints and decision boundaries
- Acceptance and verification criteria
- Facts and evidence
- User decisions
- Open critical questions
- Residual risk and assumptions

Do not create hidden workflow state, a parallel session record, a ledger, or a
runtime-specific artifact directory. A durable file is optional and should be
written only when the user requests a saved brief or a downstream handoff needs one.

## Fact versus judgment

Use these labels in the working brief:

- `[from-code][confirmed]` — directly observed repository fact with no prescription.
- `[from-code][inferred]` — interpretation that still needs user confirmation when it changes behavior.
- `[from-research]` — externally sourced fact, kept separate from a decision.
- `[from-user]` — intent, preference, business rule, scope, non-goal, tradeoff, or acceptance decision.

Never ask the user for a codebase fact that can be inspected directly. Do not convert
an implementation inference into a user decision without showing the evidence and
asking for confirmation.

## Turn procedure

### 1. Preflight

- Restate the requested outcome and the suspected ambiguity.
- Inspect relevant repository context before asking about internals.
- Identify whether the request is greenfield or brownfield.
- Record known facts, assumptions, constraints, and unresolved decisions in the working brief.

### 2. Select the next batch

- Enumerate unresolved issues that could change execution.
- Remove discoverable facts and low-impact preferences.
- Split dependent questions into separate turns.
- Select the highest-value one to three user-owned questions.
- Include concrete repository evidence when asking a confirmation question.

### 3. Pressure-test the answer

After each answer, use the next highest-value move:

1. Request a concrete example or counterexample.
2. Expose the assumption that makes the answer true.
3. Force an explicit boundary or tradeoff.
4. Reframe a symptom toward the underlying outcome.

Do not rotate across dimensions merely for coverage. Stay on a thread while it can
still change the decision, then return to the broader unresolved-issue list.

### 4. Readiness audit

The brief is ready only when:

- objective and desired outcome are explicit;
- scope in and scope out are explicit;
- constraints and decision boundaries are explicit;
- acceptance and verification are testable;
- at least one earlier answer has received an assumption, evidence, or tradeoff pressure pass;
- no remaining question would materially change implementation;
- any residual uncertainty is named with its risk and owner.

## Depth

- `--quick`: use a maximum of four turns for a bounded, low-risk request.
- default: use a maximum of ten turns.
- `--deep`: still use a maximum of ten turns, but apply the pressure pass and readiness audit more rigorously; do not create extra questions for completeness theater.

The ten-turn limit is a ceiling, not a target. A complete brief at turn three should
end at turn three.

## Handoff

When ready, stop interviewing and produce the complete working brief. Recommend the
smallest next lane:

- normal implementation or `plan` for ordinary work;
- `plan --consensus` when independent architectural and critic review is warranted;
- `plan --strict` when the change is large or high-risk.

Do not implement source changes inside Deep Interview. If the user chooses to refine
further, continue from the current brief rather than restarting discovery.

## Terminal outcomes

End with exactly one of:

- `READY` — all readiness gates pass;
- `NEEDS-USER-DECISION` — a user-owned decision is still required;
- `BLOCKED` — a safe answer cannot be inferred or the next action is unauthorized;
- `MAX-TURNS` — ten turns were reached; list unresolved critical items and residual risk.

Original task:
{{ARGUMENTS}}
