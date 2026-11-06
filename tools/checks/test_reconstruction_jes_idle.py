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
# Real fresh console delta recorded from TK5 by jes-idle --live --diagnose.
TK5_HHC = '16:36:36 HHC00013I \'/\' input entered for console 0:0009: "$DA"\n'
TK5_TYPED = '16:36:36 $DA\n'
TK5_REPLY = '16:36:36 /17.36.35           $HASP000 NO ACTIVE JOBS\n'
TK5_LIVE_DELTA = 2 * (TK5_HHC + TK5_TYPED) + TK5_REPLY


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

    def test_second_observed_tk5_timestamp_is_valid(self):
        actual = "15:38:17 /16.38.17           $HASP000 NO ACTIVE JOBS\n"
        self.assertEqual('CLEAR', mod.parse_delta(actual).state)

    def test_tk5_accepts_only_a_preceding_command_echo(self):
        with_echo = "15:38:16 /$DA\n" + TK5_CLEAR
        self.assertEqual('CLEAR', mod.parse_delta(with_echo).state)
        self.assertEqual('UNKNOWN', mod.parse_delta(TK5_CLEAR + "15:38:18 /$DA\n").state)

    def test_tk5_unrecognized_non_hasps_are_not_ignored(self):
        for extra in ("HERCULES UNKNOWN RESPONSE\n", "IEF403I JOB X STARTED\n",
                      "$HASP000 MESSAGE\n", "JOB 123 EXECUTING\n"):
            with self.subTest(extra=extra):
                observation = mod.parse_delta(TK5_CLEAR + extra)
                self.assertNotEqual('CLEAR', observation.state)

    def test_tk5_invisible_extra_line_has_diagnostic_reason(self):
        result = mod.parse_delta("HHC00000I extra line\n" + TK5_CLEAR)
        self.assertEqual('UNKNOWN', result.state)
        self.assertIn('unrecognized console line', result.reason)

    def test_tk5_real_console_double_echo_accepts_one_reply(self):
        self.assertEqual('CLEAR', mod.parse_delta(TK5_LIVE_DELTA).state)

    def test_tk5_real_console_double_echo_two_samples(self):
        commands = []
        def capture(cmd):
            commands.append(cmd)
            return (0, TK5_LIVE_DELTA)
        ok, observations = mod.check_twice(capture)
        self.assertTrue(ok)
        self.assertEqual([mod.COMMAND, mod.COMMAND], commands)
        self.assertEqual(['CLEAR', 'CLEAR'], [o.state for o in observations])

    def test_tk5_one_complete_hercules_echo_pair_is_accepted(self):
        delta = TK5_HHC + TK5_TYPED + TK5_REPLY
        self.assertEqual('CLEAR', mod.parse_delta(delta).state)

    def test_tk5_echo_pair_must_be_exact_and_matched(self):
        bad = [
            TK5_HHC + TK5_REPLY,  # no matching typed echo
            TK5_HHC + TK5_TYPED.replace('$DA', '$DQ') + TK5_REPLY,
            TK5_HHC + TK5_TYPED.replace('16:36:36', '16:36:37') + TK5_REPLY,
            TK5_HHC.replace('HHC00013I', 'HHC00014I') + TK5_TYPED + TK5_REPLY,
            TK5_HHC.replace('0:0009', '0:000A') + TK5_TYPED +
                TK5_HHC + TK5_TYPED + TK5_REPLY,  # two nonidentical pairs
            3 * (TK5_HHC + TK5_TYPED) + TK5_REPLY,  # replay bounded at two
            TK5_HHC + TK5_TYPED + 'UNRELATED MESSAGE\n' + TK5_REPLY,
            TK5_HHC + TK5_TYPED + TK5_REPLY + TK5_TYPED,  # echo after reply
        ]
        for delta in bad:
            with self.subTest(delta=delta):
                self.assertNotEqual('CLEAR', mod.parse_delta(delta).state)

    def test_tk5_real_delta_with_active_or_incomplete_must_block(self):
        self.assertEqual('UNKNOWN', mod.parse_delta(TK5_LIVE_DELTA + '$HASP611 LIST INCOMPLETE\n').state)
        self.assertEqual('UNKNOWN', mod.parse_delta(TK5_LIVE_DELTA + '$HASP373 JOB00001 STARTED\n').state)

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
        self.assertIn('does not authorize reconstruction', buf.getvalue())

    def test_opt_in_blocked_diagnostic_displays_unfiltered_delta(self):
        delta = "HHC00000I extra line\n" + TK5_CLEAR
        fake = types.SimpleNamespace(capture=lambda cmd, timeout, settle: (0, delta))
        buf = io.StringIO()
        with patch.object(mod, 'load_mvs_console', return_value=fake), \
             contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main(['--live', '--diagnose'])
        self.assertEqual(2, rc)
        self.assertIn(repr(delta), buf.getvalue())
        self.assertIn('may contain sensitive data', buf.getvalue())

    def test_cli_live_transport_error_is_blocked(self):
        marker = 'PRIVATE_TEST_PASSWORD_998'
        def broken(cmd, *, timeout, settle):
            raise RuntimeError('unavailable ' + marker)
        fake = types.SimpleNamespace(capture=broken)
        buf = io.StringIO()
        with patch.object(mod, 'load_mvs_console', return_value=fake), contextlib.redirect_stderr(buf):
            rc = mod.main(['--live'])
        self.assertEqual(2, rc)
        self.assertIn('RuntimeError', buf.getvalue())
        self.assertNotIn(marker, buf.getvalue())


if __name__ == '__main__':
    unittest.main()
