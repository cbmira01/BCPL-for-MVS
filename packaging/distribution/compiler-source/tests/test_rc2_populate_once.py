"""Synthetic-only one-shot population guard checks; no MVS access."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/compiler-source/rc2-populate-cambsource-once.py'
spec = importlib.util.spec_from_file_location('ta2_cambsource_once', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
NAMES = ['BCPL','BLIB','CG','CGHDR','EDITMAIN','IOS','LIBHDR','PM',
         'SYN','SYNHDR','TRN','TRNHDR','MAKEOBJ','MAKELIB','PROGRAM']
PATHS = {n: 'richards-bcpltape/file-' + n for n in NAMES}
BEFORE = 'HERC02.BCPL.CAMBRIDG.SOURCE:\n    (empty)\n'
AFTER = 'HERC02.BCPL.CAMBRIDG.SOURCE:\n' + ''.join('    '+m+'\n' for m in NAMES)
RECEIPT = ("JOB 9412: batch 1/2 CAMB_SOURCE (8 members), 2.1s\n"
           "JOB 9413: batch 2/2 CAMB_SOURCE (7 members), 1.4s\n"
           "populate completed: 15 ready member(s) written\n")
CANON = {'datasets': {'CAMB_SOURCE': {'dsn':'BCPL.CAMBRIDG.SOURCE', 'type':'pds',
          'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800, 'populate':True,
          'members': PATHS}}}
ACTIVE = {'mvs':{'hlq':'HERC02'},'datasets':CANON['datasets'],
          'text':{'host_encoding':'utf-8','mvs_encoding':'cp037','conversion_errors':'strict'}}
MANIFEST={'datasets': [None]*20 + [{'members':NAMES}]}


def result(text, rc=0, stderr=''):
    return SimpleNamespace(stdout=text, returncode=rc, stderr=stderr)


class PopulationOnce(unittest.TestCase):
    def setUp(self):
        (ROOT / 'workarea').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='ta2-once-', dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.messages = []
        self.plan = '\n'.join(f'{mod.MEMBER:<9} {n:<8} <- {p}' for n,p in PATHS.items()) + \
            '\nDry run: 15 ready member(s) would be written.\n'
        self.commands = []

    def invoke(self, *, before=BEFORE, populate=RECEIPT, pop_rc=0,
               after=AFTER, failure_dry=False):
        inspection = SimpleNamespace(
            source_manifest=lambda:(MANIFEST,CANON),
            verify_sources=lambda *args: ([(n,1) for n in NAMES],
                                         [NAMES[:8],NAMES[8:]]),
            inspect_listing=lambda s,n: 'empty' if s==BEFORE else
                                          'complete' if s==AFTER else 'partial')
        core = SimpleNamespace(load_config=lambda:ACTIVE)
        def module(name, path):
            return core if 'dspal_core' in name else inspection
        def command(args, **kwargs):
            self.commands.append(tuple(args))
            if args[:3] == ['git','branch','--show-current']:
                return result('main\n')
            if '--dry-run' in args:
                return result(self.plan if not failure_dry else 'invalid\n')
            if args[-2:] == ['ls','CAMB_SOURCE']:
                return result(before if sum(x[-2:]==('ls','CAMB_SOURCE') for x in self.commands)==1 else after)
            if args[-2:] == ['CAMB_SOURCE','--batch']:
                return result(populate,pop_rc)
            raise AssertionError('unknown command '+repr(args))
        with patch.object(mod,'WORK',self.work), patch.object(mod,'ATTEMPT',self.work/'attempt'), \
             patch.object(mod,'module',side_effect=module), patch.object(mod,'command',side_effect=command):
            return mod.run()

    def test_accepted_once_and_original_evidence(self):
        self.assertEqual(self.invoke(),0)
        self.assertEqual(len(self.commands),5)
        attempt=self.work/'attempt'
        self.assertEqual((attempt/'before-members.txt').read_text(),BEFORE)
        self.assertEqual((attempt/'after-members.txt').read_text(),AFTER)
        self.assertEqual((attempt/'populate.stdout.txt').read_text(),RECEIPT)
        self.assertIn('record content', (attempt/'directory-verified.txt').read_text())
        with patch.object(mod,'WORK',self.work),patch.object(mod,'ATTEMPT',attempt),\
             self.assertRaisesRegex(mod.Refusal,'already reserved'):
            self.invoke()

    def test_nonempty_read_only_refusal_no_marker(self):
        with self.assertRaisesRegex(mod.Refusal,'not empty'):
            self.invoke(before=AFTER)
        self.assertFalse((self.work/'attempt').exists())
        self.assertFalse(any(x[-2:]==('CAMB_SOURCE','--batch') for x in self.commands))

    def test_dry_plan_drift_no_mvs_job(self):
        with self.assertRaisesRegex(mod.Refusal,'dry-run does not match'):
            self.invoke(failure_dry=True)
        self.assertFalse((self.work/'attempt').exists())
        self.assertEqual(len(self.commands),2)

    def test_failed_first_or_second_job_persists_marker(self):
        with self.assertRaisesRegex(mod.Refusal,'MVS populate failed'):
            self.invoke(pop_rc=2,populate='JOB 9412 failed\n')
        self.assertTrue((self.work/'attempt'/'populate.stdout.txt').exists())
        self.assertFalse((self.work/'attempt'/'after-members.txt').exists())

    def test_unexpected_success_receipt_refused_no_retry(self):
        with self.assertRaisesRegex(mod.Refusal,'both approved batches'):
            self.invoke(populate='populate completed: 15 ready member(s) written\n')
        self.assertTrue((self.work/'attempt'/'attempt.txt').is_file())

    def test_post_write_directory_mismatch_persists_marker(self):
        with self.assertRaisesRegex(mod.Refusal,'exact 15-member'):
            self.invoke(after=BEFORE)
        self.assertTrue((self.work/'attempt'/'after-members.txt').is_file())
        self.assertFalse((self.work/'attempt'/'directory-verified.txt').exists())

    def test_effective_config_rejects_unsafe_source_override(self):
        modified=dict(ACTIVE)
        modified['datasets']={'CAMB_SOURCE':{**CANON['datasets']['CAMB_SOURCE'],
                                               'members':{'CGA':'workarea/dev'}}}
        with self.assertRaisesRegex(mod.Refusal,'mapping differs'):
            mod.check_effective_config(CANON,modified)

    def test_population_summary_exact_two_jobs(self):
        self.assertEqual(mod.check_population_receipt(RECEIPT),[9412,9413])
        for s in ('',RECEIPT.replace('batch 2/2','batch 1/2'),
                  RECEIPT.replace('9413','9412'),
                  RECEIPT.replace('7 members','8 members')):
            with self.subTest(s=s),self.assertRaises(mod.Refusal):
                mod.check_population_receipt(s)

if __name__ == '__main__':unittest.main()
