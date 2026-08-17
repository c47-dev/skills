# Sanity

## Purpose

Require the programmer or main execution owner to run programmer checks that match the changed boundary before real QA lanes and code review.

## Allowed Checks

- lint
- build
- type check
- unit tests
- narrow local checks
- markdown or path consistency checks for documentation-only changes

## Rules

- sanity is mandatory for every `Change`
- the programmer or main execution owner must run every applicable repository-provided lint, type-check, build, and unit-test command
- do not delegate programmer sanity responsibility to the independent QA role
- a missing or non-runnable required command must be reported as `blocked` or `not configured` with evidence; it must not be silently skipped
- sanity is programmer verification, not QA
- lint, type checks, builds, and unit tests are completely separate from real QA
- passing sanity does not count as, replace, reduce, or provide evidence for API QA
- passing sanity does not count as, replace, reduce, or provide evidence for browser UI QA
- required API or browser QA does not count as, replace, reduce, or provide evidence for programmer sanity
- passing sanity does not replace code review

## Error Track

- A previous workflow collapsed successful programmer checks into validation of a browser-visible feature. The correction separates evidence categories without making programmer checks optional: the programmer must run sanity, and an independent QA role must run applicable real QA.

## Required Output

1. lint command and result
2. type-check command and result
3. build command and result
4. unit-test command and result
5. any additional narrow checks and results
6. pass/fail/blocked result
7. failure, missing-command, or not-configured evidence, if any
