"""TA.0 single-member JES panel: all test operations use isolated mocks."""
from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[4] / 'tools/distribution/run-iebptpch-single-panel.py'
SPEC = importlib.util.spec_from_file_location('ta0_single_panel', SRC)
assert SPEC and SPEC.loader
panel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(panel)


class FakePrep:
    MANIFEST = 'manifest'
    DSPAL = 'dspal'
    def __init__(self):
        self.selected = ['BCPLDEMO', 'BCPLTIME', 'BCPLQSAM']
        self.selected_by_key = {
            'EXT_OBJ': self.selected,
            'MR10_OBJ': ['ICINT19'],
            'BOOT_OBJ': ['BCPLMAIN', 'BLIB', 'COROUTIN'],
        }
        self.fail_on = None

    def load_yaml(self, path):
        if path == self.MANIFEST:
            return {'datasets': [
                {'dspal_key': key, 'members': names}
                for key, names in self.selected_by_key.items()]}
        return {'datasets': {}}

    def make_job_body(self, manifest, dspal, *, dataset_key, members, hlq):
        if members[0] not in self.selected_by_key[dataset_key] or members[0] == self.fail_on:
            raise ValueError('not in selected manifest')
        suffix = {'EXT_OBJ': 'BCPL.EXT.OBJ',
                  'MR10_OBJ': 'BCPL.MR10KIT.OBJ',
                  'BOOT_OBJ': 'BCPL.BOOT.OBJ'}[dataset_key]
        return (f'//SYSUT1   DD DSN=HERC02.{suffix},DISP=SHR\n'
                '         PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1\n'
                f'         MEMBER NAME={members[0]}\n')


class FakeCore:
    def __init__(self):
        self.config = {'mvs': {'hlq': 'HERC02'}, 'datasets': {
            'EXT_OBJ': {'dsn': 'BCPL.EXT.OBJ', 'dsorg': 'PO', 'recfm': 'FB',
                        'lrecl': 80, 'blksize': 800},
            'MR10_OBJ': {'dsn': 'BCPL.MR10KIT.OBJ', 'dsorg': 'PO', 'recfm': 'FB',
                         'lrecl': 80, 'blksize': 800},
            'BOOT_OBJ': {'dsn': 'BCPL.BOOT.OBJ', 'dsorg': 'PO', 'recfm': 'FB',
                         'lrecl': 80, 'blksize': 800}}}

    def load_config(self):
        return self.config

    def full_dsn(self, config, source):
        return config['mvs']['hlq'] + '.' + source['dsn']


class FakePilot:
    def __init__(self):
        self.calls = []
        self.fail_at = None

    def run_one(self, core, prep, *, key, members, output, jobname):
        index = len(self.calls)
        self.calls.append((key, members[:], output, jobname))
        output.mkdir(mode=0o700)
        (output / 'cursor.json').write_text('{}\n')
        if self.fail_at == index:
            raise RuntimeError('mocked JES submission failure')
        job = 9100 + index
        (output / 'receipt.json').write_text(json.dumps({'job':job}) + '\n')
        return {'job':job}


class FakeDecoder:
    def __init__(self, pilot):
        self.pilot = pilot
        self.calls = []
        self.fail_at = None
        self.mismatch = False

    def process(self, evidence, output, *, expected_counts):
        self.calls.append((evidence, output, expected_counts))
        index = len(self.calls) - 1
        if index == self.fail_at:
            raise ValueError('mocked unsafe JES report format')
        expected = self.pilot.calls[index][1][0]
        member = 'WRONG' if self.mismatch else expected
        output.mkdir(mode=0o700)
        (output / f'{expected}.fb80').write_bytes(b'\x00' * 80)
        (output / 'decode-receipt.json').write_text(json.dumps({'source_job':9100+index})+'\n')
        return {'source_job':9100 + index, 'members':[{
            'member':member, 'record_count':1, 'byte_count':80,
            'sha256_of_decoded_print': hashlib.sha256(b'\x00' * 80).hexdigest()}]}


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.out = self.base / 'panel'
        self.prep = FakePrep()
        self.core = FakeCore()
        self.pilot = FakePilot()
        self.decoder = FakeDecoder(self.pilot)

    def run_panel(self, members=None, key='EXT_OBJ', out=None):
        return panel.run_panel(self.prep, self.core, self.pilot, self.decoder,
                               key=key, members=members if members is not None else
                               ['BCPLTIME','BCPLQSAM'], output=out or self.out)

    def test_two_single_member_jobs_and_receipt(self):
        summary = self.run_panel()
        self.assertEqual(summary['completed'], 2)
        self.assertEqual([x[1] for x in self.pilot.calls], [['BCPLTIME'],['BCPLQSAM']])
        self.assertEqual([x[3] for x in self.pilot.calls], ['TA0E001','TA0E002'])
        self.assertEqual([x['job'] for x in summary['members']], [9100,9101])
        self.assertEqual(len(self.decoder.calls), 2)
        self.assertEqual([x[2] for x in self.decoder.calls], [[],[]])
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.out/'panel-receipt.json').stat().st_mode & 0o777, 0o600)
        receipt = json.loads((self.out/'panel-receipt.json').read_text())
        self.assertEqual(receipt, summary)
        self.assertFalse((self.out/'failure.json').exists())

    def test_hashes_point_to_actual_saved_receipts(self):
        result = self.run_panel()
        for entry in result['members']:
            self.assertEqual(entry['pilot_receipt_sha256'],
                             panel.file_sha256(self.out/entry['pilot_directory']/'receipt.json'))
            self.assertEqual(entry['decode_receipt_sha256'],
                             panel.file_sha256(self.out/entry['decoded_directory']/'decode-receipt.json'))

    def test_first_submission_failure_stops_without_retry(self):
        self.pilot.fail_at = 0
        with self.assertRaisesRegex(RuntimeError, 'mocked'):
            self.run_panel()
        self.assertEqual(len(self.pilot.calls), 1)
        marker = json.loads((self.out/'failure.json').read_text())
        self.assertEqual((marker['stage'],marker['failed_member'],marker['pilot_job']),
                         ('pilot','BCPLTIME',None))
        self.assertFalse((self.out/'panel-receipt.json').exists())

    def test_second_submission_failure_retains_first_without_retry(self):
        self.pilot.fail_at = 1
        with self.assertRaises(RuntimeError):
            self.run_panel()
        self.assertEqual(len(self.pilot.calls), 2)
        self.assertTrue((self.out/'01-BCPLTIME-decoded'/'decode-receipt.json').exists())
        marker = json.loads((self.out/'failure.json').read_text())
        self.assertEqual(marker['stage'], 'pilot')
        self.assertEqual(marker['failed_member'], 'BCPLQSAM')
        self.assertFalse((self.out/'panel-receipt.json').exists())

    def test_decoder_failure_preserves_mvs_receipt_no_retry(self):
        self.decoder.fail_at = 0
        with self.assertRaises(ValueError):
            self.run_panel()
        self.assertEqual(len(self.pilot.calls), 1)
        self.assertTrue((self.out/'01-BCPLTIME-pilot'/'receipt.json').exists())
        marker = json.loads((self.out/'failure.json').read_text())
        self.assertEqual((marker['stage'], marker['failed_member'], marker['pilot_job']),
                         ('decode','BCPLTIME',9100))

    def test_wrong_decoder_member_identity_fails_closed(self):
        self.decoder.mismatch = True
        with self.assertRaisesRegex(panel.PanelError, 'inconsistent member'):
            self.run_panel()
        self.assertEqual(len(self.pilot.calls),1)
        self.assertFalse((self.out/'panel-receipt.json').exists())

    def test_illegal_name_refuses_before_any_jobs(self):
        with self.assertRaisesRegex(panel.PanelError,'legal uppercase'):
            self.run_panel(['bcpltime'])
        self.assertFalse(self.out.exists())
        self.assertEqual(self.pilot.calls, [])

    def test_duplicate_name_refuses_before_any_jobs(self):
        with self.assertRaisesRegex(panel.PanelError, 'duplicate'):
            self.run_panel(['BCPLTIME','BCPLTIME'])
        self.assertEqual(self.pilot.calls, [])
        self.assertFalse(self.out.exists())

    def test_unselected_later_name_fails_preflight_before_first_job(self):
        with self.assertRaisesRegex(ValueError,'not in selected'):
            self.run_panel(['BCPLTIME','BADNAME'])
        self.assertEqual(self.pilot.calls, [])
        self.assertFalse(self.out.exists())

    def test_dcb_mismatch_refuses_before_any_jobs(self):
        self.core.config['datasets']['EXT_OBJ']['recfm'] = 'U'
        with self.assertRaisesRegex(panel.PanelError, 'source DCB'):
            self.run_panel()
        self.assertEqual(self.pilot.calls, [])

    def test_wrong_active_dsn_refuses_before_any_jobs(self):
        self.core.config['datasets']['EXT_OBJ']['dsn'] = 'BCPL.OTHER.OBJ'
        with self.assertRaisesRegex(panel.PanelError, 'source dataset differs'):
            self.run_panel()
        self.assertEqual(self.pilot.calls, [])

    def test_refuse_recfm_u_load_library(self):
        with self.assertRaisesRegex(panel.PanelError, 'three selected'):
            self.run_panel(key='MR10_LOAD')
        self.assertEqual(self.pilot.calls, [])

    def test_existing_output_never_overwritten(self):
        self.out.mkdir()
        with self.assertRaisesRegex(panel.PanelError, 'NEW private directory'):
            self.run_panel()
        self.assertEqual(list(self.out.iterdir()), [])
        self.assertEqual(self.pilot.calls, [])

    def test_relative_output_rejected(self):
        with self.assertRaisesRegex(panel.PanelError, 'NEW private directory'):
            self.run_panel(out=Path('relative-evidence'))
        self.assertEqual(self.pilot.calls, [])

    def test_output_in_checkout_refused(self):
        with self.assertRaisesRegex(panel.PanelError, 'NEW private directory'):
            self.run_panel(out=panel.ROOT / 'untracked-refused')
        self.assertEqual(self.pilot.calls, [])

    def test_all_selected_reads_canonical_manifest_not_hard_coded(self):
        names = panel.select_members(self.prep,key='EXT_OBJ', named=None, all_selected=True)
        self.assertEqual(names,self.prep.selected)
        self.prep.selected.append('BCPLDEC')
        self.assertEqual(panel.select_members(self.prep,key='EXT_OBJ',named=None,all_selected=True)[-1],
                         'BCPLDEC')

    def test_selection_mode_invalid(self):
        with self.assertRaisesRegex(panel.PanelError,'either'):
            panel.select_members(self.prep,key='EXT_OBJ',named=['BCPLTIME'],all_selected=True)
        with self.assertRaisesRegex(panel.PanelError,'either'):
            panel.select_members(self.prep,key='EXT_OBJ',named=None,all_selected=False)

    def test_preflight_does_not_write_any_files(self):
        panel.preflight(self.prep,self.core,key='EXT_OBJ',
                        members=['BCPLTIME','BCPLQSAM'],output=self.out)
        self.assertFalse(self.out.exists())

    def test_private_json_exclusive_creation(self):
        f = self.base / 'one.json'
        panel.safe_json(f, {'value':1})
        self.assertEqual(f.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            panel.safe_json(f, {'value':2})
        self.assertEqual(json.loads(f.read_text()),{'value':1})

    def test_all_selected_not_accepted_for_unselected_dataset(self):
        with self.assertRaises(panel.PanelError):
            panel.select_members(self.prep,key='MR10_LOAD',named=None,all_selected=True)

    def test_mr10_single_member_job_uses_distinct_jobname(self):
        result = self.run_panel(key='MR10_OBJ', members=['ICINT19'])
        self.assertEqual([e['member'] for e in result['members']], ['ICINT19'])
        self.assertEqual(self.pilot.calls[0][3], 'TA0M001')

    def test_boot_panel_all_selected_fixture(self):
        selected = panel.select_members(self.prep, key='BOOT_OBJ',
                                        named=None, all_selected=True)
        result = self.run_panel(key='BOOT_OBJ', members=selected)
        self.assertEqual(result['completed'], 3)
        self.assertEqual([x[3] for x in self.pilot.calls],
                         ['TA0B001', 'TA0B002', 'TA0B003'])

    def test_duplicate_preflight_works_for_other_dataset(self):
        with self.assertRaisesRegex(panel.PanelError, 'duplicate'):
            self.run_panel(key='BOOT_OBJ', members=['BLIB', 'BLIB'])
        self.assertEqual(self.pilot.calls, [])

    def test_live_source_dataset_mapping_for_mr10(self):
        panel.preflight(self.prep, self.core, key='MR10_OBJ',
                        members=['ICINT19'], output=self.out)
        self.assertFalse(self.out.exists())

    def test_too_many_selected_rejected_without_mvs(self):
        with self.assertRaisesRegex(panel.PanelError, 'one to twenty'):
            self.run_panel(members=['BCPLTIME']*21)
        self.assertEqual(self.pilot.calls, [])


if __name__ == '__main__':
    unittest.main()
