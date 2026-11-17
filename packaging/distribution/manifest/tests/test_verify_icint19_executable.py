"""TA.0: no-MVS tests of the canonical MRREGRES scalar-vector executable pilot."""
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
TOOL=ROOT/'tools/distribution/verify-icint19-executable.py'
spec=importlib.util.spec_from_file_location('exec_pilot',TOOL)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    fragments=[]
    for step,member in [('SSYNI','SYNI'),('STRNI','TRNI'),('SCGI','CGI'),('SBLIBI','BLIBI'),('SICLIB','ICLIB')]:
        fragments.append(f'''//{step:<8} EXEC PGM=IEBGENER
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//SYSUT1   DD  DSN=HERC02.BCPL.MR10KIT.SOURCE({member}),
//             DISP=SHR
//SYSUT2   DD  DSN=&&{member},UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//*
''')
    fragments.append('''//C01A     EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&SYNI,DISP=(OLD,PASS)
//         DD  DSN=&&TRNI,DISP=(OLD,PASS)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//SYSIN    DD  DSN=HERC02.BCPL.MR10KIT.TESTS(SCALVEC),
//             DISP=SHR
//OCODE    DD  DSN=&&O01A,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//SYSUDUMP DD  DUMMY
//*
''')
    fragments.append('''//G01A     EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&CGI,DISP=(OLD,PASS)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//INTCODE  DD  DSN=&&I01A,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//SYSIN    DD  DSN=&&O01A,DISP=(OLD,DELETE)
//SYSUDUMP DD  DUMMY
//*
''')
    fragments.append('''//R01      EXEC PGM=ICINT19,REGION=1024K,COND=(4,LT)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=&&I01A,DISP=(OLD,DELETE)
//         DD  DSN=&&BLIBI,DISP=(OLD,PASS)
//         DD  DSN=&&ICLIB,DISP=(OLD,PASS)
//SYSUDUMP DD  DUMMY
//*
''')
    fragments.append('//X99      EXEC PGM=IEFBR14\n//*\n')
    return ('//* approved fixture\n'+''.join(fragments)).encode('ascii')


def sample_report(job=9070):
    t=(f'20.00.00 JOB {job} $HASP373 TA0ICEX STARTED - INIT 1 - CLASS A\n'
       f'20.00.02 JOB {job} $HASP395 TA0ICEX ENDED\n')
    for step,prog in zip(mod.STEPS,mod.PROGRAMS):
        t+=f'20.00.01 JOB {job} TA0ICEX {step} {prog} RC= 0000\n'
        t+=f'IEF142I TA0ICEX {step} - STEP WAS EXECUTED - COND CODE 0000\n'
    t+='CODE=0\nCODE= 0\nCODE=0\nTEST: Scalar assignments and vector load/store\n'
    t+='RP: SCALAR 17 42\nRP: VECTOR 5 10 15 20\n'
    return t


class FakeCore:
    def __init__(self,report=None):
        self.calls=0
        self.report=report or sample_report()
    def full_dsn(self,cfg,mod_spec):return cfg['mvs']['hlq']+'.'+mod_spec['dsn']
    def authenticated_job_card(self,cfg,name,descr,redact_password):
        return [f'//{name} JOB (BCPL),\'TA0\',CLASS=A,','// USER=HERC02,PASSWORD=PRIVATE']
    def submit_and_wait(self,cfg,deck,max_rc,cursor_file):
        self.calls+=1;self.deck=deck
        cursor_file.write_bytes(b'{"cursor":"mock"}\n')
        return 9070,'JOB 9070 TA0ICEX\n'+''.join(f'{s} {p} RC=0000\n' for s,p in zip(mod.STEPS,mod.PROGRAMS))
    def job_report(self,job,cursor_file):return self.report


class ExecutePilot(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.jcl=self.base/'canonical.jcl'; self.jcl.write_bytes(fixture())
        self.gold=self.base/'golden.expected'; self.gold.write_text('\n'.join(mod.GOLDEN)+'\n')
        src=self.jcl.read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(src)).encode()+b'\0'+src).hexdigest()
        self.patches=[patch.object(mod,'JCL',self.jcl),patch.object(mod,'GOLD',self.gold),
                      patch.object(mod,'SOURCE_BLOB',blob)]
        for x in self.patches:x.start();self.addCleanup(x.stop)
        self.cfg={'mvs':{'hlq':'HERC02'},'datasets':{'MR10_LOAD':{'dsn':'BCPL.MR10KIT.LOAD',
                            'dsorg':'PO','recfm':'U','lrecl':0,'blksize':6144}},
                  'runtime':{'printer':'unused'}}
        self.core=FakeCore()
        self.out=self.base/'new'
        self.evidence=self.base/'original';self.evidence.mkdir()
        self.review=self.base/'review';self.review.mkdir()
        (self.review/'directory-review.json').write_bytes(b'{}\n')
        self.preflight=patch.object(mod,'validate_directory',return_value=({'job':9060,'dsn':'HERC02.BCPL.MR10KIT.LOAD'},{}))
        self.preflight.start();self.addCleanup(self.preflight.stop)
        self.window=patch.object(mod,'save_window',side_effect=lambda c,cfg,cur,out:mod.private(out,b'cursor-window\n'))
        self.window.start();self.addCleanup(self.window.stop)

    def run_it(self):
        return mod.run(self.core,self.cfg,evidence=self.evidence,review_dir=self.review,output=self.out)

    def test_selected_8_steps_from_canonical_source(self):
        body, blob=mod.canonical_steps(fixture(),hlq='HERC02',load_dsn='HERC02.BCPL.MR10KIT.LOAD')
        self.assertEqual(tuple(m.group(1) for m in mod.EXEC.finditer(body)),mod.STEPS)
        self.assertEqual(body.count('PGM=ICINT19'),3)
        self.assertEqual(body.count('PGM=IEBGENER'),5)
        self.assertEqual(body.count('DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR'),3)
        self.assertNotIn('UNRELATED',body)
        self.assertNotIn('PASSWORD',body)
        self.assertTrue(all(len(x)<=80 for x in body.splitlines()))

    def test_full_run_pins_and_quiet(self):
        receipt=self.run_it()
        self.assertEqual(self.core.calls,1)
        self.assertEqual(receipt['job'],9070)
        self.assertEqual(receipt['result']['interpreted_codes'],[0,0,0])
        self.assertEqual(receipt['result']['rp_records'],list(mod.GOLDEN))
        self.assertEqual(set(receipt['sha256']), {'cursor.json','job-body.jcl','job-summary.txt','job-report.txt','printer-window.raw'})
        self.assertNotIn('PRIVATE',(self.out/'job-body.jcl').read_text())
        self.assertEqual((self.out/'receipt.json').stat().st_mode&0o777,0o600)
        for name,pin in receipt['sha256'].items():
            self.assertEqual(hashlib.sha256((self.out/name).read_bytes()).hexdigest(),pin)
        self.assertTrue(self.core.deck.startswith('//TA0ICEX JOB'))
        self.assertEqual(len(list(self.out.iterdir())),6)

    def test_source_mutation_fails_before_submission(self):
        self.jcl.write_bytes(fixture().replace(b'PGM=ICINT19',b'PGM=IEBGENER',1))
        with self.assertRaisesRegex(mod.ExecEvidenceError,'revision changed'):self.run_it()
        self.assertEqual(self.core.calls,0)
        self.assertFalse(self.out.exists())

    def test_load_dsn_mismatch_fails_before_submission(self):
        self.cfg['datasets']['MR10_LOAD']['dsn']='BCPL.OTHER.LOAD'
        with self.assertRaisesRegex(mod.ExecEvidenceError,'differs'):self.run_it()
        self.assertEqual(self.core.calls,0)

    def test_not_selected_dev_hlq(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'scoped'):
            mod.canonical_steps(fixture(),hlq='TEST00',load_dsn='HERC02.BCPL.MR10KIT.LOAD')

    def test_golden_mutation_fails(self):
        self.gold.write_text('RP: SCALAR 99 99\nRP: VECTOR 5 10 15 20\n')
        with self.assertRaisesRegex(mod.ExecEvidenceError,'golden output changed'):self.run_it()
        self.assertEqual(self.core.calls,0)

    def test_evidence_preflight_fails_no_submission(self):
        self.preflight.stop()
        with patch.object(mod,'validate_directory',side_effect=mod.ExecEvidenceError('missing review')):
            with self.assertRaisesRegex(mod.ExecEvidenceError,'missing review'):self.run_it()
        self.assertEqual(self.core.calls,0)

    def test_existing_output_fails(self):
        self.out.mkdir()
        with self.assertRaisesRegex(mod.ExecEvidenceError,'new directory'):self.run_it()
        self.assertEqual(self.core.calls,0)

    def test_negative_code_rejected_and_preserved(self):
        self.core.report=sample_report().replace('CODE= 0','CODE= 4')
        with self.assertRaisesRegex(mod.ExecEvidenceError,'CODE='):self.run_it()
        self.assertEqual(self.core.calls,1)
        self.assertTrue((self.out/'job-report.txt').exists())
        self.assertTrue((self.out/'failure.txt').exists())
        self.assertFalse((self.out/'receipt.json').exists())

    def test_report_wrong_job_fails(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'START/END'):
            mod.validate_report(sample_report().replace('$HASP373 TA0ICEX',' $HASP373 WRONG'),job=9070,gold=mod.GOLDEN)

    def test_report_bad_step_rc_fails(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'missing, bypassed'):
            mod.validate_report(sample_report().replace('C01A ICINT19 RC= 0000','C01A ICINT19 RC= 0008'),job=9070,gold=mod.GOLDEN)

    def test_report_wrong_golden_fails(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'RP records'):
            mod.validate_report(sample_report().replace('RP: SCALAR 17 42','RP: SCALAR 18 42'),job=9070,gold=mod.GOLDEN)

    def test_report_missing_code_fails(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'CODE='):
            mod.validate_report(sample_report().replace('CODE=0','NOCODE=0'),job=9070,gold=mod.GOLDEN)

    def test_report_duplicated_step_fails(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'missing, bypassed'):
            mod.validate_report(sample_report()+'20.00.01 JOB 9070 TA0ICEX R01 ICINT19 RC= 0000\n',job=9070,gold=mod.GOLDEN)

    def test_report_no_abend(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'ABEND'):
            mod.validate_report(sample_report()+'IEF450I TA0ICEX ABEND S0C4\n',job=9070,gold=mod.GOLDEN)

    def test_missing_ief142i_rejected(self):
        bad=sample_report().replace('IEF142I TA0ICEX R01','IEF999I TA0ICEX R01')
        with self.assertRaisesRegex(mod.ExecEvidenceError,'IEF142I'):
            mod.validate_report(bad,job=9070,gold=mod.GOLDEN)

    def test_duplicate_ief142i_rejected(self):
        extra='IEF142I TA0ICEX R01 - STEP WAS EXECUTED - COND CODE 0000\n'
        with self.assertRaisesRegex(mod.ExecEvidenceError,'IEF142I'):
            mod.validate_report(sample_report()+extra,job=9070,gold=mod.GOLDEN)

    def test_extra_semantic_record_rejected(self):
        with self.assertRaisesRegex(mod.ExecEvidenceError,'RP records'):
            mod.validate_report(sample_report()+'RP: SCALAR 17 42\n',job=9070,gold=mod.GOLDEN)

    def test_success_parser(self):
        result=mod.validate_report(sample_report(),job=9070,gold=mod.GOLDEN)
        self.assertEqual(result['rp_records'],list(mod.GOLDEN))
        self.assertEqual(len(result['step_rc']),8)


if __name__=='__main__':unittest.main()
