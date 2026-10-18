---
name: antigravity-subagent
description: Delegate bounded work to a persistent Antigravity CLI subagent with default or explicit model selection, automatic tool approval, continued two-way conversation, and status/result-only handoffs. Use when asked to use Antigravity as a subagent; does not replace mandated model or review lanes.
---

# Antigravity subagent

Use `scripts/bridge.py` as the only parent-facing worker interface. Requires Python 3.9+, POSIX Unix sockets, authenticated `agy` on PATH, and the CLI stream-json interface. Tested with CLI 1.3.1 on macOS. The bridge starts a detached worker; each agent owns one long-lived `agy` process and conversation. The primary can do independent work between calls.

## Delegate

Pass one JSON request on stdin. No model ID is needed normally. Resolve the script path from this skill directory; never interpolate task text into shell code. Example:

```bash
python3 ${CODEX_HOME:-$HOME/.codex}/skills/antigravity-subagent/scripts/bridge.py <<'JSON'
{"op":"start","cwd":"/absolute/task/workspace","text":"Read-only: investigate the duplicate login request. Own only this investigation. Return findings, file references, confidence and verification limits."}
JSON
```

Optional `model_id` selects an exact ID from the catalog below. Omitted `cwd` uses the caller's current directory. Specify the task's actual workspace, ownership, constraints and acceptance evidence. Transfer only necessary context. Do not automatically give the whole parent transcript to the worker. Follow the governing repository's delegation/model rules; this skill does not override them.

## Continue the same worker

Each call uses the same script with a JSON object on stdin:

```json
{"op":"send","agent_id":"ag-0123456789abcdef","text":"Focus only on SSO; do not edit."}
{"op":"wait","agent_id":"ag-0123456789abcdef","after":0,"timeout":50}
{"op":"status","agent_id":"ag-0123456789abcdef"}
{"op":"close","agent_id":"ag-0123456789abcdef"}
```

- Keep a separate `after` cursor for each worker, initially 0. Replace it with each `wait` response's cursor. `wait` returns the next unseen event, or current status with the unchanged cursor on timeout. `send` acknowledgements do not advance that cursor. Do not poll rapidly; use a bounded wait while working independently where possible.
- `queued` means accepted by the bridge, not yet seen by the model. Inputs received during a turn are delivered FIFO after its result. This is continuous bidirectional conversation at turn boundaries, not in-flight interruption. Never send an urgent stop as ordinary queued text or claim it has already affected a running command.
- `running` means executing; `idle` contains a completed turn's handoff and keeps the session alive. It is not independent proof of task success.
- `waiting_input` contains the worker's question. Answer with `send` to the SAME agent. `blocked` contains its stated obstacle. These are worker reports, not native permission prompts.
- `failed` reports a short protocol/runtime error code; no raw stderr or transcript is returned. Correct the cause before starting another worker; do not silently change models or replay side effects.
- `close` drains already accepted turns, closes stdin, and ends the process. Wait for `closed`. It is graceful shutdown, not cancellation. Each running turn has a 15-minute CLI ceiling. Finish by closing workers you started.
- Worker state is in a private `/tmp/agy-subagent-<uid>/<agent_id>` directory. While active it is in memory; after termination only filtered events and configuration are retained. No restart/resume or automatic retry is implemented. A disappeared process is not a successful task.

## Permissions and output boundary

Worker sessions always launch with `--dangerously-skip-permissions --sandbox=false`. The bridge verifies `init.permission_mode == always-proceed` and the exact selected model before delivering tasks. This is full-access automatic tool approval at the CLI layer; it does not grant OS admin rights, extend the user's task scope, or override explicit repository/infrastructure/Git authorization rules. Initial account authentication remains a prerequisite.

Never run the worker directly through raw `agy`, tail its logs, or read its transcript to monitor progress. The bridge drains and discards stderr and all step/tool/thinking events before they reach the primary. Its public replies contain only status/result plus routing metadata (agent ID, turn ID, cursor and initial model ID).

The worker must end each turn with one `<subagent_result>` JSON frame containing `status` (`completed`, `waiting_input`, `blocked`) and `result`. Invalid framing fails closed with `invalid_result_contract`; raw text is never used as a fallback. The bridge reads the current turn's response, not `structured_output`: CLI 1.3.1 returned stale structured_output in a real two-turn test. The model is instructed to omit reasoning, commands and logs from its handoff. This filters source channels; it cannot prove that arbitrary free-text conclusions contain no quoted process detail. The primary remains responsible for evaluating results and integration.

## Models and default

Both automatic default selection and explicit `model_id` are supported. `models.json` is the runtime catalog; the table below is generated from the same successful query. Normal starts use the stored concrete default and do not depend on a network catalog request.

```json
{"op":"models"}
{"op":"refresh_models"}
```

`refresh_models` uses **`agy --output-format json models`** (global flag BEFORE subcommand), reads `command.data.models`, and updates every returned ID/label here and in the runtime catalog. It selects the highest numeric Gemini Flash version with Medium effort; versions from different model families are never compared. It only changes the default for new workers. Failed retrieval leaves the existing catalog intact. Refresh during skill maintenance or when a requested ID is absent; users should not have to type a model ID for ordinary work. An explicit unknown ID is rejected, never silently replaced. A provider can retire or deny a saved model; a ready default setting is not a guarantee of provider availability.

<!-- MODELS:START -->
Default model ID: `gemini-3.8-flash-medium`.

Catalog retrieved: 2026-10-08T16:43:10Z.

| Model ID | Model |
| --- | --- |
| `gemini-3.8-flash-high` | Gemini 3.8 Flash (High) |
| `gemini-3.8-flash-medium` | Gemini 3.8 Flash (Medium) |
| `gemini-3.8-flash-low` | Gemini 3.8 Flash (Low) |
| `gemini-3.7-flash-high` | Gemini 3.7 Flash (High) |
| `gemini-3.7-flash-medium` | Gemini 3.7 Flash (Medium) |
| `gemini-3.7-flash-low` | Gemini 3.7 Flash (Low) |
| `gemini-3.6-flash-high` | Gemini 3.6 Flash (High) |
| `gemini-3.6-flash-medium` | Gemini 3.6 Flash (Medium) |
| `gemini-3.6-flash-low` | Gemini 3.6 Flash (Low) |
| `gemini-3.1-pro-high` | Gemini 3.1 Pro (High) |
| `gemini-3.1-pro-low` | Gemini 3.1 Pro (Low) |
| `claude-opus-5-5-low` | Claude Opus 5.5 (Low) |
| `claude-opus-5-5-medium` | Claude Opus 5.5 (Medium) |
| `claude-opus-5-5-high` | Claude Opus 5.5 (High) |
| `claude-sonnet-5-5-low` | Claude Sonnet 5.5 (Low) |
| `claude-sonnet-5-5-medium` | Claude Sonnet 5.5 (Medium) |
| `claude-sonnet-5-5-high` | Claude Sonnet 5.5 (High) |
| `gpt-oss-120b-medium` | GPT-OSS 120B (Medium) |
<!-- MODELS:END -->

## CLI maintenance and checks

For missing stream capabilities, run `agy update`, then recheck the actual executable's `--help`; do not stop at the updater's version message. Allow a background update to finish and recheck the binary. Verify `--input-format`, `--output-format`, `--disable-slash-commands` and a real two-turn run before claiming readiness. Query the current catalog with the global flag placement above. Do not guess model IDs from display names.

Validate the skill with the skill-creator validator and run `python3 scripts/test_bridge.py`. For live acceptance, use a temporary task workspace, exercise memory across turns, ask/answer, queued follow-up, a harmless terminal command and scratch-file write without approvals, default selection, explicit model selection, and close. Report runtime evidence separately from unit tests. Do not use a prescribed but unavailable model lane under a substitute name.
