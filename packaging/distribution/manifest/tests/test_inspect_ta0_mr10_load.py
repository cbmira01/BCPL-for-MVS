"""Isolated, non-submitting checks of the TA.0 IEHLIST load directory pilot."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

FILE = Path(__file__).resolve().parents[4] / 'tools/distribution/inspect-ta0-mr10-load.py'
SPEC = importlib.util.spec_from_file_location('ta0_load_inspection', FILE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

DSN = 'HERC02.BCPL.MR10KIT.LOAD'


class Core:
    def __init__(self):
        self.submissions = 0
        self.start = True
        self.rc = True
    def full_dsn(self, config, spec):
        return config['mvs']['hlq'] + '.' + spec['dsn']
    def extract_listds_block(self, report, dsn):
        return report.splitlines() if dsn in report else []
    def parse_listds(self, block):
        text = '\n'.join(block)
        if 'WRONG_DCB' in text:
            return {'volume':'TSO003','dsorg':'PO','recfm':'FB','lrecl':'80','blksize':'800'}
        if 'NO_VOLUME' in text:
            return {'dsorg':'PO','recfm':'U','lrecl':'0','blksize':'6144'}
        return {'volume':'TSO003','dsorg':'PO','recfm':'U','lrecl':'0','blksize':'6144'}
    def authenticated_job_card(self, config, jobname, description, redact_password):
        return ['//' + jobname + " JOB (BCPL),'TA0',CLASS=A,",'// USER=HERC02,PASSWORD=SECRET']
    def submit_and_wait(self, config, deck, max_rc, cursor_file):
        self.submissions += 1
        self.deck = deck
        cursor_file.write_bytes(b'{"fake":1}\n')
        cursor_file.chmod(0o600)
        if not self.start:
            raise RuntimeError('mocked failure')
        return 9099, 'JOB 9099 TA0LDIR\nDIRLIST IEHLIST RC=0000\n'
    def job_report(self, job, cursor_file):
        if not self.rc:
            return ('13.01.01 JOB 9099 $HASP373 TA0LDIR STARTED\n'
                    '13.01.02 JOB 9099 TA0LDIR DIRLIST IEHLIST RC=0008\n'
                    '13.01.03 JOB 9099 $HASP395 TA0LDIR ENDED\n')
        return ('13.01.01 JOB 9099 $HASP373 TA0LDIR STARTED\n'
                '13.01.02 JOB 9099 TA0LDIR DIRLIST IEHLIST RC=0000\n'
                '13.01.03 JOB 9099 $HASP395 TA0LDIR ENDED\n'
                'LOAD MODULE DIRECTORY OUTPUT STILL UNVERIFIED\n')


class LoadInspectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evidence = self.root / 'captured'
        self.evidence.mkdir()
        self.output = self.root / 'inspection'
        self.core = Core()
        self.config = {'mvs': {'hlq':'HERC02','default_unit':'SYSDA'},
                       'runtime': {'printer':'mvs-state/prt/prt00e.txt'},
                       'datasets':{'MR10_LOAD':{
                           'dsn':'BCPL.MR10KIT.LOAD', 'type':'loadlib', **mod.DD}}}
        manifest = {'datasets':[{'dspal_key':'MR10_LOAD','kind':'pds_unload',
                     'transfer':'iebcopy_unload','target_dcb':dict(mod.DD),
                     'members':['ICINT19']}]}
        public = {'datasets':self.config['datasets']}
        self.manifest_path = self.root / 'manifest.yaml'
        self.dspal_path = self.root / 'dspal.yaml'
        self.manifest_path.write_text(yaml.safe_dump(manifest))
        self.dspal_path.write_text(yaml.safe_dump(public))
        self.patch_manifest = patch.object(mod,'INVENTORY',self.manifest_path)
        self.patch_dspal = patch.object(mod,'DSPAL',self.dspal_path)
        self.patch_window = patch.object(mod,'save_window',
            side_effect=lambda _core,_config,_cursor,dest:mod.private_file(dest,b'RAW PRINTER WINDOW\n'))
        for x in (self.patch_manifest,self.patch_dspal,self.patch_window):
            x.start()
            self.addCleanup(x.stop)
        self.create_checks()

    def create_checks(self, stat=f'{DSN}\nVOLUME\nTSO003\nRECFM\nU ** 6144 PO\n',
                      members=f'{DSN}:\n    ICINT19\n'):
        src = {'MR10_LOAD.txt':members.encode(),'MR10_LOAD.stat-raw.txt':stat.encode()}
        for name,content in src.items():
            (self.evidence / name).write_bytes(content)
        (self.evidence / 'SHA256SUMS').write_text(''.join(
            hashlib.sha256(data).hexdigest()+'  '+name+'\n'
            for name,data in src.items()))

    def call(self):
        return mod.run(self.core,self.config,evidence=self.evidence,output=self.output)

    def assert_preflight_fails(self, pattern):
        with self.assertRaisesRegex(mod.LoadError,pattern):
            self.call()
        self.assertEqual(self.core.submissions,0)
        self.assertFalse(self.output.exists())

    def test_live_runner_stub_one_iehlist_job_private_receipts(self):
        rec = self.call()
        self.assertEqual(rec['job'],9099)
        self.assertEqual(self.core.submissions,1)
        self.assertIn('EXEC PGM=IEHLIST',self.core.deck)
        self.assertIn('LISTPDS DSNAME='+DSN, self.core.deck)
        self.assertIn('VOL=SYSDA=TSO003,FORMAT',self.core.deck)
        self.assertIn('DISP=SHR',self.core.deck)
        self.assertNotIn('DISP=OLD',self.core.deck)
        self.assertEqual(self.output.stat().st_mode & 0o777,0o700)
        self.assertEqual(len(list(self.output.iterdir())),6)
        for file in self.output.iterdir():
            self.assertEqual(file.stat().st_mode & 0o777,0o600)
        body=(self.output/'job-body.jcl').read_text()
        self.assertNotIn('SECRET',body)
        self.assertNotIn('PASSWORD=',body)
        self.assertIn('LISTPDS',body)
        self.assertNotIn('SECRET',json.dumps(rec))
        self.assertEqual(rec['source_dcb'],mod.DD)
        self.assertEqual(rec['source_volume'],'TSO003')
        self.assertIn('not prove ICINT19',rec['qualifications'][0])

    def test_sha256s_mismatch_fails(self):
        (self.evidence/'MR10_LOAD.txt').write_text('CHANGED')
        self.assert_preflight_fails('checksum mismatch')

    def test_bad_sha256s_line_fails(self):
        (self.evidence/'SHA256SUMS').write_text('invalid\n')
        self.assert_preflight_fails('malformed SHA256SUMS')

    def test_duplicate_pin_fails(self):
        p=self.evidence/'SHA256SUMS'
        p.write_text(p.read_text()+p.read_text().splitlines()[0]+'\n')
        self.assert_preflight_fails('duplicate SHA256SUMS')

    def test_missing_pin_fails(self):
        p=self.evidence/'SHA256SUMS'
        p.write_text(p.read_text().splitlines()[0]+'\n')
        self.assert_preflight_fails('missing pinned file')

    def test_missing_member_fails(self):
        self.create_checks(members=f'{DSN}:\n    OTHER\n')
        self.assert_preflight_fails('does not select ICINT19')

    def test_wrong_dcb_fails(self):
        self.create_checks(stat=f'{DSN}\nWRONG_DCB')
        self.assert_preflight_fails('not PO/U/0/6144')

    def test_missing_volume_fails(self):
        self.create_checks(stat=f'{DSN}\nNO_VOLUME')
        self.assert_preflight_fails('volume serial')

    def test_missing_stat_dsn_fails(self):
        self.create_checks(stat='OTHER\nVOLUME\nTSO003')
        self.assert_preflight_fails('missing dataset identity')

    def test_incorrect_active_dsn_fails(self):
        self.config['datasets']['MR10_LOAD']['dsn']='BCPL.OTHER.LOAD'
        self.assert_preflight_fails('mapping differs')

    def test_incorrect_active_dcb_fails(self):
        self.config['datasets']['MR10_LOAD']['recfm']='FB'
        self.assert_preflight_fails('mapping differs')

    def test_incorrect_manifest_selected_member_fails(self):
        manifest=yaml.safe_load(self.manifest_path.read_text())
        manifest['datasets'][0]['members']=['OTHERMOD']
        self.manifest_path.write_text(yaml.safe_dump(manifest))
        self.assert_preflight_fails('approved TA.0 selection')

    def test_bad_unit_fails(self):
        self.config['mvs']['default_unit']='BAD UNIT'
        self.assert_preflight_fails('unsafe volume or device unit')

    def test_existing_output_fails(self):
        self.output.mkdir()
        with self.assertRaisesRegex(mod.LoadError,'new absolute'):
            self.call()
        self.assertEqual(self.core.submissions,0)

    def test_external_symlink_fails(self):
        link=self.root/'link'
        link.symlink_to(self.evidence,target_is_directory=True)
        with self.assertRaisesRegex(mod.LoadError,'outside repository'):
            mod.run(self.core,self.config,evidence=link,output=self.output)
        self.assertEqual(self.core.submissions,0)

    def test_malformed_job_rc_fails_after_one_submission(self):
        self.core.rc=False
        with self.assertRaisesRegex(mod.LoadError,'RC=0000'):
            self.call()
        self.assertEqual(self.core.submissions,1)
        self.assertTrue((self.output/'failure.txt').exists())
        self.assertFalse((self.output/'receipt.json').exists())

    def test_submit_uncertain_no_automatic_retry(self):
        self.core.start=False
        with self.assertRaisesRegex(RuntimeError,'mocked failure'):
            self.call()
        self.assertEqual(self.core.submissions,1)
        self.assertTrue((self.output/'failure.txt').exists())

    def test_body_never_has_output_dataset(self):
        b=mod.make_body(DSN,'TSO003','SYSDA')
        self.assertEqual(b.count('EXEC PGM=IEHLIST'),1)
        self.assertNotIn('SYSUT2',b)
        self.assertNotIn('DISP=(NEW',b)
        self.assertNotIn('VOL=SER=TSO004',b)
        self.assertTrue(all(len(x)<=80 for x in b.splitlines()))

    def test_bad_dsn_rejected(self):
        with self.assertRaises(mod.LoadError):
            mod.make_body('HERC02.BCPL.BAD;DROP','TSO003','SYSDA')

    def test_bad_volser_rejected(self):
        with self.assertRaises(mod.LoadError):
            mod.make_body(DSN,'TSO003BAD','SYSDA')

if __name__ == '__main__':
    unittest.main()
