---
name: autopilot
description: Run a bounded autonomous delivery workflow from clarified requirements through consensus planning, implementation, code review, and frozen QA execution.
---

# Autopilot

Use this workflow for non-trivial work where the user wants the agent to carry
the task through planning, implementation, review, and QA. Keep the workflow
in the same conversation and current plan document. Use native goal tools for
long-running focus and native subagents only for genuinely independent lanes.

## When to Use

Use for a concrete issue, feature, migration, or refactor that needs:

- requirements clarification;
- consensus planning;
- implementation over multiple steps;
- code review;
- a frozen QA contract executed after implementation.

Do not use for simple edits, explanation-only requests, brainstorming, or a
review-only task.

## Required Phases

Run these phases in order:

```text
deep-interview
  -> plan --consensus
  -> author frozen QA/TDD artifacts
  -> native goal/direct implementation
  -> code-review
  -> qa-execute
```

### 1. Requirements

Use `deep-interview` to resolve intent, scope, non-goals, constraints, and
decision boundaries. Carry its concise requirements summary into the plan.

### 2. Consensus Plan

Use `plan --consensus` to produce the implementation plan and pre-development
QA contract. The plan must identify dependencies, acceptance criteria, changed
areas, risks, and the exact QA manifest or test requirements.

Do not begin implementation while a material planning disagreement or missing
requirement remains unresolved.

Before source implementation, author the TDD tests and freeze the QA artifacts
required by the approved contract. The implementation lane may update them only
through an explicit plan correction justified by new evidence.

### 3. Implementation

- Use `update_plan` to keep phase status and the next bounded step current.
- Use `create_goal` only when the objective genuinely spans multiple turns and
  no conflicting active goal exists.
- Use `get_goal` before resuming and before final completion.
- Use native subagents only for independent file/module/research lanes; keep
  coupled work in the same conversation.
- Implement in small, verifiable increments and run relevant checks as the
  plan requires.

### 4. Code Review

Run `code-review` on the actual diff and fresh evidence. A clean gate requires:

- reviewer recommendation `APPROVE`;
- architectural status `CLEAR`;
- no unresolved critical or high-severity finding.

The review is read-only and does not silently fix its own findings.

### 5. QA Execution

Run `qa-execute` against the frozen manifest created before implementation.
Pass, or explicitly skip only when the manifest's documented condition proves
the change is non-runtime. Do not let the executor redesign tests or inspect
the full implementation context to invent additional checks.

## Return Loop

If code review or QA is not clean:

1. record the exact finding in the current plan;
2. return to the consensus plan phase;
3. update the plan and QA contract only when the evidence requires it;
4. implement the bounded correction;
5. rerun review and QA.

Stop and report a blocker when the same root failure repeats across three
review/QA cycles without meaningful new evidence or when required authority,
credentials, or environment access is missing.

## Stop and Completion

- If the user says stop, stop the active workflow and preserve the current plan
  and evidence; do not delete progress.
- Do not declare completion from idle state, a partial test run, or an
  unverified model summary.
- Completion requires the approved plan, implementation evidence, clean review,
  and passed or explicitly skipped frozen QA evidence.
- If a native goal is active, call `update_goal({status: "complete"})` only
  after this completion audit; otherwise leave it active.

## Completion Summary

Report:

- clarified requirements and decisions;
- plan and changed-file summary;
- implementation and verification evidence;
- code-review verdict;
- QA manifest verdict;
- remaining risks or explicit blockers.
