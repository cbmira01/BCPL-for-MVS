"""Offline synthetic fixtures; no MVS, media or JES execution."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
C = SourceFileLoader('ta1b_contract', str(ROOT / 'packaging/distribution/create-tape/scripts/ta1b-contract')).load_module()


def canonical_body():
    rows = ['//* CANONICAL MRREGRES CASE01\n']
    for step, prog in zip(C.STEP_NAMES, C.PROGRAMS):
        rows.append(f'//{step:<8} EXEC PGM={prog}\n')
        if prog == 'ICINT19':
            rows.append(f'//STEPLIB  DD DSN={C.SOURCE},DISP=SHR\n')
        rows.append('//*\n')
    return ''.join(rows)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        jcl = self.root/'packaging/distribution/create-tape/jcl'
        jcl.mkdir(parents=True)
        src = ROOT/'packaging/distribution/create-tape/jcl'
        for job in ('TA1BWRIT', 'TA1BREST'):
            (jcl/(job+'.jcl')).write_bytes((src/(job+'.jcl')).read_bytes())
        self.jcl = jcl
        self.fake = types.SimpleNamespace(
            SOURCE_BLOB=C.SOURCE_BLOB, STEPS=C.STEP_NAMES, GOLDEN=C.EXPECTED_RP,
            canonical_steps=lambda source, hlq, load_dsn: (canonical_body(), C.SOURCE_BLOB))

    def test_load_source_and_restore_contract(self):
        C.validate_tape_jobs(root=self.root)

    def test_unload_is_only_selected_icint19(self):
        data = C.file_cards('TA1BWRIT', root=self.root)
        self.assertEqual(data.count('SELECT MEMBER=(ICINT19)'), 1)
        self.assertNotIn('DSORG=PO,RECFM=U', '\n'.join(x for x in data.splitlines() if not x.startswith('//*')))

    def test_restore_new_pou_6144(self):
        data = C.file_cards('TA1BREST', root=self.root)
        self.assertIn('DCB=(DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144)', data)

    def replace(self, job, old, new):
        p = self.jcl/(job+'.jcl')
        src = p.read_text()
        self.assertIn(old, src)
        p.write_text(src.replace(old, new))

    def test_unload_wrong_volser_rejected(self):
        self.replace('TA1BWRIT', 'SER=BTA102', 'SER=BTA101')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_unload_wrong_tape_sequence_rejected(self):
        self.replace('TA1BWRIT', 'LABEL=(1,SL)', 'LABEL=(2,SL)')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_catalog_tape_refused(self):
        self.replace('TA1BWRIT', 'DISP=(NEW,KEEP,KEEP)', 'DISP=(NEW,CATLG,DELETE)')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_wrong_selected_member_refused(self):
        self.replace('TA1BWRIT', 'SELECT MEMBER=(ICINT19)', 'SELECT MEMBER=(BLIB)')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_new_only_restoration(self):
        self.replace('TA1BREST', 'DISP=(NEW,CATLG,DELETE)', 'DISP=OLD')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_wrong_load_dcb_refused(self):
        self.replace('TA1BREST', 'RECFM=U,LRECL=0,BLKSIZE=6144', 'RECFM=FB,LRECL=80,BLKSIZE=800')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_extra_unload_source_refused(self):
        self.replace('TA1BWRIT', '//SYSUT3   DD', '//HACK     DD DSN=SYS1.PARMLIB,DISP=SHR\n//SYSUT3   DD')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_JCL_with_job_card_rejected(self):
        self.replace('TA1BWRIT', '//UNLOAD   EXEC', '//X JOB 123\n//UNLOAD   EXEC')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_record_longer_than_80_rejected(self):
        self.replace('TA1BWRIT', ' COPY OUTDD=', (' ' * 82)+'COPY OUTDD=')
        with self.assertRaises(C.ContractError): C.validate_tape_jobs(root=self.root)

    def test_generated_go_uses_three_restored_steplibs(self):
        with mock.patch.object(C, 'git_blob', return_value=C.SOURCE_BLOB):
            body = C.go_body(canonical=b'synthetic', pilot=self.fake)
        self.assertEqual(body.count('DSN='+C.TARGET+',DISP=SHR'), 3)
        self.assertNotIn(C.SOURCE, body)
        self.assertEqual(tuple(x[0] for x in C.EXEC.findall(body)), C.STEP_NAMES)
        self.assertTrue(body.endswith('//\n'))

    def test_go_pin_disagreement(self):
        with self.assertRaisesRegex(C.ContractError, 'pin mismatch'):
            C.go_body(canonical=b'synthetic', pilot=self.fake)

    def test_go_legacy_steplib_retained_refused(self):
        self.fake.canonical_steps = lambda src, hlq, load_dsn: (canonical_body().replace('//STEPLIB','//BADLIB ',1), C.SOURCE_BLOB)
        with mock.patch.object(C, 'git_blob', return_value=C.SOURCE_BLOB):
            with self.assertRaisesRegex(C.ContractError, 'three original'):
                C.go_body(canonical=b'synthetic', pilot=self.fake)

    def test_go_contract_changed_refused(self):
        self.fake.GOLDEN = ('WRONG',)
        with mock.patch.object(C, 'git_blob', return_value=C.SOURCE_BLOB):
            with self.assertRaisesRegex(C.ContractError, 'contract has changed'):
                C.go_body(canonical=b'synthetic', pilot=self.fake)

    def test_go_duplicate_execution_refused(self):
        self.fake.canonical_steps = lambda s, hlq, load_dsn: (canonical_body()+'//R02 EXEC PGM=ICINT19\n', C.SOURCE_BLOB)
        with mock.patch.object(C, 'git_blob', return_value=C.SOURCE_BLOB):
            with self.assertRaisesRegex(C.ContractError, 'inconsistent'):
                C.go_body(canonical=b'synthetic', pilot=self.fake)

    def test_IEHLIST_source(self):
        body = C.directory_body(C.SOURCE, 'TSO003', 'SYSDA')
        self.assertIn('LISTPDS DSNAME='+C.SOURCE+',VOL=SYSDA=TSO003,FORMAT', body)
        self.assertTrue(body.endswith('/*\n//\n'))

    def test_IEHLIST_restored(self):
        body = C.directory_body(C.TARGET, 'TSO004', 'SYSDA')
        self.assertIn('DISP=SHR,UNIT=SYSDA,VOL=SER=TSO004', body)

    def test_IEHLIST_unapproved_dsn_refused(self):
        with self.assertRaises(C.ContractError): C.directory_body('SYS1.LINKLIB', 'SYSRES', 'SYSDA')

    def test_IEHLIST_malicious_unit_refused(self):
        with self.assertRaises(C.ContractError): C.directory_body(C.TARGET, 'TSO004', 'X\n//HACK')

    def test_IEHLIST_malicious_volser_refused(self):
        with self.assertRaises(C.ContractError): C.directory_body(C.SOURCE, 'BAD\n//HACK', 'SYSDA')

    def test_canonical_member_changed_rejected(self):
        root=self.root
        d=root/'mr10-kit-compiler/jcl';d.mkdir(parents=True)
        (d/'run-regression-tests.jcl').write_text('invalid canonical JCL')
        with self.assertRaisesRegex(C.ContractError,'Git blob changed'):
            C.source_bytes(root=root)

    def test_no_hidden_temp_files_after_JCL_test(self):
        C.validate_tape_jobs(root=self.root)
        self.assertFalse((self.root/'mvs-state').exists())


if __name__=='__main__': unittest.main()
