#!/usr/bin/env python3
"""Offline tests for mvs-console: no Docker, Hercules or JES interaction."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name('mvs-console')
loader = importlib.machinery.SourceFileLoader('mvs_console', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class ConsoleTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(mod.normalize('mvs', 'D A,L'), '/D A,L')
        self.assertEqual(mod.normalize('jes2', '$D U,PRTS'), '/$D U,PRTS')
        self.assertEqual(mod.normalize('hercules', 'devlist'), 'devlist')
        with self.assertRaises(ValueError):
            mod.normalize('mvs', 'D A,L\nquit')
        with self.assertRaises(ValueError):
            mod.normalize('hercules', '/devlist')

    def test_classification(self):
        self.assertEqual(mod.classify('jes2', '$D U,PRTS'), 'inquiry')
        self.assertEqual(mod.classify('hercules', 'devinit 580 *'), 'disruptive')
        self.assertEqual(mod.classify('mvs', 'D A,L'), 'inquiry')
        self.assertNotEqual(mod.classify('mvs', 'S JOBNAME'), 'inquiry')
        self.assertNotEqual(mod.classify('hercules', 'attach 580 3420 *'), 'inquiry')

    def test_aliases(self):
        self.assertEqual(mod.resolved('jes2', ['printers']), ('$D U,PRTS', True))
        self.assertEqual(mod.resolved('jes2', ['$D', 'U,PUNS']), ('$D U,PUNS', False))

    def test_tape_file_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(mod, 'TAPES', Path(tmp)):
                (Path(tmp) / 'demo.aws').write_bytes(b'abc')
                self.assertEqual(mod.tape_command(['mount','0580','demo.aws']),
                                 ('hercules','devinit 0580 /tk5/tape/demo.aws',False))
                self.assertEqual(mod.tape_command(['unmount','580']),
                                 ('hercules','devinit 580 *',False))
                for name in ('../demo.aws', '/tmp/demo.aws', 'bad name.aws'):
                    with self.subTest(name=name), self.assertRaises(ValueError):
                        mod.tape_command(['mount','580',name])
                with self.assertRaises(ValueError):
                    mod.tape_command(['mount','580','missing.aws'])

    def test_no_send_dry_run(self):
        from argparse import Namespace
        opts = Namespace(dry_run=True, yes=False, allow_disruptive=False, timeout=5, settle=0)
        with mock.patch.object(mod, 'dispatch') as send:
            self.assertEqual(mod.execute(['tape','unmount','580'],opts), 0)
            send.assert_not_called()

    def test_noninteractive_refusal(self):
        with mock.patch.object(mod.sys.stdin,'isatty',return_value=False):
            self.assertFalse(mod.confirm('operational', 'x', yes=False, allow_disruptive=False, dry_run=False))
            self.assertFalse(mod.confirm('disruptive', 'x', yes=True, allow_disruptive=False, dry_run=False))
            self.assertTrue(mod.confirm('operational', 'x', yes=True, allow_disruptive=False, dry_run=False))

    def test_log_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp)/'3033.log'
            log.write_text('earlier\n')
            with mock.patch.object(mod,'LOG',log):
                n=mod.log_offset()
                with log.open('a') as f:
                    f.write('later\n')
                self.assertEqual(mod.read_delta(n),'later\n')


    DEVLIST = ("02:27:27 HHC01603I devlist\n"
               "02:27:27 HHC02279I 0:000E 1403 prt/prt00e.txt open\n"
               "02:27:27 HHC02279I 0:0480 3420 * IO[12] maxsize=0\n"
               "02:27:27 HHC02279I 0:0390 3390 dasd/tk5res.390 open\n")

    def test_devlist_filters_tapes_and_replays(self):
        duplicate = self.DEVLIST + self.DEVLIST
        self.assertEqual(mod.replay_filter(duplicate), self.DEVLIST)
        self.assertEqual(list(mod.tape_rows(duplicate)), ['0480'])
        self.assertEqual(mod.device_rows(duplicate)['0390'][0], '3390')

    def test_no_general_message_dedup(self):
        msg = '12:00 $HASP000 some event\n'
        self.assertEqual(mod.replay_filter(msg + msg), msg + msg)
        changed = self.DEVLIST.replace('IO[12]', 'IO[13]')
        self.assertEqual(mod.replay_filter(self.DEVLIST + changed), self.DEVLIST + changed)

    def test_filtered_display_status_and_missing(self):
        from io import StringIO
        with mock.patch('sys.stdout', new_callable=StringIO) as output:
            self.assertEqual(mod.display_tapes(self.DEVLIST), 0)
            self.assertIn('0:0480 3420', output.getvalue())
            self.assertNotIn('3390', output.getvalue())
        with mock.patch('sys.stdout', new_callable=StringIO) as output:
            self.assertEqual(mod.display_tapes(self.DEVLIST, '480'), 0)
            self.assertIn('0:0480 3420', output.getvalue())
        with mock.patch('sys.stderr', new_callable=StringIO):
            self.assertEqual(mod.display_tapes(self.DEVLIST, '390'), 1)
            self.assertEqual(mod.display_tapes('unrelated log', '480'), 1)

    def test_tape_address_preflight_fail_closed(self):
        with mock.patch.object(mod, 'capture', return_value=(0, self.DEVLIST)):
            self.assertTrue(mod.verify_tape_address('480', timeout=5, settle=0))
            self.assertFalse(mod.verify_tape_address('390', timeout=5, settle=0))
            self.assertFalse(mod.verify_tape_address('999', timeout=5, settle=0))
        with mock.patch.object(mod, 'capture', return_value=(1, self.DEVLIST)):
            self.assertFalse(mod.verify_tape_address('480', timeout=5, settle=0))
        with mock.patch.object(mod, 'capture', return_value=(0, 'other output')):
            self.assertFalse(mod.verify_tape_address('480', timeout=5, settle=0))
        busy = self.DEVLIST.replace('IO[12]', 'IO[12] open busy')
        with mock.patch.object(mod, 'capture', return_value=(0, busy)):
            self.assertFalse(mod.verify_tape_address('480', timeout=5, settle=0))

    def test_mount_requires_proved_tape_before_send(self):
        from argparse import Namespace
        opts = Namespace(dry_run=False, yes=True, allow_disruptive=False, timeout=5, settle=0)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'safe.aws').write_bytes(b'abc')
            with mock.patch.object(mod, 'TAPES', Path(tmp)), \
                 mock.patch.object(mod, 'verify_tape_address', return_value=False), \
                 mock.patch.object(mod, 'dispatch') as send:
                self.assertEqual(mod.execute(['tape', 'mount', '390', 'safe.aws'], opts), 3)
                send.assert_not_called()
            with mock.patch.object(mod, 'TAPES', Path(tmp)), \
                 mock.patch.object(mod, 'verify_tape_address', return_value=True), \
                 mock.patch.object(mod, 'dispatch', return_value=0) as send:
                self.assertEqual(mod.execute(['tape', 'mount', '480', 'safe.aws'], opts), 0)
                send.assert_called_once()

    def test_status_uses_full_devlist_not_unsupported_argument(self):
        self.assertEqual(mod.tape_command(['status', '480']), ('hercules', 'devlist', True))


    def test_devices_is_static_and_offline(self):
        from argparse import Namespace
        from io import StringIO
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        with mock.patch.object(mod, 'dispatch') as send, \
             mock.patch('sys.stdout', new_callable=StringIO) as out:
            self.assertEqual(mod.execute(['devices'], opts), 0)
            display = out.getvalue()
            for number in ('3420', '3390', '3505', '3705'):
                self.assertIn(number, display)
            self.assertIn('static reference', display)
            send.assert_not_called()

    def test_question_mark_help_stays_local(self):
        from argparse import Namespace
        from io import StringIO
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        for args in (['?'], ['?', 'tape'], ['help', '?'], ['tape', '?'],
                     ['mvs', '?'], ['jes2', '?'], ['hercules', '?'],
                     ['devices', '?'], ['commands', '?'], ['explain', '?']):
            with self.subTest(args=args), \
                 mock.patch.object(mod, 'dispatch') as send, \
                 mock.patch('sys.stdout', new_callable=StringIO) as out:
                self.assertEqual(mod.execute(args, opts), 0)
                self.assertTrue(out.getvalue())
                send.assert_not_called()

    def test_help_excess_arguments_rejected(self):
        from argparse import Namespace
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        with self.assertRaises(ValueError):
            mod.execute(['tape', '?', 'mount'], opts)
        with self.assertRaises(ValueError):
            mod.execute(['devices', '3420'], opts)



    def test_hercules_device_alias_dispatch(self):
        from argparse import Namespace
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        with mock.patch.object(mod, "dispatch", return_value=0) as send, \
             mock.patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
            self.assertEqual(mod.execute(["hercules", "devices", "dasd"], opts), 0)
            send.assert_called_once_with("devlist", timeout=5, settle=0, tape_only=False,
                                         tape_address=None, device_filter="dasd")

    def test_hercules_device_filters(self):
        from io import StringIO
        output = (self.DEVLIST +
                  "02:27:27 HHC02279I 0:0009 3215-C *syscons cmdpref '/' open\n"
                  "02:27:27 HHC02279I 0:000E 1403 prt/prt00e.txt open\n")
        for category, expected, absent in [
            ("dasd", "0:0390 3390", "0:0480 3420"),
            ("tapes", "0:0480 3420", "0:0390 3390"),
            ("printers", "0:000E 1403", "0:0390 3390"),
            ("terminal", "0:0009 3215-C", "0:0390 3390"),
        ]:
            with self.subTest(category=category), \
                 mock.patch("sys.stdout", new_callable=StringIO) as shown:
                self.assertEqual(mod.display_devices(output, category), 0)
                self.assertIn(expected, shown.getvalue())
                self.assertNotIn(absent, shown.getvalue())

    def test_devices_help_and_invalid_args_stay_local(self):
        from argparse import Namespace
        from io import StringIO
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        for words in (["hercules", "devices", "help"], ["hercules", "devices", "?"],
                      ["?", "hercules", "?"], ["?", "hercules", "devices"],
                      ["?", "hercules", "devices", "?"]):
            with self.subTest(words=words), \
                 mock.patch.object(mod, "dispatch") as send, \
                 mock.patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(mod.execute(words, opts), 0)
                self.assertTrue(output.getvalue())
                send.assert_not_called()
        for words in (["hercules", "devices", "dasd", "help"],
                      ["hercules", "devices", "dasd", "?"]):
            with self.subTest(words=words), \
                 mock.patch.object(mod, "dispatch") as send, \
                 mock.patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(mod.execute(words, opts), 0)
                self.assertIn("display dasd devices", output.getvalue())
                send.assert_not_called()
        for words in (["hercules", "devices", "bogus"],
                      ["hercules", "devices", "bogus", "help"]):
            with self.subTest(words=words), \
                 mock.patch.object(mod, "dispatch") as send:
                with self.assertRaises(ValueError):
                    mod.execute(words, opts)
                send.assert_not_called()

    def test_duplicate_hercules_error_responses_only(self):
        response = ("15:49:54 HHC01603I devices dasd\n"
                    "15:49:54 HHC01600E Unknown command devices\n")
        self.assertEqual(mod.replay_filter(response * 2, "devices dasd"), response)
        self.assertEqual(mod.replay_filter(response * 2, "other command"), response * 2)
        msg = "15:49:54 $HASP000 JES event\n"
        self.assertEqual(mod.replay_filter(msg * 2), msg * 2)
        changed = response.replace("Unknown command", "Accepted command")
        self.assertEqual(mod.replay_filter(response + changed, "devices dasd"),
                         response + changed)


    def test_nested_help_not_sent_to_consoles(self):
        from argparse import Namespace
        from io import StringIO
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        requests = [
            (["mvs", "devices", "?"], "no 'devices' alias"),
            (["mvs", "devices", "help"], "no 'devices' alias"),
            (["mvs", "dasd", "?"], "Underlying command: /D U,DASD"),
            (["jes2", "printers", "?"], "Underlying command: /$D U,PRTS"),
            (["hercules", "devices", "?"], "hercules devices"),
            (["hercules", "devices", "help"], "hercules devices"),
            (["tape", "mount", "?"], "tape list"),
            (["jes2", "unknown", "?"], "No local help"),
        ]
        for words, expected in requests:
            with self.subTest(words=words), \
                 mock.patch.object(mod, "dispatch") as send, \
                 mock.patch.object(mod, "capture") as capture, \
                 mock.patch("builtins.input", side_effect=AssertionError("unexpected prompt")), \
                 mock.patch("sys.stdout", new_callable=StringIO) as out:
                self.assertEqual(mod.execute(words, opts), 0)
                self.assertIn(expected, out.getvalue())
                send.assert_not_called()
                capture.assert_not_called()

        # Unknown categories are rejected locally, including help requests.
        for words in (["hercules", "devices", "bogus", "?"],
                      ["hercules", "devices", "bogus", "help"]):
            with self.subTest(words=words), \
                 mock.patch.object(mod, "dispatch") as send, \
                 mock.patch.object(mod, "capture") as capture, \
                 mock.patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
                with self.assertRaisesRegex(ValueError, "unknown device category 'bogus'"):
                    mod.execute(words, opts)
                send.assert_not_called()
                capture.assert_not_called()


    def test_repl_rejects_misplaced_startup_options(self):
        from argparse import Namespace
        from io import StringIO
        opts = Namespace(dry_run=False, yes=False, allow_disruptive=False, timeout=5, settle=0)
        with mock.patch("builtins.input", side_effect=[
                     "hercules 'help devlist' --dry-run",
                     "mvs 'D A,L' --timeout 2",
                     "quit"
                 ]), \
             mock.patch.object(mod, "execute", wraps=mod.execute) as execute, \
             mock.patch.object(mod, "dispatch") as dispatch, \
             mock.patch("sys.stderr", new_callable=StringIO) as errors:
            self.assertEqual(mod.repl(opts), 0)
            self.assertIn("--dry-run", errors.getvalue())
            self.assertIn("--timeout", errors.getvalue())
            dispatch.assert_not_called()
            execute.assert_called_once_with(["quit"], opts)



if __name__ == '__main__':
    unittest.main()
