# Code Review

## Purpose

Run the named `/code-review` skill as the single review authority after the
required verification evidence exists.

## Scale Rule

- `Small`: skip review unless the user explicitly asks for it.
- `Medium` / `Large`: always run `/code-review`.

## Required Actions

- start the review authority with `gpt-5.6-sol` and high reasoning; if that model is unavailable, return `blocked`
- invoke `/code-review` inside that Sol review agent with the exact repository scope, governing spec, active planning artifact, and available verification evidence
- let `/code-review` own its code-quality and architecture perspectives using
  its native sequential or independent-lane contract
- require any review sub-agents created by `/code-review` to use `gpt-5.6-sol` with high reasoning
- require file and line evidence for every finding
- map the `/code-review` result to the Harness result as follows:
  - `APPROVE` with architecture `CLEAR` -> `pass`
  - `COMMENT` with only explicitly non-blocking findings and architecture `CLEAR` or `WATCH` -> `pass`, retaining every finding and remaining risk in the report
  - `REQUEST CHANGES`, architecture `BLOCK`, or any validated delivery-blocking finding -> `fail`
  - unavailable model, incomplete scope, missing required evidence, or an unavailable review skill -> `blocked`
- treat validated findings that violate correctness, security, accepted behavior, governing contracts, data integrity, or required test coverage as delivery blockers; do not block delivery for style-only or explicitly non-blocking suggestions

## Boundaries

- QA execution is not a review lane or review fallback
- `receiving-code-review` is not an additional review stage
- do not invoke external advisor CLIs or create a second review session solely
  to validate `/code-review`
- if `/code-review` is unavailable, report `blocked`; do not claim review
  success or silently substitute another review authority

## Required Output

1. files and boundaries reviewed
2. verification evidence considered
3. findings by severity with file and line references
4. architectural status and remaining risk
5. overall verdict: `pass` / `fail` / `blocked`
