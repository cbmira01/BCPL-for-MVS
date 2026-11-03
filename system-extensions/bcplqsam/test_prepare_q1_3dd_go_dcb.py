"""Offline checks for the opt-in Q.0 RDJFCB geometry comparison."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def imported(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


dcbs = imported('q1_go_dcb', 'prepare-q1-3dd-go-dcb.py')
three = imported('q1_three', 'prepare-q1-3dd.py')
opendiag = imported('q1_open', 'prepare-q1-3dd-open-diag.py')


def diagnostic_deck() -> str:
    helper = three.query_helper().time_helper().trailer_helper()
    baseline = three.make_deck(
        helper.sample_generated(),
        ["//Q13DD JOB (BCPL),'DCB CHECK',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    return opendiag.instrument_deck(baseline)


class Q0ReaderGeometryTest(unittest.TestCase):
    def test_explicit_go_dcb_isolation(self):
        old = diagnostic_deck()
        new = dcbs.explicit_go_dcb(old)
        self.assertEqual(new.count(dcbs.GEOMETRY), 6)
        self.assertEqual(new.count('Q1O:GEOM R3='), 1)
        self.assertEqual(
            new.count('//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'), 1)
        self.assertEqual(new.count(' BCXREQ BCPLQSAM'), 1)
        undo = new
        for i in range(3):
            old_dd = f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE)'
            self.assertIn(old_dd + ',\n' + dcbs.GEOMETRY, undo)
            undo = undo.replace(old_dd + ',\n' + dcbs.GEOMETRY,
                                old_dd, 1)
        self.assertEqual(undo, old)
        self.assertTrue(all(len(row) <= 71 and row.isascii()
                            for row in new.splitlines()))

    def test_wrong_or_duplicate_source_is_rejected(self):
        old = diagnostic_deck()
        new = dcbs.explicit_go_dcb(old)
        with self.assertRaises(ValueError):
            dcbs.explicit_go_dcb(new)
        with self.assertRaises(ValueError):
            dcbs.explicit_go_dcb(old.replace('REGION=256K',
                                             'REGION=512K'))
        with self.assertRaises(ValueError):
            dcbs.explicit_go_dcb(old.replace('Q1O:GEOM R3=', 'NO TRACE'))
        with self.assertRaises(ValueError):
            dcbs.explicit_go_dcb(old.replace(
                '//Q00      DD  DSN=&&Q1H00,DISP=(OLD,DELETE)',
                '//Q00      DD  DSN=&&Q1H00,DISP=(SHR)'))

    def test_workarea_only(self):
        with self.assertRaises(ValueError):
            dcbs.workarea_path(Path('/tmp/q13dd-dcb.jcl'))


if __name__ == '__main__':
    unittest.main()
