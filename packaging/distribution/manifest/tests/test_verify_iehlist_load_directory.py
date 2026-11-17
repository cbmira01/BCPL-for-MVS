"""Synthetic, non-submitting tests of TA.0 IEHLIST saved evidence parsing.

Output format based on a published example, NOT JOB 9060 actual printer output.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[4] / 'tools/distribution/verify-iehlist-load-directory.py'
SPEC = importlib.util.spec_from_file_location('ta0_iehlist_review', SRC)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

DSN = 'HERC02.BCPL.MR10KIT.LOAD'
JOB = '9060'
BODY = '''//* PRIVATE-CREDENTIAL-FREE JOB BODY
//DIRLIST  EXEC PGM=IEHLIST
//SYSPRINT DD SYSOUT=*
//VOLDD    DD DSN=HERC02.BCPL.MR10KIT.LOAD,
//            DISP=SHR,UNIT=SYSDA,VOL=SER=TSO003
//SYSIN    DD *
 LISTPDS DSNAME=HERC02.BCPL.MR10KIT.LOAD,VOL=SYSDA=TSO003,FORMAT
/*
'''
LISTING = '''\f
                                   SYSTEMS SUPPORT UTILITIES---IEHLIST                               PAGE    1

     DATE: 2026.321  TIME: 11.44.00
       DIRECTORY INFO FOR SPECIFIED PDS ON VOL TSO003
      HERC02.BCPL.MR10KIT.LOAD

                                                     OTHER INFORMATION INDEX
         SCATTER FORMAT   SCTR=SCATTER/TRANSLATION TABLE TTR IN HEX
         ALIAS NAMES      ALIAS MEMBER NAMES WILL BE FOLLOWED BY AN ASTERISK

       MEMBER       ENTRY    ATTR    REL ADDR-HEX     CONTIG    LEN 1ST
        NAME        PT-HEX   HEX    BEGIN  1ST TXT   STOR-DEC   TXT-DEC
       ICINT19       08000D   0103   000003  010100   00151312    10496
      OF THE 00001 DIRECTORY BLOCKS ALLOCATED TO THIS PDS, 00000 ARE(IS) COMPLETELY UNUSED
'''
REPORT = f'''11.42.43 JOB {JOB}  $HASP373 TA0LDIR STARTED - INIT 1 - CLASS A
11.42.43 JOB {JOB}  TA0LDIR DIRLIST IEHLIST RC= 0000
11.42.43 JOB {JOB}  $HASP395 TA0LDIR ENDED
//TA0LDIR JOB (BCPL),'LOAD DIRECTORY',CLASS=A,MSGCLASS=A,
//             USER=HERC02,PASSWORD=TOPSECRET,
IEF142I TA0LDIR DIRLIST - STEP WAS EXECUTED - COND CODE 0000
{LISTING}'''


def pin(root: Path, report: str = REPORT, *, member: str = 'ICINT19'):
    raw = {
        'cursor.json': b'{"fake":1}',
        'job-body.jcl': BODY.encode('ascii'),
        'job-summary.txt': b'JOB 9060  TA0LDIR\nDIRLIST    IEHLIST      RC=0000\n',
        'job-report.txt': report.encode('utf-8'),
        'printer-window.raw': b'raw printer bytes (sensitive)\n',
    }
    for name, content in raw.items():
        (root / name).write_bytes(content)
    receipt = {'phase': mod.EXPECTED_PHASE,
               'job': 9060, 'jobname': 'TA0LDIR',
               'dataset_key': 'MR10_LOAD', 'dsn': DSN,
               'member': member, 'source_volume': 'TSO003',
               'source_dcb': mod.DCB, 'directory_utility': 'IEHLIST LISTPDS FORMAT',
               'sha256': {name: hashlib.sha256(content).hexdigest() for name, content in raw.items()}}
    (root / 'receipt.json').write_text(json.dumps(receipt) + '\n')


class ParseExamples(unittest.TestCase):
    def test_parses_known_format_without_echo(self):
        result = mod.parse_directory(REPORT, dsn=DSN, volser='TSO003', member='ICINT19')
        self.assertEqual(result['entry_point_hex'], '08000D')
        self.assertEqual(result['attributes_hex'], '0103')
        self.assertEqual(result['other_member_rows'], 0)
    def test_accepts_extra_members_without_changing_selected_member(self):
        other = LISTING.replace('       ICINT19', '       OTHER123     000011   0103   000003\n       ICINT19')
        result = mod.parse_directory(REPORT.replace(LISTING, other), dsn=DSN, volser='TSO003', member='ICINT19')
        self.assertEqual(result['other_member_rows'], 1)
    def test_rejects_only_jcl_echo(self):
        report = REPORT.split('SYSTEMS SUPPORT UTILITIES---IEHLIST')[0] + '\nLISTPDS DSNAME=' + DSN + ',FORMAT\n'
        with self.assertRaisesRegex(mod.EvidenceError, 'IEHLIST_FORMAT_UNRECOGNIZED'):
            mod.parse_directory(report, dsn=DSN, volser='TSO003', member='ICINT19')
    def test_rejects_missing_member_row_despite_control_echo(self):
        r = REPORT.replace('       ICINT19       08000D', '       OTHER123      08000D')
        with self.assertRaisesRegex(mod.EvidenceError, 'MEMBER_ROW_MISSING'):
            mod.parse_directory(r, dsn=DSN, volser='TSO003', member='ICINT19')
    def test_rejects_duplicate_member_rows(self):
        r = REPORT.replace('       ICINT19       08000D', '       ICINT19       08000D   0103\n       ICINT19       08000D')
        with self.assertRaisesRegex(mod.EvidenceError, 'MEMBER_ROW_MISSING'):
            mod.parse_directory(r, dsn=DSN, volser='TSO003', member='ICINT19')
    def test_rejects_alias_row(self):
        r = REPORT.replace('       ICINT19       08000D', '       ICINT19*      08000D')
        with self.assertRaisesRegex(mod.EvidenceError, 'MEMBER_ROW_MISSING'):
            mod.parse_directory(r, dsn=DSN, volser='TSO003', member='ICINT19')
    def test_missing_footer_rejected(self):
        r=REPORT.replace('OF THE 00001 DIRECTORY BLOCKS ALLOCATED TO THIS PDS', 'MORE DATA')
        with self.assertRaisesRegex(mod.EvidenceError,'DIRECTORY_FOOTER_MISSING'):
            mod.parse_directory(r,dsn=DSN,volser='TSO003',member='ICINT19')
    def test_bad_volume_rejected(self):
        with self.assertRaisesRegex(mod.EvidenceError, 'DIRECTORY_VOLUME_MISMATCH'):
            mod.parse_directory(REPORT,dsn=DSN,volser='OTHER',member='ICINT19')
    def test_bad_dsn_rejected(self):
        with self.assertRaisesRegex(mod.EvidenceError, 'DIRECTORY_DATASET_MISMATCH'):
            mod.parse_directory(REPORT,dsn='OTHER.DATASET',volser='TSO003',member='ICINT19')
    def test_header_corruption_rejected(self):
        r=REPORT.replace('MEMBER       ENTRY    ATTR', 'MEMBER       OTHER    ATTR')
        with self.assertRaisesRegex(mod.EvidenceError, 'MEMBER_COLUMNS_MISSING'):
            mod.parse_directory(r,dsn=DSN,volser='TSO003',member='ICINT19')
    def test_member_row_not_below_heading_rejected(self):
        r=REPORT.replace('       ICINT19       08000D', '       ICINT19       08000D')
        r=r.replace('       MEMBER       ENTRY', '       OTHER        ENTRY')
        with self.assertRaisesRegex(mod.EvidenceError,'MEMBER_COLUMNS_MISSING'):
            mod.parse_directory(r,dsn=DSN,volser='TSO003',member='ICINT19')


class PinnedEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.evidence=self.root/'existing'
        self.evidence.mkdir()
        self.output=self.root/'new'
        pin(self.evidence)
    def run_validation(self):
        return mod.verify(self.evidence,self.output)
    def test_verified_writes_one_private_receipt(self):
        v=self.run_validation()
        self.assertEqual(v['job'], 9060)
        self.assertEqual(v['directory']['member'],'ICINT19')
        self.assertEqual(v['directory']['entry_point_hex'],'08000D')
        self.assertEqual(self.output.stat().st_mode & 0o777,0o700)
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ['directory-review.json'])
        self.assertEqual((self.output/'directory-review.json').stat().st_mode & 0o777,0o600)
        self.assertNotIn('TOPSECRET',(self.output/'directory-review.json').read_text())
        self.assertEqual(v['source_job_report_sha256'],mod.sha((self.evidence/'job-report.txt').read_bytes()))
    def test_wrong_job_id_rejected(self):
        data=json.loads((self.evidence/'receipt.json').read_text());data['job']=9059
        (self.evidence/'receipt.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(mod.EvidenceError,'JES_IDENTITY'):
            self.run_validation()
    def test_report_tamper_rejected_before_parser(self):
        (self.evidence/'job-report.txt').write_text('ICINT19')
        with self.assertRaisesRegex(mod.EvidenceError, 'ATTACHMENT_HASH_MISMATCH'):
            self.run_validation()
    def test_receipt_bad_phase_rejected(self):
        p=self.evidence/'receipt.json';j=json.loads(p.read_text());j['phase']='RELEASE ACCEPTED';p.write_text(json.dumps(j))
        with self.assertRaisesRegex(mod.EvidenceError, 'INVALID_RECEIPT_PHASE'):
            self.run_validation()
    def test_wrong_dcb_rejected(self):
        p=self.evidence/'receipt.json';j=json.loads(p.read_text());j['source_dcb']['recfm']='FB';p.write_text(json.dumps(j))
        with self.assertRaisesRegex(mod.EvidenceError,'WRONG_SOURCE_OR_DCB'):
            self.run_validation()
    def test_wrong_member_rejected(self):
        p=self.evidence/'receipt.json';j=json.loads(p.read_text());j['member']='NOTFOUND';p.write_text(json.dumps(j))
        with self.assertRaisesRegex(mod.EvidenceError,'WRONG_JOB_OR_MEMBER'):
            self.run_validation()
    def test_missing_report_rejected(self):
        (self.evidence/'job-report.txt').unlink()
        with self.assertRaisesRegex(mod.EvidenceError,'MISSING_OR_UNSAFE_EVIDENCE'):
            self.run_validation()
    def test_evidence_symlink_rejected(self):
        target=self.evidence/'job-report.txt';target.unlink();target.symlink_to(self.evidence/'job-summary.txt')
        with self.assertRaisesRegex(mod.EvidenceError,'MISSING_OR_UNSAFE_EVIDENCE'):
            self.run_validation()
    def test_missing_control_rejected(self):
        p=self.evidence/'job-body.jcl'
        body=p.read_text().replace('LISTPDS DSNAME=', 'WRONG DSNAME=')
        p.write_text(body)
        jpath=self.evidence/'receipt.json';j=json.loads(jpath.read_text());j['sha256']['job-body.jcl']=mod.sha(p.read_bytes());jpath.write_text(json.dumps(j))
        with self.assertRaisesRegex(mod.EvidenceError,'JOB_BODY_MISMATCH'):
            self.run_validation()
    def test_wrong_step_rc_rejected(self):
        p=self.evidence/'job-report.txt';p.write_text(p.read_text().replace('RC= 0000','RC= 0008'))
        jpath=self.evidence/'receipt.json';j=json.loads(jpath.read_text());j['sha256']['job-report.txt']=mod.sha(p.read_bytes());jpath.write_text(json.dumps(j))
        with self.assertRaisesRegex(mod.EvidenceError,'JES_IDENTITY_OR_RC_MISMATCH'):
            self.run_validation()
    def test_existing_output_rejected(self):
        self.output.mkdir()
        with self.assertRaisesRegex(mod.EvidenceError,'BAD_OUTPUT_LOCATION'):
            self.run_validation()
    def test_outside_workarea_enforced(self):
        # No untracked test directory needs creating in the checkout root.
        with self.assertRaisesRegex(mod.EvidenceError,'BAD_OUTPUT_LOCATION'):
            mod.check_paths(self.evidence,mod.ROOT/'unauthorized-ta0-output')
    def test_private_no_console_full_report(self):
        from contextlib import redirect_stdout,redirect_stderr
        from io import StringIO
        out,err=StringIO(),StringIO()
        with redirect_stdout(out),redirect_stderr(err):
            self.assertEqual(mod.main(['--evidence-dir',str(self.evidence),'--output-dir',str(self.output)]),0)
        self.assertNotIn('PASSWORD',out.getvalue()+err.getvalue())
        self.assertNotIn('TOPSECRET',out.getvalue()+err.getvalue())


if __name__ == '__main__':
    unittest.main()
