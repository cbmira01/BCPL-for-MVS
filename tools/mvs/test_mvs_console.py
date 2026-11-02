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


if __name__ == '__main__':
    unittest.main()
