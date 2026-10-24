"""Offline R.5 layout and installed-mode JCL checks (never touches MVS)."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / 'tools/checks/prepare-r5-extension-regression.py'


def load_generator():
    spec = importlib.util.spec_from_file_location('r5_installed_generator', GEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class R5InstalledLayoutTests(unittest.TestCase):
    def test_manifest_declares_separate_object_and_text_pds(self):
        data = (ROOT / 'config/dspal.yaml').read_text()
        for identity, dsn in (
                ('EXT_OBJ', 'BCPL.EXT.OBJ'),
                ('EXT_MAC', 'BCPL.EXT.MAC'),
                ('EXT_ASM', 'BCPL.EXT.ASM'),
                ('EXT_SOURCE', 'BCPL.EXT.SOURCE')):
            self.assertIn(f'  {identity}:\n    dsn: {dsn}\n', data)
        object_part = data.split('  EXT_OBJ:\n', 1)[1].split('  EXT_MAC:\n', 1)[0]
        self.assertIn('content_type: object', object_part)
        self.assertIn('populate: false', object_part)
        for member in ('BCXPRE', 'BCXCAT', 'BCXPOST'):
            self.assertIn(f'{member}: bootstrap-toolchain/extensions/bcx/', data)
        self.assertIn('DEMOHDR: bootstrap-toolchain/extensions/bcpldemo/bcpldemo.h', data)

    def test_installed_mode_uses_resident_macros_and_object_member(self):
        g = load_generator()
        t = g.trail_module()
        cards = g.make_deck(147, t.sample_generated(),
            ["//RG147R JOB (BCPL),'R5 TEST',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ', mode='installed',
            extension_dsn='HERC02.BCPL.EXT.OBJ',
            macro_dsn='HERC02.BCPL.EXT.MAC')
        for member in ('BCXPRE', 'BCXCAT', 'BCXPOST'):
            self.assertIn(f'DSN=HERC02.BCPL.EXT.MAC({member}),DISP=SHR', cards)
        self.assertIn('//EXTLIB   DD  DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR', cards)
        self.assertIn('         BCXREQ BCPLDEMO', cards)
        self.assertNotIn('BCXADD &PKG', cards)
        self.assertNotIn('BCXCAT &PKG', cards)
        self.assertNotIn('//ASMD ', cards)
        self.assertNotIn('DISP=MOD', cards)

    def test_absent_extension_stays_unlinked(self):
        g = load_generator()
        t = g.trail_module()
        for num in (146, 158):
            cards = g.make_deck(num, t.sample_generated(),
                [f"//RG{num:03d}R JOB (BCPL),'R5 TEST',CLASS=A"],
                'HERC02.BCPL.BOOT.OBJ', mode='installed',
                extension_dsn='HERC02.BCPL.EXT.OBJ',
                macro_dsn='HERC02.BCPL.EXT.MAC')
            self.assertNotIn('//EXTLIB', cards)
            self.assertNotIn('BCXREQ BCPLDEMO', cards)
            self.assertNotIn('BCXSEL BCPLDEMO', cards)

    def test_source_mode_still_embeds_r4_sources(self):
        g = load_generator()
        t = g.trail_module()
        cards = g.make_deck(147, t.sample_generated(),
            ["//RG147R JOB (BCPL),'R5 TEST',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')
        self.assertIn('         BCXREQ BCPLDEMO', cards)
        self.assertIn('BCXADD &PKG', cards)
        self.assertIn('//ASMD ', cards)
        self.assertNotIn('DSN=HERC02.BCPL.EXT.MAC(', cards)

    def test_install_deck_does_not_modify_core_datasets(self):
        deck = (ROOT / 'bootstrap-toolchain/jcl/r5dinst.jcl').read_text()
        self.assertIn('EXEC PGM=IFOX00', deck)
        self.assertIn('EXEC PGM=IEBGENER', deck)
        self.assertIn('EXEC PGM=IEBCOMPR', deck)
        self.assertNotIn(' JOB ', '\n'.join(line for line in deck.splitlines() if not line.startswith('//*')))
        self.assertIn('DSN=HERC02.BCPL.EXT.OBJ(BCPLDEMO),DISP=OLD', deck)
        self.assertNotIn('DSN=HERC02.BCPL.BOOT.OBJ(', deck)
        self.assertNotIn('DSN=HERC02.BCPL.BOOT.DEVOBJ(', deck)
        self.assertTrue(all(len(line) <= 71 for line in deck.splitlines()))


if __name__ == '__main__':
    unittest.main()
