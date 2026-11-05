"""Offline synthetic tests of the JES2 $DA idle safeguard.

The fixture examples are NOT claimed to be verified TK5 console transcripts.
"""
from __future__ import annotations
import contextlib
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'reconstruction/jes-idle'


def load_script():
    loader = importlib.machinery.SourceFileLoader('reconstruction_jes_idle_test', str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


mod = load_script()
CLEAR = "12:34:00  /$DA\n12:34:01  $HASP612 NO ACTIVE JOBS\n"
ACTIVE = "12:34:00  /$DA\n12:34:01 JOB00012 $HASP608 IC19BLD EXECUTING A PRIO 9 IBM1\n"
# Exact fresh console line reported from WSL against TK5/MVS 3.8J, 2026-11-05.
TK5_CLEAR = "15:20:00 /16.19.59           $HASP000 NO ACTIVE JOBS\n"


class TestParse(unittest.TestCase):
    def test_observed_clear_with_correlated_echo(self):
        r = mod.parse_delta(CLEAR)
        self.assertEqual('CLEAR', r.state)
        self.assertEqual(1, len(r.evidence))

    def test_actual_tk5_transcript_without_separate_echo(self):
        observation = mod.parse_delta(TK5_CLEAR)
        self.assertEqual('CLEAR', observation.state)
        self.assertIn('$HASP000 NO ACTIVE JOBS', observation.evidence[0])

    def test_tk5_clear_is_not_generic_hasp000(self):
        for text in (
            '$HASP000 NO ACTIVE JOBS\n',
            '15:20:00 $HASP000 NO ACTIVE JOBS\n',
            '15:20:00 /16.19.59 $HASP000 OK\n',
            '15:20:00 /16.19.59 $HASP000 NO ACTIVE JOBS FROM FILE\n',
            '15:20:00 /16.19.59 $HASP000 NO ACTIVE JOBS\nOTHER UNKNOWN MESSAGE\n',
        ):
            with self.subTest(text=text):
                self.assertEqual('UNKNOWN', mod.parse_delta(text).state)

    def test_tk5_active_or_incomplete_remains_blocked(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(TK5_CLEAR + '$HASP611 LIST INCOMPLETE\n').state)
        self.assertEqual('ACTIVE', mod.parse_delta(TK5_CLEAR + ACTIVE).state)

    def test_tk5_two_fresh_samples_required(self):
        seen = []
        def capture(command):
            seen.append(command)
            return (0, TK5_CLEAR if len(seen) == 1 else '')
        passed, observations = mod.check_twice(capture)
        self.assertFalse(passed)
        self.assertEqual(2, len(observations))
        self.assertEqual(['CLEAR', 'UNKNOWN'], [r.state for r in observations])

    def test_tk5_both_fresh_samples_clear(self):
        passed, observations = mod.check_twice(lambda command: (0, TK5_CLEAR))
        self.assertTrue(passed)
        self.assertEqual(['CLEAR', 'CLEAR'], [r.state for r in observations])

    def test_empty_and_transport_failure_blocked(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('').state)
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR, 1).state)

    def test_no_echo_rejects_stale_or_unrelated_reply(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('$HASP612 NO ACTIVE JOBS\n').state)

    def test_echo_after_result_cannot_correlate_reply(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('$HASP612 NO ACTIVE JOBS\n/$DA\n').state)

    def test_unexpected_positive_phrase_without_message_id_blocks(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('/$DA\nNO ACTIVE JOBS\n').state)

    def test_active_job_blocks(self):
        self.assertEqual('ACTIVE', mod.parse_delta(ACTIVE).state)

    def test_modern_active_job_blocks(self):
        response = '/$DA\nJOB00007 $HASP890 JOB(SPINLOOP)\n$HASP890 JOB(SPINLOOP) STATUS=(EXECUTING/SPL2)\n'
        self.assertEqual('ACTIVE', mod.parse_delta(response).state)

    def test_incomplete_list_takes_precedence(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR + '$HASP611 LIST INCOMPLETE\n').state)

    def test_contradictory_active_and_empty_refused(self):
        self.assertEqual('ACTIVE', mod.parse_delta(CLEAR + ACTIVE).state)

    def test_ongoing_jes_job_activity_blocks(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR + '$HASP373 JOB00012 STARTED\n').state)

    def test_other_hasps_blocks(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR + '$HASP000 INVALID COMMAND\n').state)

    def test_duplicate_reply_refused(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR + '$HASP612 NO ACTIVE JOBS\n').state)

    def test_rejected_command_refused(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(CLEAR + 'COMMAND REJECTED\n').state)

    def test_wrong_console_command_refused(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('/$DQ\n$HASP612 NO ACTIVE JOBS\n').state)

    def test_unparseable_error_output_refused(self):
        self.assertEqual('UNKNOWN', mod.parse_delta('HTTP accepted; no console messages captured').state)


class TestReadOnlyCheck(unittest.TestCase):
    def test_twice_clear_issues_only_fixed_command(self):
        calls = []
        def capture(cmd):
            calls.append(cmd)
            return 0, CLEAR
        passed, observations = mod.check_twice(capture)
        self.assertTrue(passed)
        self.assertEqual([mod.COMMAND, mod.COMMAND], calls)
        self.assertEqual(['CLEAR', 'CLEAR'], [x.state for x in observations])

    def test_first_unknown_stops_without_second_query(self):
        calls = []
        def capture(cmd):
            calls.append(cmd)
            return 0, ''
        passed, observations = mod.check_twice(capture)
        self.assertFalse(passed)
        self.assertEqual(1, len(calls))
        self.assertEqual('UNKNOWN', observations[-1].state)

    def test_second_active_blocks(self):
        calls = []
        def capture(cmd):
            calls.append(cmd)
            return (0, CLEAR if len(calls) == 1 else ACTIVE)
        passed, observations = mod.check_twice(capture)
        self.assertFalse(passed)
        self.assertEqual(['CLEAR', 'ACTIVE'], [x.state for x in observations])

    def test_cli_parsing_synthetic_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'fresh-console-delta.txt'
            path.write_text(CLEAR)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod.main(['--parse-file', str(path)])
            self.assertEqual(0, rc)
            self.assertIn('not a live JES-idle verification', buf.getvalue())

    def test_cli_live_uses_mvs_console_transport_only(self):
        commands = []
        fake = types.SimpleNamespace(capture=lambda cmd, timeout, settle: (commands.append(cmd) or 0, CLEAR))
        buf = io.StringIO()
        with patch.object(mod, 'load_mvs_console', return_value=fake), contextlib.redirect_stdout(buf):
            rc = mod.main(['--live'])
        self.assertEqual(0, rc)
        self.assertEqual(['/$DA', '/$DA'], commands)
        self.assertIn('Reconstruction --run remains disabled', buf.getvalue())

    def test_cli_live_transport_error_is_blocked(self):
        def broken(cmd, *, timeout, settle):
            raise RuntimeError('unavailable')
        fake = types.SimpleNamespace(capture=broken)
        with patch.object(mod, 'load_mvs_console', return_value=fake), contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main(['--live'])
        self.assertEqual(2, rc)


if __name__ == '__main__':
    unittest.main()
