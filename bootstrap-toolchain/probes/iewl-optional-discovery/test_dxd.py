"""Host-only R.4 DXD/CXD preflight (no JES/IFOX/IEWL claims)."""
from pathlib import Path
import importlib.util
import unittest

HERE = Path(__file__).resolve().parent


def candidate():
    spec = importlib.util.spec_from_file_location('r4_dxd',
                                                  HERE / 'make-dxd-job.py')
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CumulativeLengthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = candidate()
        cls.base = cls.m.baseline()

    def test_package_adds_distinct_dxd_and_q(self):
        for pkg, (xd, cs) in self.m.XD.items():
            text = self.m.extension_source(pkg, self.base)
            self.assertIn(f'{xd:<8} DXD   F', text)
            self.assertIn(f'{cs:<8} CSECT', text)
            self.assertIn(f'         DC    Q({xd})', text)
            self.assertEqual(text.count('         END   '), 1)
            self.assertEqual(text.count(' CSECT'), 3)
            self.assertIn("DC    CL4'BCEX'", text)
        self.assertNotEqual(self.m.XD['a'][0], self.m.XD['b'][0])

    def test_observer_cannot_possess_package_symbol_names(self):
        text = self.m.observer_source(self.base)
        self.assertIn('DXDLEN   CXD', text)
        self.assertIn('LR    15,0', text)
        self.assertNotIn('WXTRN', text)
        for word in ('DMOBEG', 'R2BBEG', 'R4DXDA', 'R4DXDB', 'BCPLREG'):
            self.assertNotIn(word, text)

    def test_four_links_select_only_explicit_objects(self):
        deck = self.m.make_deck([
            "//R4DXDCXD JOB (BCPL),'R4 DXD',CLASS=A,MSGCLASS=A"],
            self.base)
        cards = deck.splitlines()
        self.assertEqual(cards.count('/*'), 7)
        self.assertEqual(deck.count(' INCLUDE PKGA'), 2)
        self.assertEqual(deck.count(' INCLUDE PKGB'), 2)
        self.assertEqual(deck.count(' ENTRY R4CXDOBS'), 4)
        self.assertEqual(deck.count('DXDLEN   CXD'), 1)
        self.assertIn('DC    Q(R4DXDA)', deck)
        self.assertIn('DC    Q(R4DXDB)', deck)
        self.assertNotIn('DISP=MOD', deck)
        self.assertTrue(all(x.isascii() and len(x) <= 71 for x in cards))
        for p in self.m.PROFILE:
            start = next(i for i,x in enumerate(cards)
                         if x.startswith(f'//{self.m.LINK[p]:<8} EXEC'))
            end = next(i for i,x in enumerate(cards[start:],start)
                       if x.startswith('//SYSLMOD'))
            section = '\n'.join(cards[start:end])
            self.assertEqual(' INCLUDE PKGA' in section,
                             'a' in self.m.SELECT[p])
            self.assertEqual(' INCLUDE PKGB' in section,
                             'b' in self.m.SELECT[p])
            self.assertIn('DSN=&&R4OBS,DISP=(OLD,PASS)', section)

    def test_bad_jobcard(self):
        with self.assertRaisesRegex(ValueError, 'JOB card'):
            self.m.make_deck(['//OTHER JOB X'], self.base)


if __name__ == '__main__':
    unittest.main()
