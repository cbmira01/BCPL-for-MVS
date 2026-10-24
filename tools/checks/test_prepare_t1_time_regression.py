from contextlib import ExitStack
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location('t1_prepare', HERE / 'prepare-t1-time-regression.py')
t1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1)


class FakeR0:
    @staticmethod
    def application_source(source):
        return ['R0APP CSECT', '         END']

    @staticmethod
    def checked_asm(source, name):
        return source.splitlines()

    @staticmethod
    def asm_step(step, target, lines):
        return [f'//{step} EXEC PGM=IFOX00', '//SYSIN DD *', *lines, '/*']


class TestT1Generator(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        reg = base / 'bootstrap-toolchain/regression'
        bcx = base / 'bootstrap-toolchain/extensions/bcx'
        time = base / 'bootstrap-toolchain/extensions/bcpltime'
        demo = base / 'bootstrap-toolchain/extensions/bcpldemo'
        asm = base / 'bootstrap-toolchain/asm'
        for path in (reg, bcx, time, demo, asm):
            path.mkdir(parents=True, exist_ok=True)
        for number, selection in t1.SELECTIONS.items():
            directory = reg / f'{number:03d}-case'
            directory.mkdir()
            (directory / 'time-selection.asm').write_text(
                ''.join(f'         {line}\n' for line in selection))
        for path in (bcx / 'BCXPRE.asm', bcx / 'BCXPOST.asm',
                     time / 't1-catalog.asm', time / 'bcpltime.asm',
                     demo / 'bcpldemo.asm', asm / 'bcplmain.asm',
                     asm / 'bcplrgs.asm'):
            path.write_text('         MACRO\n         MEND\n')
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in [('ROOT', base), ('REG', reg), ('BCX', bcx),
                            ('TIME', time), ('DEMO', demo)]:
            self.stack.enter_context(patch.object(t1, name, value))
        self.stack.enter_context(patch.object(t1, 'load_r0', return_value=FakeR0))

    def deck(self, number, mode='source'):
        return t1.make_deck(number, 'dummy',
                             [f"//RG{number:03d}R JOB (BCPL),'TEST',CLASS=A"],
                             'HERC02.BCPL.BOOT.OBJ', mode,
                             'HERC02.BCPL.EXT.OBJ' if mode == 'installed' else None,
                             'HERC02.BCPL.EXT.MAC' if mode == 'installed' else None)

    def test_source_time_only(self):
        deck = self.deck(159)
        self.assertIn('//ASMT EXEC', deck)
        self.assertNotIn('//ASMD EXEC', deck)
        self.assertIn('//TIMEOBJ  DD  DSN=&&T1TMOBJ', deck)
        self.assertNotIn('//DEMOOBJ  DD', deck)
        self.assertIn('BCXREQ BCPLTIME', deck)

    def test_source_two_packages(self):
        for number in (160, 161, 162):
            deck = self.deck(number)
            self.assertIn('//ASMT EXEC', deck)
            self.assertIn('//ASMD EXEC', deck)
            self.assertIn('//DEMOOBJ  DD  DSN=&&T1DEOBJ', deck)
            self.assertIn('//TIMEOBJ  DD  DSN=&&T1TMOBJ', deck)

    def test_reverse_selection(self):
        deck = self.deck(161)
        self.assertLess(deck.index('BCXREQ BCPLTIME'),
                        deck.index('BCXREQ BCPLDEMO'))

    def test_upgrade_duplicate(self):
        deck = self.deck(162)
        self.assertEqual(deck.count('BCXREQ BCPLTIME'), 2)
        self.assertEqual(deck.count('BCXSEL BCPLTIME'), 1)
        self.assertEqual(deck.count('BCXREQ BCPLDEMO'), 1)

    def test_installed_read_only_macro_library(self):
        deck = self.deck(160, 'installed')
        self.assertIn('DSN=HERC02.BCPL.EXT.MAC(BCXCAT)', deck)
        self.assertIn('//EXTLIB   DD  DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR', deck)
        self.assertNotIn('//ASMD EXEC', deck)
        self.assertNotIn('//ASMT EXEC', deck)
        self.assertNotIn('//TIMEOBJ  DD', deck)

    def test_fail_closed_on_fixture_mutation(self):
        fixture = t1.REG / '160-case/time-selection.asm'
        fixture.write_text('         BCXREQ BCPLTIME\n')
        with self.assertRaisesRegex(ValueError, 'fixture changed'):
            self.deck(160)

    def test_reject_bad_mode(self):
        with self.assertRaisesRegex(ValueError, 'mode'):
            self.deck(159, 'writable')

    def test_reject_missing_installed_dsns(self):
        with self.assertRaisesRegex(ValueError, 'requires approved'):
            t1.make_deck(160, 'dummy',
                         ["//RG160R JOB (BCPL),'TEST',CLASS=A"],
                         'HERC02.BCPL.BOOT.OBJ', 'installed')


if __name__ == '__main__':
    unittest.main()
