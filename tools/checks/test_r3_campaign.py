"""Offline tests for the R.3 acceptance runner (no MVS or secrets)."""
from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT/'tools/bootstrap/run-r3-acceptance'
SPEC = importlib.util.spec_from_loader('r3_campaign_test_module',
    importlib.machinery.SourceFileLoader('r3_campaign_test_module',str(SCRIPT)))
R3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R3)


MAP = '''
                                                CROSS REFERENCE TABLE
  CONTROL SECTION                       ENTRY
    NAME    ORIGIN  LENGTH                NAME   LOCATION
  R0APP         00     2C0
  BCPLMAIN     2C0    1048
  RGINIT      1308     A20
  RGFINI      1D28     100
  BCPLREG     1E28      2C
                                        BCRGBEG     1E28    BCRGEND 1E54
  TMDSC       1E58      38
                                        TMBEG       1E58    TMEND   1E90
  TMDISP      1E90      B8
{fin}  BLIB        4248    1BB0

  LOCATION  REFERS TO SYMBOL  IN CONTROL SECTION
     1CE0            BCRGBEG         BCPLREG                   1CE4            BCRGEND         BCPLREG
     1E44            TMBEG           TMDSC                     1E48            TMEND           TMDSC
     1E8C            TMDISP          TMDISP{finref}
'''


def summary(with_fin=False):
    names=('ASMA','ASMN','ASMR','ASMG','ASMD','ASMS')
    if with_fin:
        names+=('ASMF',)
    names+=('LKED','GO')
    return '\n'.join(f'{n} IFOX00 RC=0000' for n in names) + '\nJOB RESULT: SUCCESS\n'


def report(with_fin=False):
    return (MAP.format(fin='  TMFIN       1F48      94\n' if with_fin else '',
        finref='                      1E7C            TMFIN           TMFIN'
        if with_fin else '')+
        '\nR3 TEMPLATE CLIENT PASS\n'+
        ('17.29.43 JOB 3095  +R3 TEMPLATE FINALIZER CALLED\n'
         if with_fin else ''))


class R3CandidateTests(unittest.TestCase):
    def test_real_template_source_is_relocatable(self):
        for with_fin in (False, True):
            reg, desc, disp, final = R3.sources(with_fin)
            self.assertIn('A(TMBEG),A(TMEND)',reg)
            self.assertIn('A(TMDISP)',desc)
            self.assertIn("CL8'R3TMPL'",reg)
            self.assertIn("F'299'",desc)
            self.assertEqual(final is not None,with_fin)
            self.assertIn('TMFIN',desc) if with_fin else self.assertIn("F'0'",desc)
            if final:
                self.assertEqual(final.count("WTO   'R3 TEMPLATE FINALIZER CALLED'"),1)
                self.assertLess(final.index('WTO   '),final.index('SR    15,15'))

    def test_positive_both_variants(self):
        for enabled in (False, True):
            with self.subTest(finalizer=enabled):
                problems, found=R3.verify_template(summary(enabled),
                    report(enabled),with_finalizer=enabled)
                self.assertEqual(problems,[])
                self.assertEqual(len(found),9 if enabled else 8)

    def test_wrong_steps_fail_closed(self):
        errors,_=R3.verify_template(summary().replace('ASMD IFOX00 RC=0000',
            'ASMD IFOX00 RC=0012'),report())
        self.assertIn('ASMD RC=12',errors)
        errors,_=R3.verify_template(summary().replace('LKED IFOX00 RC=0000',''),
                                     report())
        self.assertTrue(any('wrong JES step set' in s for s in errors))

    def test_wrong_finalizer_selection_and_missing_wto_fail(self):
        issues,_=R3.verify_template(summary(True),report(False),
                                    with_finalizer=True)
        self.assertTrue(any('wrong TMFIN inclusion' in s for s in issues))
        self.assertTrue(any('live finalizer WTO' in s for s in issues))
        issues,_=R3.verify_template(summary(),report(True))
        self.assertTrue(any('wrong TMFIN inclusion' in s for s in issues))

    def test_client_pass_and_map_must_be_real(self):
        for changed in (report().replace('R3 TEMPLATE CLIENT PASS','NO PASS'),
                        report().replace('TMDSC       1E58      38',
                                         'TMDSC       1E58      3C'),
                        report().replace('1E44            TMBEG',
                                         '1E44            WRONG')):
            with self.subTest(report=changed[-100:]):
                self.assertTrue(R3.verify_template(summary(),changed)[0])

    def test_no_persistent_object_write_calls_in_runner(self):
        src=SCRIPT.read_text()
        self.assertIn("cfg['datasets']['BOOT_OBJ']",src)
        self.assertIn("obj_dsn = core.full_dsn",src)
        self.assertIn("registry_override=registry",src)
        self.assertIn("'r3_r1_campaign'",src)
        self.assertNotIn('dspal purgebcpl',src)
        self.assertNotIn('dspal put BOOT',src)
        self.assertNotIn('git push',src)

    def test_regression_requires_exact_skip_083(self):
        class FakeR1:
            def __init__(self, body, rc=0):
                self.body, self.rc = body, rc
            def stream_native_run(self,cmd,env,transcript,timeout):
                self.command = cmd
                transcript.write_text(self.body)
                self.assert_mode = env.get('R1_ACCEPTANCE')
                return self.rc
        good='SKIP  083  source-only\nPASS  145\nFAIL  0\nSKIP  1\nTOTAL 146\n'
        with tempfile.TemporaryDirectory() as root:
            run=Path(root)
            for body, want in ((good,'PASS'),
                               (good.replace('083','084'),'FAIL'),
                               (good.replace('PASS  145','PASS  144'),'FAIL')):
                fake=FakeR1(body)
                result=R3.fresh_regression(run,fake,5)
                self.assertEqual(result['result'],want)
                self.assertEqual(fake.command[-2:],['0','145'])
                self.assertEqual(fake.assert_mode,'1')

    def test_synthetic_no_mvs_preflight_pipeline(self):
        with mock.patch.object(R3,'call',return_value='') as recorded:
            R3.preflight()
        self.assertEqual(recorded.call_count,8)
        self.assertTrue(all('--execute' not in ' '.join(map(str,c.args))
                            for c in recorded.call_args_list))
        self.assertTrue(all('submit-jcl' not in ' '.join(map(str,c.args))
                            for c in recorded.call_args_list))


if __name__=='__main__':
    unittest.main()
