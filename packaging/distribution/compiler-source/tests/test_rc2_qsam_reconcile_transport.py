"""Offline tests: reconcile saved MVS JOB 9330 without MVS access."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/compiler-source/rc2-qsam-reconcile-transport.py'
spec = importlib.util.spec_from_file_location('ta2_reconcile', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReconcileTests(unittest.TestCase):
    def fixture(self):
        edited = set(('BCPL','BLIB','CG','CGHDR','PM','SYN','TRN','TRNHDR'))
        sources = {}
        rows = []
        expected = {}
        for name in mod.MEMBER_NAMES:
            detail = 'A |[]' if name in ('PM', 'SYN') else 'A |' if name in edited else 'ABC'
            raw = (name + '\n' + detail + '\n').encode('ascii')
            sources[name] = raw
            old = mod.fixed80(raw, {})
            mapped = mod.fixed80(raw, mod.READER_BYTES)
            o = {k: old[k] for k in ('count', 'trail', 'fnv', 'sum')}
            n = {k: mapped[k] for k in ('count', 'trail', 'fnv', 'sum')}
            expected[name] = {**o, 'git_sha256': hashlib.sha256(raw).hexdigest()}
            rows.append({'member':name,'expected':o,'observed':n,'match':o==n})
        receipt = {'candidate':'BCPL-0.1.0-rc2', 'population_jobs':[9325,9326],
                   'mvs_verification_job':9330, 'status':'mismatch',
                   'results':rows,'expected':expected}
        return receipt, sources, rows, 'GO steps all successful'

    def test_profile_bytes_and_blank_tail(self):
        data = mod.fixed80(b'|[]\n\n', mod.READER_BYTES)
        self.assertEqual(data['count'],2)
        self.assertEqual(data['trail'],1)
        raw = bytes([0x6a,0xad,0xbd])+b'\x40'*77 + b'\x40'*80
        h=0x811c9dc5
        for b in raw:
            h=((h^b)*16777619)&0xffffffff
        self.assertEqual(data['fnv'],h)
        self.assertEqual(data['sum'],sum(raw)&0xffffffff)
        self.assertEqual(data['sha256'],hashlib.sha256(raw).hexdigest())

    def test_expected_15_matches_with_7_original(self):
        out=mod.reconcile(*self.fixture())
        self.assertEqual(out['reader_profile_pass'],15)
        self.assertEqual(out['original_cp037_pass'],7)
        self.assertEqual(out['mvs_job'],9330)
        self.assertEqual(out['status'],'reader-profile-reconciled')
        self.assertIn('NOT literal CP037',out['important_limit'])
        self.assertTrue(all(x['reader_profile_match'] for x in out['members']))

    def test_wrong_or_missing_job_rejected(self):
        for field,value in (('mvs_verification_job',9331), ('population_jobs',[9325,0]),
                            ('candidate','BCPL-0.1.0-rc1'), ('status','pass')):
            receipt,sources,rows,summary=self.fixture()
            receipt[field]=value
            with self.subTest(field=field),self.assertRaises(mod.Refusal):
                mod.reconcile(receipt,sources,rows,summary)

    def test_original_report_disagrees(self):
        receipt,sources,rows,summary=self.fixture()
        altered=[dict(x) for x in rows]
        altered[0]['observed']={'count':1,'trail':1,'fnv':1,'sum':1}
        with self.assertRaisesRegex(mod.Refusal,'JES report'):
            mod.reconcile(receipt,sources,altered,summary)

    def test_original_cp037_receipt_tampered(self):
        receipt,sources,rows,summary=self.fixture()
        receipt['expected']['BCPL']['fnv']=0
        with self.assertRaisesRegex(mod.Refusal,'CP037 evidence'):
            mod.reconcile(receipt,sources,rows,summary)

    def test_frozen_source_changed_refused(self):
        receipt,sources,rows,summary=self.fixture()
        sources['BCPL']=b'BCPL\nA ||\n'
        with self.assertRaises(mod.Refusal):
            mod.reconcile(receipt,sources,rows,summary)

    def test_mvs_byte_mismatch_not_silently_accepted(self):
        receipt,sources,rows,summary=self.fixture()
        unexpected=rows[0]['observed'].copy()
        unexpected['fnv']^=1
        rows[0]['observed']=unexpected
        receipt['results'][0]['observed']=unexpected
        with self.assertRaisesRegex(mod.Refusal,'not reconciled'):
            mod.reconcile(receipt,sources,rows,summary)

    def test_incomplete_or_reordered_list_refused(self):
        receipt,sources,rows,summary=self.fixture()
        receipt['results']=receipt['results'][:-1]
        with self.assertRaises(mod.Refusal):
            mod.reconcile(receipt,sources,receipt['results'],summary)

    def test_source_encoding_invalid_rejected(self):
        for b in (b'', b'NO LF', b'\xff\n', b'OVER\r\n',
                  b'X'*81+b'\n',b'X\x00\n'):
            with self.subTest(b=b),self.assertRaises(mod.Refusal):
                mod.fixed80(b, mod.READER_BYTES)

    def test_empty_summary_rejected(self):
        receipt,sources,rows,_=self.fixture()
        with self.assertRaises(mod.Refusal):
            mod.reconcile(receipt,sources,rows,'')


if __name__=='__main__':
    unittest.main()
