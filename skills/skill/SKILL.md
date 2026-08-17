---
name: skill
description: Manage local Codex skills by listing, inspecting, creating, editing, validating, backing up, and removing user or project skill folders.
---

# Skill Management

Use this skill for the lifecycle of local `SKILL.md` folders. Work directly
with the active user skill root (normally `~/.codex/skills/`) and the current
project's `.codex/skills/` directory. Do not assume an external skill CLI,
session runtime, usage database, or hidden state service exists.

## Inventory

1. Locate the active user and project skill roots.
2. Use `find` or `rg --files` to enumerate `SKILL.md` files.
3. Read frontmatter and report name, description, scope, and validation status.
4. Never invent usage counts, quality scores, or trigger statistics. Report
   `unknown` when the repository does not provide them.

## Inspect and Search

- Inspect one skill's complete `SKILL.md` before editing it.
- Search by name, description, or body with `rg`.
- Search cross-skill references before renaming or removing a skill.
- Distinguish active files from backup copies and plugin/system skills.

## Create or Edit

1. Define one clear responsibility and a precise trigger description.
2. Keep YAML frontmatter to `name` and `description` unless the active skill
   format explicitly supports another field.
3. Keep the body concise and imperative. Prefer the smallest workflow that
   adds non-obvious procedural value beyond native model intelligence.
4. Use `apply_patch` for edits and preserve unrelated user changes.
5. Validate with the available `quick_validate.py` after editing.
6. Scan for stale references, deleted skill names, runtime assumptions, and
   contradictory instructions.

## Remove

Before deleting a skill:

1. Confirm the exact user or project scope and skill directory.
2. Search active skills for references to the skill.
3. Identify whether another workflow must be updated or whether the reference
   should simply disappear.
4. Confirm the deletion when it was not already explicitly requested.
5. Create or identify a recoverable backup before material deletion.
6. Remove only the exact skill directory and verify it is absent.
7. Validate the remaining referencing skills.

Never delete a broad directory, workspace root, or unrelated skill collection.

## Backup and Validation

- Use a timestamped backup outside the active skill root before batch changes.
- Keep backup copies separate from active discovery scans.
- Validate changed skills and the workflows that reference them.
- A successful validation means the frontmatter is valid; it does not prove the
  workflow is semantically correct, so also inspect cross-references and run
  a bounded realistic smoke test when the skill is complex.

## Native Runtime Boundary

Skills should describe model reasoning, normal repository files, explicit tool
calls, and native goal/subagent capabilities. Do not add dependencies on:

- external workflow CLI commands;
- terminal multiplexer orchestration or hidden worker protocols;
- hidden runtime ledgers or session state;
- notification hooks or HUD state;
- external advisor sessions.

If a workflow truly needs independent subagents, state the independence,
handoff, and synthesis contract explicitly; otherwise keep it in the same
conversation and document.
