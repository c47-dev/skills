# Browser QA Network Monitor Workflow

Use this document only inside the Browser UI QA lane when the verified browser flow issues requests that affect correctness, data safety, auth state, or persistence behavior.

## Source Of Truth

- repository contract: `AGENTS.md`
- test entrypoint: `harness/phases/test.md`
- browser lane execution document: `harness/qa-test/browser-ui-qa.md`
- browser automation capability: `browser:control-in-app-browser`

## Architecture

| Layer | Responsibility |
| --- | --- |
| Browser UI QA agent | execute the real browser flow with `browser:control-in-app-browser` |
| Browser binding and tab | use the selected Browser runtime and a fresh tab for that QA run |
| Documented network surface | collect network evidence only when exposed by the selected Browser runtime |
| QA report | combine visible UI evidence and network evidence into one verdict |

## Session Contract

- every browser QA run must use a fresh tab from the browser binding selected according to the Browser skill
- record the initial URL and visible state before interaction
- do not inspect cookies, local storage, profiles, passwords, or session stores
- when authentication is required, use an already authenticated supported browser session; if none is available, return `blocked`
- the same browser binding and tab must be used for:
  - page navigation
  - interaction flow
  - network request inspection, when the selected Browser runtime documents that capability
  - latency evidence collection

## Network Monitoring Contract

- inspect network traffic only when the selected Browser runtime documentation exposes the required capability
- when available and required, inspect navigational requests and API or data requests that can affect:
  - authentication
  - persistence
  - visible state
  - permission behavior
  - sensitive data exposure
- static asset requests are not required evidence unless they directly explain a visible failure

## Required Evidence

For each relevant request, collect when retrievable:

- URL
- HTTP method
- status code
- request headers relevant to auth or content type
- request body excerpt
- response headers relevant to auth, cache, or content type
- response body excerpt
- latency evidence in milliseconds

If a field is not retrievable from the active tooling, the report must say so explicitly instead of inventing data.

## Required Concern Checks

The QA report must explicitly check and classify:

- unexpected duplicate requests
- unexpected retries
- inconsistent response body versus visible UI state
- auth or cookie leakage across runs
- cross-session contamination
- unexpected error payloads hidden by UI fallback
- sensitive data exposure in request or response bodies

## Browser QA Verdict Rule

- browser QA passes only if both conditions are true:
  - visible UI checks pass
  - network concern checks pass
- any unresolved network concern affecting correctness or data safety returns `fail`
- tooling limits that block required evidence return `blocked`

## Execution Guidance

- use `browser:control-in-app-browser` for the browser flow
- follow the Browser skill's exact browser-selection, setup, and runtime-documentation requirements
- use a fresh tab from the selected browser binding
- use request or response-body evidence only where the selected Browser runtime explicitly documents and provides it
- if a checklist requires network evidence that the selected Browser runtime cannot provide, return `blocked`

## Required Output

Return exactly:

1. surfaces tested
2. checks executed
3. network evidence collected
4. pass items
5. fail items
6. concerns found
7. tooling limits, if any
8. overall verdict: `pass` / `fail` / `blocked`
