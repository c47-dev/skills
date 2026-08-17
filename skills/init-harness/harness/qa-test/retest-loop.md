# Retest Loop

## Purpose

Fix and retest whenever sanity, any required QA lane, QA report completeness, or code review fails.

## Required Actions

1. collect the failure evidence
2. localize the failure to the owning boundary
3. fix the issue in the main agent flow
4. rerun sanity
5. rerun every required QA lane affected by the fix, including the originally failed lane
6. rebuild the QA report from the fresh QA evidence whenever any QA lane reruns
7. rerun `/code-review` when review is applicable to the current change, using the refreshed QA report

## Rules

- repeat until every mandatory test procedure passes
- stop only if:
  - all mandatory test procedures pass
  - a real blocker is identified
  - the user stops the task
- do not stop after the first QA failure
- do not report partial success while required QA is still failing

## Required Output

1. whether a QA loop was required
2. which boundary failed
3. QA lanes rerun and refreshed QA report status
4. `/code-review` result when review was applicable
5. whether retest passed or is blocked
