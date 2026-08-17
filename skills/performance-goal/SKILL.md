---
name: performance-goal
description: Run an evaluator-gated performance optimization workflow. Use when performance work needs a measurable baseline, an explicit benchmark contract, small reversible changes, and evidence-based completion rather than a one-off review.
---

# Performance Goal

Use a measurable evaluator as the authority for performance work. Keep the
optimization loop in the current conversation, active plan, and native goal
tools; do not create hidden workflow state.

## Contract

- Define the evaluator command, baseline, target, and pass/fail rule before editing.
- Do not call an optimization successful because ordinary tests pass if the declared evaluator fails.
- Change one performance cause at a time and keep each patch reversible.
- Run the evaluator and relevant regression tests after every meaningful candidate.
- Report `PASS`, `FAIL`, or `BLOCKED` with the command and evidence.
- Complete only after a passing evaluator result, regression evidence, and a final objective audit.

## Workflow

1. State the performance objective and what must not regress.
2. Inspect the current implementation and run the baseline evaluator when possible.
3. Define:
   - evaluator command;
   - baseline measurement;
   - target threshold;
   - relevant regression tests;
   - environment and dataset assumptions.
4. Use `update_plan` to record the objective, evaluator contract, and iteration boundary.
5. For work that spans multiple turns, use `create_goal` when no active goal exists. Use `get_goal` before resuming or finalizing.
6. Apply the smallest change that targets the measured bottleneck.
7. Run the evaluator and regression tests. Record the result in the active plan or normal repo artifact when one exists.
8. If the result fails, inspect the evidence and either make the next bounded change or report the blocker. Do not vary unrelated code to chase a number.
9. Stop after a small bounded number of unsuccessful iterations unless new evidence changes the diagnosis.
10. Before completion, rerun the evaluator from a clean enough state, verify the objective and regression criteria, then call `update_goal({status: "complete"})` only when the native goal is genuinely complete.

## Evaluator Rules

- Prefer a deterministic command with a stable input and output format.
- Keep warm-up, sample count, timeout, hardware, and environment assumptions explicit when they affect the result.
- Distinguish a real regression from an environment limitation, flaky measurement, or missing fixture.
- A benchmark that cannot reproduce the baseline is `BLOCKED`, not `PASS`.
- Preserve useful measurements even when the optimization is rejected.

## Completion Report

```text
PERFORMANCE GOAL REPORT
Objective: [measurable objective]
Evaluator: [command]
Baseline: [measurement and environment]
Target: [pass/fail rule]

Iterations:
- [change] -> [measurement] -> PASS/FAIL/BLOCKED -> [evidence]

Regression tests: PASS/FAIL/BLOCKED
Final evaluator: PASS/FAIL/BLOCKED
Remaining risks: [none or concise list]
```

Do not claim durable completion, benchmark improvement, or goal completion
without fresh evaluator evidence.
