"""Contract and lifecycle tests; CLI acceptance is a separate real run."""
import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bridge


class ResultBoundary(unittest.TestCase):
    def test_only_framed_handoff_survives(self):
        response = 'thinking: secret A\ncommand: secret B\nstdout: secret C\n'
        response += '<subagent_result>{"status":"completed","result":"Found the cause."}</subagent_result>\n'
        self.assertEqual(bridge.parse_result(response), {'status': 'completed', 'result': 'Found the cause.'})

    def test_unframed_and_extra_payloads_fail_closed(self):
        for response in ['raw command output',
                         '<subagent_result>{"status":"completed","result":"ok","thinking":"secret"}</subagent_result>',
                         '<subagent_result>{"status":"completed","result":3}</subagent_result>',
                         '<subagent_result>{"status":"completed","result":"ok"}</subagent_result>secret',
                         '<subagent_result>{}</subagent_result><subagent_result>{}</subagent_result>']:
            with self.subTest(response=response), self.assertRaises(bridge.BridgeError):
                bridge.parse_result(response)

    def test_errors_do_not_echo_tool_output(self):
        self.assertEqual(bridge.error_code('command secret; secret stdout'), 'cli_error')
        self.assertEqual(bridge.error_code('RESOURCE_EXHAUSTED secret'), 'quota_exhausted')

    def test_closed_session_cursor_does_not_repeat_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            event = {'status': 'failed', 'result': 'cli_error', 'cursor': 1}
            (folder / 'events.json').write_text(json.dumps([event]))
            with patch.object(bridge, 'directory', return_value=folder):
                self.assertEqual(bridge.dispatch({'op': 'wait', 'after': 0}), event)
                self.assertIsNone(bridge.dispatch({'op': 'wait', 'after': 1})['result'])

    def test_failed_catalog_query_preserves_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / 'models.json'
            catalog.write_text('{"default_model_id":"saved"}')
            p = type('Process', (), {'returncode': 1, 'stderr': 'secret failure'})()
            with patch.object(bridge, 'CATALOG', catalog), patch.object(bridge.shutil, 'which', return_value='/agy'), patch.object(bridge.subprocess, 'run', return_value=p):
                with self.assertRaises(bridge.BridgeError):
                    bridge.refresh_models()
            self.assertEqual(json.loads(catalog.read_text())['default_model_id'], 'saved')


class Communication(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.worker = bridge.Worker(Path('/tmp/ag-test'), {})

    async def test_busy_messages_are_fifo_and_do_not_skip_unread_results(self):
        self.worker.active = 1
        self.worker.state = 'running'
        event = await self.worker.emit('idle', 'first answer')
        for text in ['second', 'third']:
            ack = await self.worker.handle({'op': 'send', 'text': text})
            self.assertEqual(ack['status'], 'queued')
            self.assertNotIn('cursor', ack)
        self.assertEqual((await self.worker.queue.get())[1], 'second')
        self.assertEqual((await self.worker.queue.get())[1], 'third')
        self.assertEqual(await self.worker.handle({'op': 'wait', 'after': 0}), event)

    async def test_wait_wakes_for_new_result(self):
        task = asyncio.create_task(self.worker.handle({'op': 'wait', 'after': 0, 'timeout': 1}))
        await asyncio.sleep(0)
        await self.worker.emit('waiting_input', 'Which entry point?')
        reply = await task
        self.assertEqual(reply['status'], 'waiting_input')
        self.assertEqual(reply['result'], 'Which entry point?')
        timeout = await self.worker.handle({'op': 'wait', 'after': 1, 'timeout': 0})
        self.assertIsNone(timeout['result'])
        self.assertEqual(timeout['cursor'], 1)

    async def test_close_drains_existing_queue_and_rejects_new_work(self):
        await self.worker.handle({'op': 'send', 'text': 'accepted'})
        self.assertEqual((await self.worker.handle({'op': 'close'}))['status'], 'closing')
        self.assertEqual((await self.worker.queue.get())[1], 'accepted')
        self.assertIsNone(await self.worker.queue.get())
        with self.assertRaises(bridge.BridgeError):
            await self.worker.handle({'op': 'send', 'text': 'too late'})

    async def test_raw_tool_and_thinking_events_never_become_public_events(self):
        self.worker.config = {'model_id': 'test-model'}
        self.worker.closing = True
        self.worker.pending_result = asyncio.get_running_loop().create_future()
        stream = asyncio.StreamReader()
        terminal = {'status': 'SUCCESS', 'response': '<subagent_result>{"status":"completed","result":"current"}</subagent_result>',
                    'structured_output': {'status': 'completed', 'result': 'STALE'}}
        for event in [
            {'event': 'init', 'init': {'model': 'test-model', 'permission_mode': 'always-proceed'}},
            {'event': 'step_update', 'step_update': {'step_type': 'tool', 'tool_info': {'parameters': 'SECRET_COMMAND', 'output': 'SECRET_STDOUT'}}},
            {'event': 'step_update', 'step_update': {'step_type': 'thinking', 'text_delta': 'SECRET_THOUGHT'}},
            {'event': 'result', 'result': terminal},
        ]:
            stream.feed_data((json.dumps(event) + '\n').encode())
        stream.feed_eof()
        self.worker.proc = type('Proc', (), {'stdout': stream})()
        await self.worker.read_stdout()
        r = await self.worker.pending_result
        parsed = bridge.parse_result(r['response'])
        await self.worker.emit('idle', parsed['result'])
        public = json.dumps(self.worker.events)
        for secret in ['SECRET_COMMAND', 'SECRET_STDOUT', 'SECRET_THOUGHT', 'STALE']:
            self.assertNotIn(secret, public)
        self.assertEqual(self.worker.events[0]['result'], 'current')

    async def test_unexpected_permission_mode_is_rejected_before_task_delivery(self):
        self.worker.config = {'model_id': 'test-model'}
        stream = asyncio.StreamReader()
        stream.feed_data((json.dumps({'event': 'init', 'init': {'model': 'test-model', 'permission_mode': 'request-review'}}) + '\n').encode())
        stream.feed_eof()
        self.worker.proc = type('Proc', (), {'stdout': stream})()
        await self.worker.read_stdout()
        with self.assertRaisesRegex(bridge.BridgeError, 'unexpected_cli_configuration'):
            await self.worker.ready
        self.assertEqual(self.worker.events[-1]['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
