"""TA.0 build-chain tests. All MVS documents are synthetic, not acceptance proof."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/distribution/audit-binary-build-chain.py'
INVENTORY = ROOT / 'packaging/distribution/manifest/ta0-inventory.yaml'
spec = importlib.util.spec_from_file_location('ta0_binary_chain', SOURCE)
assert spec and spec.loader
chain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chain)

CORE = ('BCPLMAIN', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT',
        'BCPLIO', 'BCPLRGS', 'BCPLREG')
EXT = ('BCPLDEMO', 'BCPLTIME', 'BCPLQSAM')
ASM = ('ASMMMAIN', 'ASMMMEM', 'ASMMBYTE', 'ASMMAPT', 'ASMMIO', 'ASMRGS', 'ASMREG')
PUT = ('PUTMAIN', 'PUTMEM', 'PUTBYTE', 'PUTAPT', 'PUTIO', 'PUTRGS', 'PUTREG')
STEPS = {
    'IC19BLD': ('ASM', 'LKED', 'SAVEOBJ'),
    'BLDBMAIN': ASM + PUT,
    'BLIBBLD': ('COMP', 'PREPASM', 'PREPLK', 'FIXASM', 'ASMBLIB', 'INSTALL'),
    'BLDCORCO': ('ASMCOR', 'PUTCOR', 'RDCOR', 'VFCOR'),
    'BLDCORLB': ('ASMCOLIB', 'PUTCOLIB', 'RDCOLIB', 'VFCOLIB'),
    'BCPLDEMO': ('ASMDEMO', 'PUTDEMO', 'READBACK', 'VERIFY'),
    'BCPLTIME': ('ASMTIME', 'PUTTIME', 'READBACK', 'VERIFY'),
    'BCPLQSAM': ('ASMQ', 'PUTQSAM', 'READBACK', 'VERIFY'),
}


class BinaryChainAudit(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.manifest = chain.validation.load(INVENTORY)
        data = {}
        for row in self.manifest['datasets'][2:]:
            key = row['dspal_key']
            members = {}
            for name in row['members']:
                if key in chain.BINARY_KEYS or name in row.get('generated_members', {}):
                    continue
                if key == 'BOOT_SOURCE' and name == 'BLIB':
                    continue
                path = f'fixture/{key}/{name}.txt'
                members[name] = path
                p = self.root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                if key in ('BOOT_JCL', 'MR10_JCL') and name in STEPS:
                    p.write_text(self._jcl(STEPS[name]), encoding='utf-8')
                else:
                    p.write_text('synthetic source only\n', encoding='utf-8')
            if key == 'BOOT_JCL':
                path = 'fixture/BOOT_JCL/BLIBBLD.txt'
                members['BLIBBLD'] = path
                p = self.root / path
                p.write_text(self._jcl(STEPS['BLIBBLD']), encoding='utf-8')
            data[key] = {**row['target_dcb'],
                         'dsn': row['target_dsn_template'].removeprefix('{HLQ}.'),
                         'members': members,
                         'populate': False,
                         'generated_members': ({'BLIB': 'workarea/bootstrap-cambridge/demoted/blib'}
                                               if key == 'BOOT_SOURCE' else {})}
        self.dspal = {'mvs': {'hlq': 'HERC02'}, 'datasets': data}
        v = self.root / 'tools/reconstruction/verify.py'
        v.parent.mkdir(parents=True, exist_ok=True)
        v.write_text('ASM_CORE = ' + repr(ASM) + '\n'
                     'PUT_CORE = ' + repr(PUT) + '\n'
                     'EXPECTED_STEPS = {'
                     + ', '.join(repr(k) + ': ' + ('(*ASM_CORE, *PUT_CORE)' if k == 'BLDBMAIN'
                                                    else repr(s)) for k, s in STEPS.items()) + '}\n'
                     'RUNTIME_MEMBERS = frozenset(' + repr(CORE + ('BLIB', 'BCPLCO', 'COROUTIN')) + ')\n'
                     'EXTENSION_MEMBERS = frozenset(' + repr(EXT) + ')\n', encoding='utf-8')
        chain.validation.check(self.manifest, self.dspal, self.root)

    @staticmethod
    def _jcl(steps):
        return ''.join(f'//{step} EXEC PGM=IFOX00\n' for step in steps)

    def plan(self):
        return chain.build_plan(self.manifest, self.dspal, self.root)

    def test_exact_fifteen_members(self):
        p = self.plan()
        self.assertEqual(p['summary']['binary_members'], 15)
        self.assertEqual(p['summary']['mvs_receipts_verified'], 0)
        self.assertEqual(p['summary']['rights_approvals'], 0)
        self.assertEqual(p['summary']['unshipped_build_jobs'], ['BOOT_JCL(BLIBBLD)'])
        self.assertEqual(p['summary']['bcpl_source_rebuilds_unavailable_without_native_compiler'], 2)

    def test_generated_coroutine_source_chain(self):
        row = next(r for r in self.plan()['members'] if r['target'] == 'BOOT_OBJ(COROUTIN)')
        self.assertEqual(row['selected_source_members'], ['BOOT_SOURCE(COROUTIN)', 'BOOT_ASM(COROUTIN)'])
        self.assertTrue(row['requires_generated_assembler'])
        self.assertEqual(row['build_job'], 'BOOT_JCL(BLDCORLB)')
        self.assertIsNone(row['mvs_binary_readback_receipt'])

    def test_historical_blib_not_claimed_shippable_builder(self):
        row = next(r for r in self.plan()['members'] if r['target'] == 'BOOT_OBJ(BLIB)')
        self.assertFalse(row['build_jcl_on_tape'])
        self.assertTrue(row['requires_absent_compiler_for_bcpl_source_rebuild'])
        self.assertEqual(row['build_job'], 'BOOT_JCL(BLIBBLD)')

    def test_expected_reconstruction_steps_required(self):
        p = self.root / self.dspal['datasets']['BOOT_JCL']['members']['BLDBMAIN']
        p.write_text(p.read_text().replace('//ASMREG EXEC', '//ASMXYZ EXEC'))
        with self.assertRaisesRegex(chain.ChainError, 'JCL steps differ'):
            self.plan()

    def test_missing_build_jcl(self):
        p = self.root / self.dspal['datasets']['BOOT_JCL']['members']['BLDCORCO']
        p.unlink()
        with self.assertRaisesRegex(chain.ChainError, 'missing/unsafe Git-backed'):
            self.plan()

    def test_missing_contract(self):
        p = self.root / 'tools/reconstruction/verify.py'
        p.write_text(p.read_text().replace("'BLIBBLD':", "'NOTBLIB':"))
        with self.assertRaisesRegex(chain.ChainError, 'contracts missing'):
            self.plan()

    def test_runtime_inventory_drift(self):
        p = self.root / 'tools/reconstruction/verify.py'
        p.write_text(p.read_text().replace("'BCPLMAIN'", "'BADMAIN'"))
        with self.assertRaisesRegex(chain.ChainError, 'BOOT_OBJ differs'):
            self.plan()

    def test_missing_selected_binary(self):
        row = next(r for r in self.manifest['datasets'] if r.get('dspal_key') == 'EXT_OBJ')
        row['members'].remove('BCPLQSAM')
        with self.assertRaisesRegex(chain.ChainError, 'EXT_OBJ differs'):
            self.plan()

    def test_missing_generated_assembler(self):
        row = next(r for r in self.manifest['datasets'] if r.get('dspal_key') == 'BOOT_ASM')
        row['members'].remove('COROUTIN')
        with self.assertRaisesRegex(chain.ChainError, 'missing selected source'):
            self.plan()

    def test_bad_source_mapping(self):
        self.dspal['datasets']['BOOT_JCL']['members']['BLIBBLD'] = '../../escape.jcl'
        with self.assertRaisesRegex(chain.ChainError, 'missing/unsafe'):
            self.plan()

    def _listings(self):
        p = self.root / 'listings'
        p.mkdir()
        for key in chain.BINARY_KEYS:
            members = next(r['members'] for r in self.manifest['datasets'] if r.get('dspal_key') == key)
            dsn = 'HERC02.' + self.dspal['datasets'][key]['dsn']
            (p / (key + '.txt')).write_text(f'{dsn}:\n' + ''.join(f'    {m}\n' for m in members))
        return p

    def test_saved_readonly_mvs_inventory(self):
        folder = self._listings()
        for key in chain.BINARY_KEYS:
            row = next(r for r in self.manifest['datasets'] if r.get('dspal_key') == key)
            dsn = 'HERC02.' + self.dspal['datasets'][key]['dsn']
            chain.check_inventory_listing(folder / (key + '.txt'), dsn, set(row['members']))

    def test_inventory_missing_member(self):
        folder = self._listings()
        p = folder / 'MR10_LOAD.txt'
        p.write_text('HERC02.BCPL.MR10KIT.LOAD:\n')
        with self.assertRaisesRegex(chain.ChainError, 'missing'):
            chain.check_inventory_listing(p, 'HERC02.BCPL.MR10KIT.LOAD', {'ICINT19'})

    def test_inventory_extra_member(self):
        folder = self._listings()
        p = folder / 'MR10_LOAD.txt'
        with p.open('a') as f: f.write('    EXTRAMEM\n')
        with self.assertRaisesRegex(chain.ChainError, 'extra'):
            chain.check_inventory_listing(p, 'HERC02.BCPL.MR10KIT.LOAD', {'ICINT19'})

    def test_inventory_duplicate_member(self):
        folder = self._listings()
        p = folder / 'MR10_LOAD.txt'
        with p.open('a') as f: f.write('    ICINT19\n')
        with self.assertRaisesRegex(chain.ChainError, 'duplicate member'):
            chain.check_inventory_listing(p, 'HERC02.BCPL.MR10KIT.LOAD', {'ICINT19'})

    def test_inventory_wrong_heading(self):
        folder = self._listings()
        with self.assertRaisesRegex(chain.ChainError, 'wrong MVS dataset heading'):
            chain.check_inventory_listing(folder / 'MR10_LOAD.txt', 'OTHER.BCPL.MR10KIT.LOAD', {'ICINT19'})


if __name__ == '__main__':
    unittest.main()
