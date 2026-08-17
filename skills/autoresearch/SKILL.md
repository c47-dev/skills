---
name: autoresearch
description: "Run a bounded research loop with an explicit validator, evidence-gated completion, and optional native goal tracking"
---

# Autoresearch

Run research when the output is a bounded deliverable that must satisfy an explicit
validator. Use the current conversation as the working context. A normal repository
document may be written only at a user-approved path or when the research output is
itself a requested deliverable.

## Boundary with best-practice research

Use `best-practice-research` for a bounded source-backed answer or planning lookup.
Use `autoresearch` only when the research output must be iterated against a declared
validator, critic rubric, benchmark, schema, or other completion contract.

Research evidence is input to planning. It is not a final architecture or component
decision unless the user explicitly makes that the requested deliverable.

## Core contract

Before the first research iteration, define:

- mission and bounded question;
- required output artifact or answer shape;
- evidence and source-quality rules;
- exactly one completion validator;
- iteration limit and same-failure stop condition;
- safety, credential, network, and write boundaries.

Do not stop because the model says “done”, because a turn made no progress, or because
one partial validator run looked positive.

Use a maximum of five iterations by default. Stop earlier after the same blocking
failure occurs three times. Record every iteration's evidence and validator result in
the visible working document or requested artifact.

## Validation modes

Choose one mode before research begins:

### Validator command

Use an exact `exec_command` command or project-native checker. Define its input,
success exit code, required output markers, failure markers, timeout, and cleanup.
The command result is authoritative over positive prose.

### Critic review

Use a native sub-agent for an explicitly independent critic role when available. The
critic receives the mission, rubric, and research artifact, not hidden runtime state.
Run the researcher and critic sequentially; do not claim independence when the same
model performs both passes. The critic must return `PASS`, `FAIL`, or `BLOCKED` with
evidence against each rubric item.

### Goal tracking

Use goal tools only when the user explicitly requests long-running goal tracking:

- call `get_goal` during intake when an active goal may exist;
- call `create_goal` only when no active goal exists and the objective is explicit;
- never replace a different active goal;
- call `update_goal({status: "complete"})` only after the research artifact and
  validator pass their final audit;
- call `get_goal` again after completion for a fresh snapshot.

Goal tracking is optional thread-level accounting. It does not create a research
ledger, a second session, or a separate source of truth.

## Workflow

1. Restate the mission, output, validator, safety bounds, and stop condition.
2. Inspect relevant repository facts with `rg` and `exec_command`.
3. Gather external evidence with `web__run` when current or upstream facts matter.
4. Produce a first bounded research artifact with citations and evidence labels.
5. Run the selected validator exactly as declared.
6. If the validator fails, classify the failure as evidence gap, reasoning error,
   artifact defect, environment blocker, or validator defect. Revise only within the
   declared scope and iteration limit.
7. Repeat validation after every material revision.
8. Run a completion audit mapping every mission requirement to evidence and a passing
   validator result.
9. Emit the final artifact, residual risks, and any carried-forward blocker.

Do not invoke external advisor CLIs. Do not use hidden hooks, automatic nudges, a
detached process, or a runtime-specific state directory.

## Completion artifact

The final result must contain:

```json
{
  "status": "passed",
  "passed": true,
  "mission": "<bounded mission>",
  "validator": "<command or critic rubric>",
  "evidence": ["<source, file, command, or artifact reference>"],
  "output_artifact_path": "<normal user-approved path or null>",
  "iterations": 1,
  "residual_risks": []
}
```

The result is incomplete when the validator is absent, failed, blocked, unverifiable,
or inconsistent with the final artifact.

## Terminal outcomes

- `COMPLETE` — final artifact and validator evidence pass;
- `BLOCKED` — required evidence, authority, dependency, or safe execution is unavailable;
- `MAX-ITERATIONS` — the bounded loop ended with explicit failures and residual risk;
- `VALIDATOR-INVALID` — the declared validator cannot measure the mission reliably.

Research task:
{{ARGUMENTS}}
