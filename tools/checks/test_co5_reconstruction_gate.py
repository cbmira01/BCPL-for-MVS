"""Offline CO.5 reconstruction gate tests: no MVS/JES interaction."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'tools/reconstruction/coroutine_gate.py'
spec = importlib.util.spec_from_file_location('co5_recon_gate', HELPER)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class RebuildCoroutineGateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.git = 'a' * 40
        self.inv = {'BOOT_ASM': 'HERC02.BCPL.BOOT.ASM'}

    def check(self, kind, output):
        return gate.verify_reconstruction_coroutine(
            kind, root=self.root, output=output,
            git_sha=self.git, inventory=self.inv)

    def test_compiled_requires_real_file_and_job(self):
        line = ('JOB 123\nsaved Cambridge CODE: '
                'workarea/co5-production/coroutines-generated.asm\n')
        with self.assertRaisesRegex(ValueError, 'CODE missing'):
            self.check('coroutine-compile', line)
        path = self.root / gate.COMPILED
        path.parent.mkdir(parents=True)
        path.write_text('         CSECT\n')
        self.assertIsNone(self.check('coroutine-compile', line))
        with self.assertRaisesRegex(ValueError, 'CODE missing'):
            self.check('coroutine-compile', line.replace('JOB 123', 'JOB X'))

    def test_prepared_checks_card_count_and_exports(self):
        path = self.root / gate.PREPARED
        path.parent.mkdir(parents=True)
        rows = (['CO3LIB   CSECT',
                 '         ENTRY C3INIT,C3CREATE,C3DELETE'] +
                ['         DS    0F'] * 100 +
                ['         END   CO3LIB'])
        path.write_text('\n'.join(rows) + '\n')
        text = f'Prepared IFOX COROUTIN: {gate.PREPARED} ({len(rows)} cards)\n'
        self.assertIsNone(self.check('coroutine-prepare', text))
        with self.assertRaisesRegex(ValueError, 'card'):
            self.check('coroutine-prepare', text.replace('103', '104'))

    def test_stage_requires_target_member_identity(self):
        output = ('put completed as JOB 111: '
                  'workarea/co5-production/coroutin-prepared.asm -> '
                  'HERC02.BCPL.BOOT.ASM(COROUTIN)\n')
        self.assertIsNone(self.check('coroutine-stage', output))
        with self.assertRaisesRegex(ValueError, 'stage receipt'):
            self.check('coroutine-stage', output.replace('(COROUTIN)', '(BLIB)'))

    def test_oracle_checks_jobreceipt_revision_and_21_records(self):
        rel = (gate.ORACLE_ROOT / '20261115T235200Z-test')
        path = self.root / rel / 'result.json'
        path.parent.mkdir(parents=True)
        evidence = {
            'status': 'PASS', 'git_head': self.git,
            'compiler_job': '321', 'native_job': '322',
            'installed_objects_modified': False,
            'linkage': 'installed BOOT_OBJ(BCPLMAIN/BCPLCO/COROUTIN)',
            'steps': {'ASMA': 0, 'LKED': 0, 'GO': 0},
            'bcpl_records': ['CO3BCPL MADE'] +
                            ['CO3BCPL TEST'] * 19 + ['CO3BCPL PASS'],
        }
        path.write_text(json.dumps(evidence))
        text = (f'INSTALLED COROUTINES PASS: compiler JOB 321, native JOB 322; '
                'IFOX/IEWL/GO all RC=0000\n'
                f'Installed coroutine evidence: {rel}\n')
        self.assertIn('"status": "PASS"', self.check('coroutine-oracle', text))
        evidence['git_head'] = 'b' * 40
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, 'revision'):
            self.check('coroutine-oracle', text)
        with self.assertRaisesRegex(ValueError, 'receipt missing'):
            self.check('coroutine-oracle', text.replace('PASS:', 'FAIL:'))


if __name__ == '__main__':
    unittest.main()
