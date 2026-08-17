# API QA

Use this document only for the independent API QA executor.

## Required Inputs

- target system
- governing spec path
- affected API surfaces
- API QA checklist

## Execution Rules

- this lane is mandatory whenever API QA is classified as required
- construct this lane's bounded QA contract; it must include the repository root, the `qa` lane, the complete checklist, exact allowed commands, forbidden operations, completion criteria, and required evidence
- start one bounded API QA sub-agent using `gpt-5.6-luna` with low reasoning
- give the sub-agent only the bounded API QA contract and required tool instructions
- if the required model or tool is unavailable, return `blocked`; do not substitute another model or execution surface
- execute API QA against the real API surface
- do not replace API QA with source-only review
- do not replace API QA with programmer self-review, lint, type checks, builds, or unit tests
- verify every checklist item
- collect direct evidence for every pass and fail item
- report exact failures and exact blocked conditions
- this output becomes the API QA section of the QA report

## Required Checks

For every checklist item, verify:

- request shape
- response shape
- status code
- error payload
- side effect, if applicable

## Required Output

Return exactly:

1. surfaces tested
2. checks executed
3. pass items with evidence
4. fail items with evidence
5. tooling or environment limits, if any
6. overall verdict: `pass` / `fail` / `blocked`

## Failure Rule

If any required check fails:

- return `fail`
- point to the failing surface
- include the concrete evidence

Do not propose code changes.
