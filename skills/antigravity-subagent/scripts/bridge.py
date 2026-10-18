#!/usr/bin/env python3
"""Persistent Antigravity workers with a result-only local interface (POSIX)."""
import asyncio
import contextlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import uuid

SKILL = Path(__file__).resolve().parents[1]
CATALOG = SKILL / 'models.json'
ROOT = Path('/tmp') / f'agy-subagent-{os.getuid()}'
BEGIN, END = '<subagent_result>', '</subagent_result>'
CONTRACT = '''You are a delegated subagent with your own persistent context. Execute only
the assigned scope. The primary owns requirements, integration, and final decisions.
Do not launch other agents, commit/push, message people, or operate infrastructure
unless that specific action is explicitly authorized in the assignment. Follow the
target workspace's governing instructions. Other workers may share the workspace;
do not revert their changes. Ask the primary when necessary by ending this turn with
status waiting_input; its next message will answer you in this same conversation.
Return a concise handoff: conclusions, relevant file references, actual verification
outcomes, or one necessary question. Never include thinking, working commentary,
tool traces, executed commands, terminal output, or a transcript in the handoff.
At the very end of EVERY turn, emit exactly this frame, with valid JSON inside:
<subagent_result>{"status":"completed","result":"your concise handoff"}</subagent_result>
Allowed status: completed, waiting_input, blocked. There must be exactly one result
frame in the turn. Do not quote these delimiters inside the result. completed means
this turn has a handoff, not that unverified work is proven correct.
The frame is mandatory even for a simple acknowledgement or a follow-up answer.
'''


class BridgeError(Exception):
    pass


def result(status, text=None, **ids):
    return {**ids, 'status': status, 'result': text}


def parse_result(response):
    """Read only the explicitly framed handoff, never raw text or stale schema data."""
    if not isinstance(response, str) or response.count(BEGIN) != 1 or response.count(END) != 1:
        raise BridgeError('invalid_result_contract')
    _, framed = response.split(BEGIN)
    payload, after = framed.split(END)
    if after.strip():
        raise BridgeError('invalid_result_contract')
    try:
        data = json.loads(payload)
    except (ValueError, TypeError):
        raise BridgeError('invalid_result_contract') from None
    if (not isinstance(data, dict) or set(data) != {'status', 'result'}
            or data['status'] not in ('completed', 'waiting_input', 'blocked')
            or not isinstance(data['result'], str)):
        raise BridgeError('invalid_result_contract')
    return data


def error_code(error):
    text = str(error).lower()
    for code, terms in [('authentication_required', ('authentication required', 'sign in', 'not authenticated')),
                        ('model_unavailable', ('invalid model', 'unknown model', 'not recognized as a known model')),
                        ('quota_exhausted', ('quota', 'resource_exhausted', 'out of credits'))]:
        if any(term in text for term in terms):
            return code
    return 'cli_error'


def private_root():
    ROOT.mkdir(mode=0o700, exist_ok=True)
    st = ROOT.lstat()
    if ROOT.is_symlink() or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise BridgeError('unsafe_runtime_directory')


def directory(agent_id):
    if not isinstance(agent_id, str) or not re.fullmatch(r'ag-[0-9a-f]{16}', agent_id):
        raise BridgeError('invalid_agent_id')
    private_root()
    return ROOT / agent_id


def atomic_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def request_socket(folder, request):
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(60)
        sock.connect(str(folder / 'rpc'))
        sock.sendall((json.dumps(request, ensure_ascii=False) + '\n').encode())
        with sock.makefile('r') as stream:
            return json.loads(stream.readline())


def refresh_models():
    binary = shutil.which('agy')
    if not binary:
        raise BridgeError('cli_not_found')
    p = subprocess.run([binary, '--output-format', 'json', 'models'],
                       capture_output=True, text=True, timeout=45)
    if p.returncode:
        raise BridgeError(error_code(p.stderr))
    try:
        envelope = json.loads(p.stdout)
        models = envelope['command']['data']['models']
        if not models or any(not isinstance(m.get('id'), str) or not isinstance(m.get('label'), str) for m in models):
            raise ValueError()
        if len({m['id'] for m in models}) != len(models):
            raise ValueError()
        candidates = []
        for model in models:
            match = re.fullmatch(r'gemini-(\d+(?:\.\d+)*)-flash-medium', model['id'])
            if match:
                candidates.append((tuple(map(int, match[1].split('.'))), model['id']))
        default = max(candidates)[1]
    except (ValueError, KeyError, TypeError, AttributeError):
        raise BridgeError('invalid_model_catalog') from None
    catalog = {'default_model_id': default, 'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'models': models}
    doc = SKILL / 'SKILL.md'
    content = doc.read_text()
    start, end = '<!-- MODELS:START -->', '<!-- MODELS:END -->'
    if content.count(start) != 1 or content.count(end) != 1:
        raise BridgeError('invalid_skill_catalog_markers')
    table = f'\nDefault model ID: `{default}`.\n\nCatalog retrieved: {catalog["updated_at"]}.\n\n| Model ID | Model |\n| --- | --- |\n'
    table += ''.join(f'| `{m["id"]}` | {m["label"]} |\n' for m in models)
    updated = content.split(start)[0] + start + table + end + content.split(end)[1]
    atomic_json(CATALOG, catalog)
    temp = doc.with_suffix('.tmp')
    temp.write_text(updated)
    temp.replace(doc)
    return result('completed', f'Updated {len(models)} models; default: {default}.')


class Worker:
    def __init__(self, folder, config):
        self.folder, self.config = folder, config
        self.agent_id = folder.name
        self.events = []
        self.changed = asyncio.Condition()
        self.queue = asyncio.Queue()
        self.next_turn = 0
        self.active = 0
        self.state = 'starting'
        self.closing = False
        self.ready = asyncio.get_running_loop().create_future()
        self.pending_result = None
        self.proc = None
        self.done = asyncio.Event()

    def snapshot(self):
        return result(self.state, agent_id=self.agent_id, turn_id=self.active)

    async def emit(self, status, text=None, turn=None):
        self.state = status
        event = result(status, text, agent_id=self.agent_id,
                       turn_id=self.active if turn is None else turn, cursor=len(self.events) + 1)
        async with self.changed:
            self.events.append(event)
            self.changed.notify_all()
        return event

    async def handle(self, request):
        op = request.get('op')
        if op == 'send':
            text = request.get('text')
            if not isinstance(text, str) or not text.strip():
                raise BridgeError('text_required')
            if self.closing or self.state in ('failed', 'closed'):
                raise BridgeError('session_not_accepting_messages')
            self.next_turn += 1
            turn = self.next_turn
            self.queue.put_nowait((turn, text))
            # Acknowledgements are not event cursors: sending must not skip unread results.
            return result('queued', agent_id=self.agent_id, turn_id=turn)
        if op == 'status':
            return self.snapshot()
        if op == 'wait':
            after = request.get('after', 0)
            timeout = request.get('timeout', 50)
            if type(after) is not int or after < 0 or after > len(self.events):
                raise BridgeError('invalid_cursor')
            if not isinstance(timeout, (int, float)) or not 0 <= timeout <= 50:
                raise BridgeError('invalid_wait_timeout')
            async with self.changed:
                if len(self.events) <= after:
                    with contextlib.suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self.changed.wait_for(lambda: len(self.events) > after), timeout)
                if len(self.events) > after:
                    return self.events[after]
                return {**self.snapshot(), 'cursor': after}
        if op == 'close':
            self.closing = True
            self.queue.put_nowait(None)
            return result('closing', agent_id=self.agent_id)
        raise BridgeError('unknown_operation')

    async def rpc(self, reader, writer):
        try:
            data = json.loads(await reader.readline())
            response = await self.handle(data)
        except BridgeError as exc:
            response = result('failed', str(exc), agent_id=self.agent_id)
        except Exception:
            response = result('failed', 'invalid_request', agent_id=self.agent_id)
        writer.write((json.dumps(response, ensure_ascii=False) + '\n').encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def read_stdout(self):
        try:
            async for line in self.proc.stdout:
                event = json.loads(line)
                if event.get('event') == 'init':
                    init = event.get('init', {})
                    if init.get('permission_mode') != 'always-proceed' or init.get('model') != self.config['model_id']:
                        raise BridgeError('unexpected_cli_configuration')
                    if not self.ready.done():
                        self.ready.set_result(True)
                elif event.get('event') == 'result':
                    r = event['result']
                    if not self.ready.done():
                        raise BridgeError(error_code(r.get('error', '')))
                    if self.pending_result is None or self.pending_result.done():
                        raise BridgeError('unexpected_turn_result')
                    self.pending_result.set_result(r)
                # All progress, reasoning, tool events and deltas are discarded here.
        except Exception as exc:
            code = str(exc) if isinstance(exc, BridgeError) else 'invalid_cli_stream'
        else:
            code = 'cli_exited'
        for future in [self.ready, self.pending_result]:
            if future is not None and not future.done():
                future.set_exception(BridgeError(code))
        if not self.closing:
            await self.emit('failed', code)
            self.closing = True
            self.queue.put_nowait(None)

    async def discard_stderr(self):
        while await self.proc.stderr.read(65536):
            pass

    async def run(self):
        readers = []
        try:
            self.proc = await asyncio.create_subprocess_exec(
                self.config['binary'], '--input-format', 'stream-json', '--output-format', 'stream-json',
                '--dangerously-skip-permissions', '--sandbox=false', '--disable-slash-commands',
                '--model', self.config['model_id'], '--print-timeout', '15m',
                cwd=self.config['cwd'], stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                limit=16 * 1024 * 1024, start_new_session=True)
            readers = [asyncio.create_task(self.read_stdout()), asyncio.create_task(self.discard_stderr())]
            await asyncio.wait_for(asyncio.shield(self.ready), 60)
            while True:
                item = await self.queue.get()
                if item is None:
                    break
                self.active, text = item
                await self.emit('running')
                self.pending_result = asyncio.get_running_loop().create_future()
                prompt = CONTRACT + '\nAssignment from primary:\n' + text
                self.proc.stdin.write((json.dumps({'event': 'user', 'message': {'content': prompt}}) + '\n').encode())
                await self.proc.stdin.drain()
                r = await asyncio.wait_for(asyncio.shield(self.pending_result), 920)
                if r.get('status') != 'SUCCESS':
                    raise BridgeError(error_code(r.get('error', '')))
                handoff = parse_result(r.get('response'))
                state = 'idle' if handoff['status'] == 'completed' else handoff['status']
                await self.emit(state, handoff['result'])
            self.proc.stdin.close()
            await asyncio.wait_for(self.proc.wait(), 10)
            await self.emit('closed')
        except Exception as exc:
            code = str(exc) if isinstance(exc, BridgeError) else ('timeout' if isinstance(exc, asyncio.TimeoutError) else 'worker_error')
            await self.emit('failed', code)
        finally:
            self.closing = True
            if self.proc is not None and self.proc.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(self.proc.pid, signal.SIGTERM)
                try:
                    await asyncio.wait_for(self.proc.wait(), 5)
                except asyncio.TimeoutError:
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(self.proc.pid, signal.SIGKILL)
                    await self.proc.wait()
            for task in readers:
                task.cancel()
            if readers:
                await asyncio.gather(*readers, return_exceptions=True)
            atomic_json(self.folder / 'events.json', self.events)
            self.done.set()


async def serve(folder):
    config = json.loads((folder / 'config.json').read_text())
    worker = Worker(folder, config)
    server = await asyncio.start_unix_server(worker.rpc, str(folder / 'rpc'), limit=1024 * 1024)
    async with server:
        task = asyncio.create_task(worker.run())
        await worker.done.wait()
        await task
        # Let already-connected waiters receive the terminal event before shutting down.
        await asyncio.sleep(0.1)
    (folder / 'rpc').unlink(missing_ok=True)


def start(request):
    catalog = json.loads(CATALOG.read_text())
    model = request.get('model_id', catalog['default_model_id'])
    if model not in {m['id'] for m in catalog['models']}:
        raise BridgeError('unknown_model_id_refresh_models')
    text = request.get('text')
    if not isinstance(text, str) or not text.strip():
        raise BridgeError('text_required')
    cwd = Path(request.get('cwd', os.getcwd())).resolve(strict=True)
    if not cwd.is_dir():
        raise BridgeError('invalid_working_directory')
    binary = shutil.which('agy')
    if not binary:
        raise BridgeError('cli_not_found')
    agent_id = 'ag-' + uuid.uuid4().hex[:16]
    folder = directory(agent_id)
    folder.mkdir(mode=0o700)
    atomic_json(folder / 'config.json', {'binary': binary, 'cwd': str(cwd), 'model_id': model})
    proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--serve', str(folder)],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True, close_fds=True)
    for _ in range(100):
        if (folder / 'rpc').exists():
            response = request_socket(folder, {'op': 'send', 'text': text})
            return {**response, 'model_id': model}
        if proc.poll() is not None:
            raise BridgeError('worker_start_failed')
        time.sleep(0.05)
    proc.terminate()
    raise BridgeError('worker_start_timeout')


def dispatch(request):
    op = request.get('op')
    if op == 'start':
        return start(request)
    if op == 'refresh_models':
        return refresh_models()
    if op == 'models':
        c = json.loads(CATALOG.read_text())
        return result('completed', 'Default: ' + c['default_model_id'] + '\n' + '\n'.join(m['id'] + '\t' + m['label'] for m in c['models']))
    folder = directory(request.get('agent_id'))
    saved = folder / 'events.json'
    if saved.exists():
        events = json.loads(saved.read_text())
        if op == 'wait':
            after = request.get('after', 0)
            if type(after) is not int or not 0 <= after <= len(events):
                raise BridgeError('invalid_cursor')
            return events[after] if after < len(events) else {**events[-1], 'result': None}
        if op in ('status', 'close'):
            return events[-1]
        raise BridgeError('session_closed')
    return request_socket(folder, request)


def main():
    os.umask(0o077)
    if len(sys.argv) == 3 and sys.argv[1] == '--serve':
        asyncio.run(serve(Path(sys.argv[2])))
        return
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise BridgeError('invalid_request')
        output = dispatch(request)
    except BridgeError as exc:
        output = result('failed', str(exc))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        output = result('failed', 'bridge_request_failed')
    print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
