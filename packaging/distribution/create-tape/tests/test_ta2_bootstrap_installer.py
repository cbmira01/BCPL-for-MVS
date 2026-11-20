"""Offline synthetic safety/contracts for TA.2 MVS-only bootstrap artifacts."""
from __future__ import annotations

from copy import deepcopy
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-bootstrap-installer'
loader = SourceFileLoader('ta2_bt_material_test', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


def sample():
    rows = [
        {'sequence': 1, 'kind': 'sequential_text', 'generator': 'bootstrap_fb80',
         'target_dcb': {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}},
        {'sequence': 2, 'kind': 'pds_unload', 'generator': 'installer_pds',
         'target_dcb': mod.FB}]
    for n in range(3, 21):
        members = ['ICINT19'] if n == 12 else [f'M{j:07d}' for j in range(7)]
        if n == 3:
            members += [f'EX{j:06d}' for j in range(7)]
        rows.append({'sequence': n, 'kind': 'pds_unload', 'transfer': 'iebcopy_unload',
                     'dspal_key': 'MR10_LOAD' if n == 12 else
                                  'DIST_DOCS' if n == 3 else f'LIB{n:04d}',
                     'target_dcb': mod.LOAD if n == 12 else mod.FB,
                     'target_dsn_template': f'{{HLQ}}.BCPL.TEST.LIB{n:04d}',
                     'members': members})
    design = {'schema_version': 1, 'phase': 'design', 'datasets': rows}
    candidate = deepcopy(design)
    candidate.update({'phase': 'candidate',
                      'release': {'candidate_id': 'SYNTHETIC', 'version': '0.0.0-test',
                                  'source_commit': 'a'*40, 'native_compiler': 'absent'},
                      'volume': {'format': 'aws', 'labeling': 'SL', 'volser': 'BC1234'}})
    return candidate, design


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.candidate, self.design = sample()
        self.work = ROOT / 'workarea'
        self.work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.work)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old = mod.WORKAREA
        mod.WORKAREA = self.root
        self.addCleanup(setattr, mod, 'WORKAREA', self.old)

    def test_exact_canonical_inventory(self):
        self.assertEqual(len(mod.validate(self.candidate, self.design)), 20)
        self.assertEqual(sum(len(x['members']) for x in self.candidate['datasets'][2:]), 127)

    def test_manifest_changed_member_refused(self):
        self.candidate['datasets'][3]['members'] = ['SOMETHIN']
        with self.assertRaisesRegex(mod.Refusal, 'member selection'):
            mod.render(self.candidate, self.design)

    def test_load_module_dcb_remains_u(self):
        self.candidate['datasets'][11]['target_dcb'] = mod.FB
        with self.assertRaisesRegex(mod.Refusal, 'BT0012'):
            mod.render(self.candidate, self.design)

    def test_missing_release_identity_refused(self):
        self.candidate['release']['version'] = None
        with self.assertRaisesRegex(mod.Refusal, 'version'):
            mod.render(self.candidate, self.design)

    def test_wrong_tape_volser_refused(self):
        self.candidate['volume']['volser'] = 'BTA102'
        with self.assertRaisesRegex(mod.Refusal, 'VOLSER'):
            mod.render(self.candidate, self.design)

    def test_wrong_native_compiler_status_refused(self):
        self.candidate['release']['native_compiler'] = 'included'
        with self.assertRaisesRegex(mod.Refusal, 'compiler-absent'):
            mod.render(self.candidate, self.design)

    def test_missing_dataset_refused(self):
        self.candidate['datasets'].pop()
        with self.assertRaisesRegex(mod.Refusal, '20 ordered'):
            mod.render(self.candidate, self.design)

    def test_unsafe_target_dsn_template_refused(self):
        self.candidate['datasets'][2]['target_dsn_template'] = 'HERC02.BCPL.OVERRIDE'
        with self.assertRaisesRegex(mod.Refusal, 'template'):
            mod.render(self.candidate, self.design)

    def test_bootstrap_80_byte_ebcdic_records(self):
        files = mod.render(self.candidate, self.design)
        raw = files['BT0001.ebcdic-fb80']
        self.assertEqual(len(raw) % 80, 0)
        rows = [raw[i:i+80].decode('cp037') for i in range(0,len(raw),80)]
        self.assertIn('BCPL.BT0012', ''.join(rows))
        self.assertIn('BC1234', ''.join(rows))
        self.assertIn('BCPL.BT0001', ''.join(rows))
        self.assertIn('ABSENT', ''.join(rows))
        self.assertEqual(raw, mod.fb80(files['BT0001.txt'].decode('ascii')))

    def test_manifest_drives_twenty_logical_names(self):
        text = mod.render(self.candidate, self.design)['BT0001.txt'].decode()
        for n in range(1,21):
            self.assertEqual(sum(line.startswith(f'BCPL.BT{n:04d}  ') for line in text.splitlines()), 1)

    def test_bootstrap_read_jobs_mvs_only(self):
        files = mod.render(self.candidate, self.design)
        for n in (1, 2):
            deck = files[f'BOOTREAD{n}.jcl'].decode()
            self.assertIn(f'LABEL=({n},SL)', deck)
            self.assertIn(f'BCPL.BT000{n}', deck)
            self.assertIn('VOL=SER=BC1234', deck)
            self.assertNotIn('HERC02',deck)
            self.assertIn('UNIT=<TAPE>',deck)
            mod.card_lines(deck.splitlines(), jcl=True)
        self.assertIn('DISP=(NEW,CATLG,DELETE)',files['BOOTREAD2.jcl'].decode())

    def test_installer_has_four_members_with_fb80(self):
        files = mod.render(self.candidate,self.design)
        for name in ('INSTALL','DATASETS','RELEASE','RESTORE'):
            self.assertIn('BT0002-'+name+'.txt',files)
            raw = files['BT0002-'+name+'.ebcdic-fb80']
            self.assertEqual(len(raw)%80,0)
            self.assertEqual(raw,mod.fb80(files['BT0002-'+name+'.txt'].decode()))

    def test_restorer_18_steps_and_load_dcb(self):
        jcl = mod.render(self.candidate,self.design)['BT0002-RESTORE.txt'].decode()
        self.assertEqual(jcl.count(' EXEC PGM=IEBCOPY'),18)
        self.assertEqual(jcl.count(' COPY OUTDD=OUTPDS,INDD=INTAPE'),18)
        self.assertEqual(jcl.count('DISP=(NEW,CATLG,DELETE)'),18)
        self.assertEqual(jcl.count('RECFM=U'),1)
        self.assertEqual(jcl.count('RECFM=FB'),17)
        self.assertNotIn('HERC02',jcl)
        self.assertNotIn('DD DISP=MOD',jcl)
        self.assertEqual(jcl.count('UNIT=<DASD>'),18)
        self.assertEqual(jcl.count('UNIT=<TAPE>'),18)
        self.assertEqual(jcl.count('LABEL=('),18)

    def test_no_mvs_submission_or_unapproved_allocation(self):
        files = mod.render(self.candidate,self.design)
        for name,data in files.items():
            if name.endswith('.jcl') or name == 'BT0002-RESTORE.txt':
                self.assertIn('<TAPE>',data.decode())
                self.assertIn('<',data.decode())
                self.assertNotIn('JOB (',data.decode())

    def test_release_hash_receipt(self):
        files = mod.render(self.candidate,self.design)
        manifest = json.loads(files['materials.json'])
        self.assertEqual(manifest['status'],'OFFLINE_MATERIALS_NOT_MVS_ACCEPTED')
        for name, raw in files.items():
            if name != 'materials.json':
                self.assertEqual(manifest['files_sha256'][name],hashlib.sha256(raw).hexdigest())

    def test_exclusive_no_overwrite(self):
        files=mod.render(self.candidate,self.design)
        target=self.root/'testkit'
        mod.write_new(target,files)
        self.assertEqual((target/'materials.json').read_bytes(),files['materials.json'])
        with self.assertRaises(FileExistsError): mod.write_new(target,files)

    def test_outside_repo_workarea_refused(self):
        with self.assertRaisesRegex(mod.Refusal, 'workarea'):
            mod.write_new(self.work/'bad',mod.render(self.candidate,self.design))

    def test_jcl_card_validation_rejects_overwide(self):
        with self.assertRaisesRegex(mod.Refusal,'column 71'):
            mod.card_lines(['//ALONG  DD ' + 'X'*65],jcl=True)

    def test_identity_injection_refused(self):
        self.candidate['release']['candidate_id']='INJECT\n//JOB'
        with self.assertRaisesRegex(mod.Refusal,'candidate_id'):
            mod.render(self.candidate,self.design)

    def test_incorrect_schema_refused(self):
        self.candidate['schema_version']=2
        with self.assertRaisesRegex(mod.Refusal,'schema-v1'):
            mod.render(self.candidate,self.design)


if __name__ == '__main__':
    unittest.main()
