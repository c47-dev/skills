# Browser UI QA

Use this document only for the independent Browser UI QA executor.

Browser UI QA must use `browser:control-in-app-browser`.

## Required Inputs

- target system
- governing spec path
- affected browser-visible surfaces
- browser UI QA checklist

## Execution Rules

- this lane is mandatory whenever browser UI QA is classified as required
- construct this lane's bounded QA contract; it must include the repository root, the `qa` lane, the complete checklist, exact allowed commands, forbidden operations, completion criteria, and required evidence
- start one bounded Browser UI QA sub-agent using `google-antigravity/gemini-3.7-flash` with medium reasoning
- give the sub-agent only the bounded Browser UI QA contract and `browser:control-in-app-browser` instructions
- if the required model or browser tool is unavailable, return `blocked`; do not substitute another model or execution surface
- use `browser:control-in-app-browser` and follow its browser-selection and documentation requirements
- execute the real browser flow
- use a fresh tab in the selected browser binding and record the initial URL and visible state
- do not inspect cookies, local storage, profiles, passwords, or session stores
- when authentication is required, use an already authenticated supported browser session; if authentication is unavailable, return `blocked` rather than bypassing sign-in or switching to an unapproved source
- read `harness/qa-test/browser-network-monitor.md` when the verified flow issues requests that affect auth, persistence, visible state, permissions, or sensitive data
- collect network evidence only through capabilities explicitly documented by the selected Browser runtime; if required network evidence is unavailable, return `blocked`
- do not replace browser QA with source-code-only review
- do not replace browser QA with programmer self-review, lint, type checks, builds, or unit tests
- verify every checklist item
- collect concrete evidence for every pass and fail item
- report tooling limits explicitly when request or response bodies are not retrievable
- this output becomes the browser UI QA section of the QA report

## Required Checks

For every checklist item, verify:

- required elements are present
- interaction flow works
- visible state changes are correct
- visible error rendering is correct

For every relevant network request, verify when retrievable:

- URL, method, and status are expected
- request body does not contain unexpected or sensitive data
- response body matches the visible UI state
- latency evidence is recorded
- duplicate requests, unexpected retries, and session contamination are absent

## Required Output

Return exactly:

1. surfaces tested
2. checks executed
3. network evidence collected, when required and available
4. pass items with evidence
5. fail items with evidence
6. concerns found
7. tooling limits, if any
8. overall verdict: `pass` / `fail` / `blocked`

## Failure Rule

If any required check fails:

- return `fail`
- point to the failing surface
- include the concrete evidence

Do not propose code changes.
