"""Offline mock MVS evidence reconciliation; no real JES/DASD/tape use."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT/'tools/distribution/reconcile-ta0-binary-evidence.py'
spec = importlib.util.spec_from_file_location('reconcile', SRC)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

KEYS = {
    'EXT_OBJ': ['BCPLDEMO','BCPLTIME','BCPLQSAM'],
    'MR10_OBJ': ['ICINT19'],
    'BOOT_OBJ': ['BCPLMAIN','BCPLMEM','BCPLBYTE','BCPLAPT','BCPLIO',
                 'BCPLRGS','BCPLREG','BLIB','BCPLCO','COROUTIN'],
}
COUNTS = [10,12,159,221,76,18,3,7,150,57,3,132,22,32]
assert sum(COUNTS) == 902


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


class FakeDecoder:
    def __init__(self):
        self.data = {}
    def load_evidence(self, folder):
        receipt = mod.js(folder/'receipt.json')
        report = mod.read(folder/'job-report.txt')
        pins = {'job-report.txt': sha(report), 'printer-window.raw': sha(mod.read(folder/'printer-window.raw'))}
        if receipt['sha256']['job-report.txt'] != pins['job-report.txt']:
            raise ValueError('UNVERIFIED_REPORT')
        return receipt, report.decode('ascii'), pins
    def decode_multi(self, report, *, job, jobname, members):
        member = members[0]
        if report != member + ':' + str(job):
            raise ValueError('INCORRECT_PRINT_CONTENT')
        return {member: self.data[(member, job)]}


class FakePilot:
    CORE = Path('not-needed')
    def import_file(self, path, name):
        return type('Core', (), {'load_config': lambda self: {}})()


class FakeTriage:
    def __init__(self):self.state = 'SAVED_EXECUTION_VERIFIED'; self.job = '9061'
    def diagnose(self, *args, **kwargs):
        return {'state': self.state, 'preflight': 'OK_NOW', 'job': self.job}


class EvidenceFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'workarea').mkdir()
        self.base = self.root/'workarea'/'ta0-mvs-evidence-20261117'
        self.base.mkdir()
        self.manifest = self.root/'manifest.yaml'
        self.ledger = self.root/'ledger.md'
        entries = []
        for key, members in KEYS.items():
            entries.append({'dspal_key': key, 'members': members,
              'target_dcb': {'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800}})
        self.manifest.write_text(yaml.safe_dump({'phase':'design','datasets':entries}))
        self.decoder = FakeDecoder()
        self.triage = FakeTriage()
        self.pilot = FakePilot()
        self.sources=[]
        ledger=['| Source | Member | JES job | Observed FB80 records | Decoded print SHA-256 |',
                '| --- | --- | ---: | ---: | --- |']
        i=0
        for key,members in KEYS.items():
            folder = self.base / mod.DIRS[key]
            folder.mkdir()
            items=[]
            for n, member in enumerate(members, 1):
                records=COUNTS[i]; job=9046+i;i+=1
                source=(member.encode().ljust(80,b'\x40'))*records
                meta={'member':member,'record_count':records,'byte_count':len(source),
                      'sha256_of_decoded_print':sha(source), 'record_length':80,
                      'job':job,'block_end_records':[records],
                      'expected_records_supplied':False, 'repeated_page_headings':0,
                      'qualification':'PRINT-ONLY; NO INDEPENDENT DASD BYTE OR SOURCE PROVENANCE'}
                self.decoder.data[(member,job)] = source,meta
                name=f'{n:02d}-{member}'
                pilot_dir=folder/f'{name}-pilot';pilot_dir.mkdir()
                decoded_dir=folder/f'{name}-decoded';decoded_dir.mkdir()
                report=(f'{member}:{job}').encode('ascii')
                (pilot_dir/'job-report.txt').write_bytes(report)
                (pilot_dir/'printer-window.raw').write_bytes(b'printer')
                pilot_receipt={'dataset_key':key,'requested_members':[member],
                               'job':job,'jobname':f'TA0{mod.KEYS[key]}{n:03d}',
                               'source_dataset':'HERC02.BCPL.OBJ',
                               'sha256':{'job-report.txt':sha(report)}}
                dump(pilot_dir/'receipt.json',pilot_receipt)
                decoded_receipt={'source_job':job,'source_dataset':'HERC02.BCPL.OBJ',
                    'source_receipt_sha256':sha((pilot_dir/'receipt.json').read_bytes()),
                    'source_report_sha256':sha(report), 'source_printer_window_sha256':sha(b'printer'),
                    'members':[meta]}
                dump(decoded_dir/'decode-receipt.json',decoded_receipt)
                (decoded_dir/f'{member}.fb80').write_bytes(source)
                items.append({'member':member,'job':job,'jobname':pilot_receipt['jobname'],
                    'record_count_from_print':records,'bytes_from_print':len(source),
                    'sha256_of_decoded_print':sha(source),
                    'pilot_receipt_sha256':sha((pilot_dir/'receipt.json').read_bytes()),
                    'decode_receipt_sha256':sha((decoded_dir/'decode-receipt.json').read_bytes()),
                    'pilot_directory':pilot_dir.name, 'decoded_directory':decoded_dir.name})
                self.sources.append((key,member,job,records,sha(source),pilot_dir,decoded_dir))
                ledger.append(f'| {key} | {member} | {job} | {records} | `{sha(source)}` |')
            dump(folder/'panel-receipt.json',{'phase':'TA.0 SINGLE-MEMBER FB80 PANEL — PRINTER-DECODE EVIDENCE ONLY',
                 'dataset_key':key,'selected_members':members,'completed':len(members),'members':items})
        self.ledger.write_text('\n'.join(ledger)+'\n')
        for name in ('ta0-mr10-load-iehlist','ta0-mr10-load-directory-reviewed','ta0-mr10-load-execution'):
            (self.base/name).mkdir()
        dump(self.base/'ta0-mr10-load-directory-reviewed'/'directory-review.json', {'job':9060})
        self.patches=[patch.object(mod,'ROOT',self.root),patch.object(mod,'MANIFEST',self.manifest),
                      patch.object(mod,'LEDGER',self.ledger)]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)

    def check(self):
        return mod.reconcile(self.base, load_module=self.decoder,
                             exec_module=self.pilot, triage_module=self.triage)

    def test_all_four_evidence_groups_reconciled(self):
        result=self.check()
        self.assertEqual(result['fb80_objects'],14)
        self.assertEqual(result['fb80_records'],902)
        self.assertEqual(result['fb80_bytes'],72160)
        self.assertEqual(result['load_execution_job'],9061)
        self.assertEqual(len(result['members']),14)
        self.assertIn('NOT RELEASE ACCEPTANCE',result['phase'])

    def test_recovered_ext_receipt_allowed(self):
        f=self.base/mod.DIRS['EXT_OBJ']/'panel-receipt.json'
        obj=mod.js(f);obj['phase']='TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY'
        (f.parent/'failure.json').write_bytes(b'RECOVERY LOG PRESERVED')
        obj['original_failure_sha256']=sha((f.parent/'failure.json').read_bytes())
        obj['recovery']='Re-decoded existing verified JES reports; ZERO new MVS jobs.'
        dump(f,obj)
        self.check()

    def test_managed_selection_not_duplicate(self):
        inventory=yaml.safe_load(self.manifest.read_text());inventory['datasets'][0]['members'].append('BCPLDEMO')
        self.manifest.write_text(yaml.safe_dump(inventory))
        with self.assertRaisesRegex(mod.ReconcileError,'MANIFEST_MEMBER_LIST_INVALID'):self.check()

    def test_unexpected_order_fails(self):
        folder=self.base/mod.DIRS['EXT_OBJ'];p=folder/'panel-receipt.json';obj=mod.js(p)
        obj['selected_members']=obj['selected_members'][::-1];dump(p,obj)
        with self.assertRaisesRegex(mod.ReconcileError,'PANEL_IDENTITY_MISMATCH'):self.check()

    def test_changed_published_job_fails(self):
        self.ledger.write_text(self.ledger.read_text().replace('BCPLDEMO | 9046','BCPLDEMO | 9071'))
        with self.assertRaisesRegex(mod.ReconcileError,'PUBLISHED_MVS_READBACK_MISMATCH'):self.check()

    def test_modified_pilot_pin_fails(self):
        self.sources[0][5].joinpath('job-report.txt').write_text('TAMPERED')
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_REPORT'):self.check()

    def test_altered_decoded_binary_fails(self):
        key,member,job,records,hashhex,_,folder=self.sources[0]
        folder.joinpath(member+'.fb80').write_bytes(b'X'*(records*80))
        with self.assertRaisesRegex(mod.ReconcileError,'DECODED_BINARY_MISMATCH'):self.check()

    def test_tampered_member_receipt_fails(self):
        folder=self.sources[0][6];p=folder/'decode-receipt.json';obj=mod.js(p)
        obj['members'][0]['record_count']=999;dump(p,obj)
        with self.assertRaisesRegex(mod.ReconcileError,'PANEL_RECEIPT_MISMATCH'):self.check()

    def test_bad_load_job_blocks(self):
        self.triage.job='9020'
        with self.assertRaisesRegex(mod.ReconcileError,'ICINT19_EXECUTABLE_EVIDENCE_NOT_VERIFIED'):self.check()

    def test_modified_recovery_receipt_blocks(self):
        folder=self.base/mod.DIRS['EXT_OBJ'];p=folder/'panel-receipt.json';obj=mod.js(p)
        obj['phase']='TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY'
        obj['original_failure_sha256']='0'*64
        obj['recovery']='Re-decoded existing verified JES reports; ZERO new MVS jobs.'
        dump(folder/'failure.json', {})
        dump(p,obj)
        with self.assertRaisesRegex(mod.ReconcileError,'RECOVERY_PROVENANCE_MISMATCH'):self.check()

    def test_wrong_load_directory_job_blocks(self):
        p=self.base/'ta0-mr10-load-directory-reviewed'/'directory-review.json'
        dump(p,{'job':9999})
        with self.assertRaisesRegex(mod.ReconcileError,'LOAD_DIRECTORY_JOB_MISMATCH'):self.check()

    def test_invalid_execution_blocks(self):
        self.triage.state='RECEIPT_ALREADY_PRESENT'
        with self.assertRaisesRegex(mod.ReconcileError,'ICINT19_EXECUTABLE_EVIDENCE_NOT_VERIFIED'):self.check()

    def test_workarea_boundary(self):
        with self.assertRaises(ValueError):
            mod.reconcile(self.root,load_module=self.decoder,exec_module=self.pilot,
                          triage_module=self.triage)

    def legacy_receipt(self, index):
        # Preserve the actual old schema from before the pagination fix:
        # all metadata keys except repeated_page_headings.
        key, member, job, count, h, pilot_dir, decoded_dir = self.sources[index]
        path = decoded_dir/'decode-receipt.json'
        saved = mod.js(path)
        self.assertEqual(saved['members'][0]['repeated_page_headings'], 0)
        del saved['members'][0]['repeated_page_headings']
        dump(path, saved)
        panel_path = decoded_dir.parent/'panel-receipt.json'
        panel = mod.js(panel_path)
        for item in panel['members']:
            if item['member'] == member:
                item['decode_receipt_sha256'] = sha(path.read_bytes())
                break
        else:
            self.fail('no selected panel member')
        dump(panel_path, panel)
        return path, decoded_dir, saved

    def test_historical_pre_pagination_receipts_accepted_without_rewriting(self):
        self.legacy_receipt(0)   # BCPLDEMO, JOB 9046
        self.legacy_receipt(1)   # BCPLTIME, JOB 9047
        before = {p.relative_to(self.base).as_posix(): p.read_bytes()
                  for p in self.base.rglob('*') if p.is_file()}
        result = self.check()
        self.assertEqual(result['historical_pre_page_receipts'], 2)
        self.assertEqual(result['members'][0]['decode_receipt_schema'], 'PRE_PAGE_V1')
        self.assertEqual(result['members'][1]['decode_receipt_schema'], 'PRE_PAGE_V1')
        self.assertEqual(result['members'][2]['decode_receipt_schema'], 'PAGE_AWARE_V2')
        self.assertEqual(result['fb80_bytes'], 72160)
        self.assertEqual({p.relative_to(self.base).as_posix(): p.read_bytes()
                          for p in self.base.rglob('*') if p.is_file()}, before)

    def test_recovered_ext_panel_and_legacy_receipts(self):
        self.legacy_receipt(0)
        self.legacy_receipt(1)
        f = self.base/mod.DIRS['EXT_OBJ']/'panel-receipt.json'
        obj=mod.js(f)
        obj['phase']='TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY'
        (f.parent/'failure.json').write_bytes(b'RECOVERY LOG PRESERVED')
        obj['original_failure_sha256']=sha((f.parent/'failure.json').read_bytes())
        obj['recovery']='Re-decoded existing verified JES reports; ZERO new MVS jobs.'
        dump(f, obj)
        self.assertEqual(self.check()['historical_pre_page_receipts'], 2)

    def test_historical_receipt_cannot_hide_real_page_continuation(self):
        self.legacy_receipt(0)
        key, member, job, count, h, pilot_dir, decoded_dir = self.sources[0]
        binary, new_meta = self.decoder.data[(member, job)]
        new_meta['repeated_page_headings'] = 2
        with self.assertRaisesRegex(mod.ReconcileError,
                                    'DECODE_RECEIPT_METADATA_MISMATCH_EXT_OBJ_BCPLDEMO'):
            self.check()

    def test_historical_receipt_changed_record_count_rejected_after_repin(self):
        path, decoded_dir, saved = self.legacy_receipt(0)
        saved['members'][0]['record_count'] = 11
        dump(path, saved)
        panel_path = decoded_dir.parent/'panel-receipt.json'
        panel = mod.js(panel_path)
        panel['members'][0]['decode_receipt_sha256'] = sha(path.read_bytes())
        dump(panel_path, panel)
        with self.assertRaisesRegex(mod.ReconcileError,
                                    'DECODE_RECEIPT_METADATA_MISMATCH_EXT_OBJ_BCPLDEMO'):
            self.check()

    def test_historical_receipt_missing_other_metadata_field_rejected(self):
        path, decoded_dir, saved = self.legacy_receipt(0)
        del saved['members'][0]['job']
        dump(path, saved)
        panel_path = decoded_dir.parent/'panel-receipt.json'
        panel = mod.js(panel_path)
        panel['members'][0]['decode_receipt_sha256'] = sha(path.read_bytes())
        dump(panel_path, panel)
        with self.assertRaisesRegex(mod.ReconcileError,
                                    'DECODE_RECEIPT_METADATA_MISMATCH_EXT_OBJ_BCPLDEMO'):
            self.check()

    def test_new_receipt_page_count_tampering_rejected_after_repin(self):
        path = self.sources[0][6]/'decode-receipt.json'
        saved = mod.js(path)
        saved['members'][0]['repeated_page_headings'] = 7
        dump(path, saved)
        panel_path = path.parent.parent/'panel-receipt.json'
        panel=mod.js(panel_path)
        panel['members'][0]['decode_receipt_sha256']=sha(path.read_bytes())
        dump(panel_path, panel)
        with self.assertRaisesRegex(mod.ReconcileError,
                                    'DECODE_RECEIPT_METADATA_MISMATCH_EXT_OBJ_BCPLDEMO'):
            self.check()

    def test_legacy_source_report_pin_tampering_rejected(self):
        path, decoded_dir, saved = self.legacy_receipt(0)
        saved['source_report_sha256'] = '0'*64
        dump(path, saved)
        panel_path = decoded_dir.parent/'panel-receipt.json'
        panel = mod.js(panel_path)
        panel['members'][0]['decode_receipt_sha256'] = sha(path.read_bytes())
        dump(panel_path, panel)
        with self.assertRaisesRegex(mod.ReconcileError,
                                    'DECODE_RECEIPT_SOURCE_MISMATCH_EXT_OBJ_BCPLDEMO'):
            self.check()

    def test_no_side_effects(self):
        before={p.relative_to(self.base).as_posix():p.read_bytes()
                for p in self.base.rglob('*') if p.is_file()}
        self.check()
        after={p.relative_to(self.base).as_posix():p.read_bytes()
                for p in self.base.rglob('*') if p.is_file()}
        self.assertEqual(before,after)


if __name__ == '__main__':
    unittest.main()
