"""Offline verification of the single-TK5 public reconstruction entry point."""
from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reconstruction'))
import live_entry as entry


class Terminal:
    def __init__(self, tty):
        self.tty = tty
    def isatty(self):
        return self.tty


class TestLiveEntry(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = []
        self.messages = []

    def invoke(self, *, in_tty=True, out_tty=True, fake=None, prompt=None):
        def runner(*args, **kwargs):
            self.calls.append((args, kwargs))
            if fake is not None:
                fake(*args, **kwargs)
        with patch.object(entry, 'load_extensionless', return_value=type('Module', (), {'load_dspal_core': staticmethod(lambda root: 'CORE')})):
            return entry.run_live(self.root, runner,
                                  lambda root, command: (0, 'MOCK'),
                                  stdin=Terminal(in_tty), stdout=Terminal(out_tty),
                                  emit=self.messages.append,
                                  prompt=prompt or (lambda msg: 'NO'),
                                  observe=lambda root, emit: (True, ['CLEAR', 'CLEAR']))

    def test_actual_extensionless_tool_loader(self):
        from dataclasses import dataclass
        path = self.root / 'extensionless-tool'
        path.write_text('from dataclasses import dataclass\n@dataclass\nclass Item:\n    value: int\n')
        module = entry.load_extensionless(path, 'test_real_extensionless_tool')
        self.assertEqual(42, module.Item(42).value)
        self.assertIs(module, sys.modules['test_real_extensionless_tool'])
        sys.modules.pop('test_real_extensionless_tool', None)

    def test_jes_capture_exception_is_not_accepted_as_idle(self):
        class Probe:
            @staticmethod
            def load_mvs_console(path):
                class Console:
                    @staticmethod
                    def capture(*args, **kw):
                        raise OSError('console failure')
                return Console()
            @staticmethod
            def check_twice(capture):
                capture('/$DA')
                raise AssertionError('unreachable')
        with patch.object(entry, 'load_extensionless', return_value=Probe):
            with self.assertRaisesRegex(OSError, 'console failure'):
                entry.observe_jes(self.root, self.messages.append)

    def test_noninteractive_input_never_calls_runner(self):
        self.assertEqual(2, self.invoke(in_tty=False))
        self.assertFalse(self.calls)

    def test_noninteractive_output_never_calls_runner(self):
        self.assertEqual(2, self.invoke(out_tty=False))
        self.assertFalse(self.calls)

    def test_interactive_path_receives_exact_dependencies(self):
        self.assertEqual(0, self.invoke())
        self.assertEqual(1, len(self.calls))
        args, keywords = self.calls[0]
        self.assertEqual(self.root, args[0])
        self.assertEqual('CORE', args[3])
        self.assertTrue(keywords['terminal'])
        self.assertEqual((True, ['CLEAR', 'CLEAR']), keywords['jes_idle_guard']())
        self.assertEqual((0, 'MOCK'), args[4](['command']))

    def test_approved_controller_exception_is_fail_closed(self):
        def failure(*args, **kw):
            raise RuntimeError('synthetic guard failure')
        self.assertEqual(2, self.invoke(fake=failure))
        self.assertTrue(any('synthetic guard failure' in line for line in self.messages))

    def test_interrupted_controller_retains_nonzero_rc(self):
        def failure(*args, **kw):
            raise KeyboardInterrupt()
        self.assertEqual(130, self.invoke(fake=failure))

    def test_closed_input_controller_retains_nonzero_rc(self):
        def failure(*args, **kw):
            raise EOFError()
        self.assertEqual(130, self.invoke(fake=failure))

    def test_module_load_failure_is_fail_closed(self):
        with patch.object(entry, 'load_extensionless', side_effect=FileNotFoundError('missing tool')):
            rc = entry.run_live(self.root, lambda *a,**k: self.fail('runner reached'),
                                lambda r,c: (0,''), stdin=Terminal(True),
                                stdout=Terminal(True), emit=self.messages.append)
        self.assertEqual(2, rc)
        self.assertTrue(any('missing tool' in x for x in self.messages))

    def test_jes_parser_fails_closed_on_unknown(self):
        class Obs:
            def __init__(self, state):
                self.state = state
                self.reason = state
                self.evidence = ['FROM JES']
        class Probe:
            @staticmethod
            def load_mvs_console(path):
                return object()
            @staticmethod
            def check_twice(capture):
                return False, [Obs('UNKNOWN')]
        with patch.object(entry, 'load_extensionless', return_value=Probe):
            result = entry.observe_jes(self.root, self.messages.append)
        self.assertEqual(False, result[0])
        self.assertEqual('UNKNOWN', result[1][0].state)
        self.assertTrue(any('FROM JES' in x for x in self.messages))

    def test_jes_parser_reports_each_clear(self):
        class Obs:
            def __init__(self):
                self.state='CLEAR';self.reason='fresh';self.evidence=['HASP000']
        class Probe:
            @staticmethod
            def load_mvs_console(path):
                class Console:
                    @staticmethod
                    def capture(cmd, timeout, settle):
                        assert (cmd,timeout,settle)==('/$DA',10.0,2.0)
                        return 0,'data'
                return Console()
            @staticmethod
            def check_twice(capture):
                capture('/$DA');capture('/$DA')
                return True, [Obs(),Obs()]
        with patch.object(entry, 'load_extensionless', return_value=Probe):
            result=entry.observe_jes(self.root,self.messages.append)
        self.assertTrue(result[0]);self.assertEqual(2,len(result[1]))
        self.assertEqual(2,len([x for x in self.messages if 'CLEAR' in x]))


if __name__=='__main__':
    unittest.main()
