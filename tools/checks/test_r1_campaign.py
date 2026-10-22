#!/usr/bin/env python3
"""Host-only acceptance campaign invariants; does not submit MVS jobs."""
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'bootstrap-toolchain/probes/r1-registration'


def module(path, name):
    return SourceFileLoader(name,str(path)).load_module()


class CampaignHostChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign=module(ROOT/'tools/bootstrap/run-r1-acceptance',
                            'r1_campaign_host')
        cls.life=module(HERE/'make-lifecycle-jobs.py','r1_life_host')
        cls.overlay=module(ROOT/'tools/checks/r1-overlay-regression-jcl.py',
                           'r1_overlay_host')
        cls.patcher=module(ROOT/'tools/checks/r1_prepare_candidate.py',
                           'r1_candidate_host')

    def test_source_provenance_rejects_bogus_aligned_finalizer(self):
        checker=module(ROOT/'tools/checks/r1_provenance.py','r1_provenance_host')
        registry=(HERE/'selected-registry.asm').read_text('ascii')
        desc=(HERE/'descriptor.asm').read_text('ascii')
        disp=(HERE/'dispatcher.asm').read_text('ascii')
        result=checker.check(registry,desc,[disp])
        self.assertEqual(result['descriptor_spans'],1)
        evil=desc.replace("F'1',F'0',F'1',F'0',F'0',F'0'",
                          "F'1',F'0',F'1',F'4096',F'0',F'0'")
        with self.assertRaisesRegex(ValueError,r'lacks A\(SYMBOL\)'):
            checker.check(registry,evil,[disp])
        evil=desc.replace("F'298',A(R1DISP)","F'298',A(R1FAKE)")
        with self.assertRaisesRegex(ValueError,'untrusted'):
            checker.check(registry,evil,[disp])
        evil=registry.replace('A(R1EXBEG),A(R1EXEND)',"F'4096',F'8192'")
        with self.assertRaises(ValueError):
            checker.check(evil,desc,[disp])

    def test_effective_owner_ledger_and_registration_check(self):
        patcher=module(ROOT/'tools/checks/r1_prepare_candidate.py',
                       'r1_owner_patcher_host')
        registrar=(ROOT/'bootstrap-toolchain/asm/bcplrgs.asm').read_text('ascii')
        src=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        patched=patcher.adapt(src)
        self.assertIn('R1OWNB   DS    CL700',patched)
        self.assertIn('R1OWNP   DC    A(R1OWNB)',patched)
        for bit in ('01','02','04'):
            self.assertIn("X'"+bit+"'",patched)
        self.assertIn('ST    2,RGOWNER',registrar)
        self.assertIn('CLI   0(4),X\'00\'',registrar)
        self.assertIn('RGOWNER  DC',registrar)

    def test_case_roster_includes_full_diagnostics_and_lifecycle(self):
        cases=self.campaign.case_spec()
        self.assertEqual(len(cases),24)
        self.assertEqual(len({s[1] for s in cases}),24)
        self.assertEqual({s[0] for s in cases if s[0].startswith('neg-')},
                         {f'neg-{n}' for n in (*range(1001,1015),2001)})
        self.assertEqual([s[2] for s in cases if s[0].startswith('life-')],
                         [0,7,8,7])

    def test_real_prior_owner_probe_roster(self):
        owner=module(HERE/'make-owner-jobs.py','r1_owner_host')
        source=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        trail=module(HERE.parent/'r0-export-trailer-probe/make-job.py',
                     'r1_owner_trail_host')
        for profile,(slot,name) in owner.PROFILES.items():
            with self.subTest(profile=profile):
                deck=owner.build(profile,trail.sample_generated(),source,
                       [f"//{name} JOB (BCPL),'R1 TEST',CLASS=A,MSGCLASS=A"],
                       'HERC02.BCPL.BOOT.OBJ')
                self.assertIn(f"F'{slot}',A(R1DISP)",deck)
                self.assertIn(f' NAME {name}(R)',deck)
                self.assertNotIn('DISP=MOD',deck)
                self.assertTrue(all(len(x)<=71 for x in deck.splitlines()))

    def test_unique_run_scoped_generated_job_paths(self):
        run=Path('/tmp/r1-test-run-example')
        specs=self.campaign.case_spec()
        self.assertEqual(len(specs),24)
        for name, *_ in specs:
            path=self.campaign.fixture_path(name,run)
            self.assertEqual(path.parent,run/'jcl')
            self.assertTrue(path.name.startswith('r1-'))
            self.assertEqual(path.suffix,'.jcl')
        self.assertEqual(self.campaign.fixture_path('life-stop',run).name,
                         'r1-life-stop.jcl')

    def test_application_sysprint_can_follow_go_completion(self):
        spec=next(s for s in self.campaign.case_spec() if s[0]=='selected')
        sm=('JOB 2230  R1SELECT\nASMA IFOX00 RC=0000\n'
            'LKED IEWL RC=0000\nGO PGM=*.DD RC=0000\n'
            'JOB RESULT: SUCCESS\n')
        raw=('  BCPLMAIN BCPLMAIN   RGINIT RGINIT\n'
             '  BCRGBEG BCPLREG   BLIB BLIB   R1DISP R1DISP\n'
             'IEF236I ALLOC. FOR R1SELECT GO\n'
             'IEF142I R1SELECT GO - STEP WAS EXECUTED - COND CODE 0000\n'
             'SYSPRINT USER DATA\nR1 SELECTED BCPLREG PASS\n')
        self.assertEqual(self.campaign.verify_case(spec,sm,raw)[0],'PASS')
        self.assertEqual(self.campaign.verify_case(spec,sm,raw.replace(
            'R1 SELECTED BCPLREG PASS','WRONG OUTPUT'))[0],'FAIL')

    def test_two_package_finalizers_and_reverse_order(self):
        for profile in self.life.PROFILES:
            reg,desc,extra=self.life.sources(profile)
            self.assertIn("F'28',F'44',F'2',F'0'",reg)
            self.assertLess(reg.index('A(R1BABEG)'),reg.index('A(R1EXBEG)'))
            self.assertIn("CL8'R1BASE',F'1',F'0'",desc)
            self.assertIn('A(R1FINA)',desc)
            self.assertIn('A(R1FINB)',extra[0][2])
            self.assertEqual(len(extra),3)
            self.assertIn('STM   14,12,12(13)',extra[1][2])
            self.assertIn("C     3,=F'7'",extra[1][2])
            self.assertIn("LA    15,8",extra[1][2])
            self.assertIn("'R1 TRACE FINA FINISH'",extra[1][2])
            self.assertIn("'R1 TRACE FINB STOP'",extra[2][2])
            self.assertIn('DONE     LA    15,8' if profile.endswith('-error')
                          else 'DONE     LA    15,0',extra[1][2])

    def test_jcl_profile_is_temporary_and_card_bounded(self):
        source=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        r=module(HERE.parent/'r0-export-trailer-probe/make-job.py',
                 'r1_mock_trail_host')
        for profile in self.life.PROFILES:
            j=self.life.JOBS[profile]
            deck=self.life.build(profile,r.sample_generated(),source,
                   [f"//{j} JOB (BCPL),'R1 TEST',CLASS=A,MSGCLASS=A"],
                   'HERC02.BCPL.BOOT.OBJ')
            self.assertIn(f' NAME {j}(R)',deck)
            self.assertIn('DISP=SHR',deck)
            self.assertNotIn('DISP=MOD',deck)
            self.assertNotIn('BOOT.DEVOBJ',deck)
            self.assertEqual(sum(x=='/*' for x in deck.splitlines()),10)
            self.assertTrue(all(x.isascii() and len(x)<=71 for x in
                                deck.splitlines()))

    def test_verifier_uses_live_go_section_not_asm_listing(self):
        raw=('  BCPLMAIN BCPLMAIN   RGINIT RGINIT\n'
             '  BCRGBEG BCPLREG   BLIB BLIB   R1DISP R1DISP\n'
             'IFOX LISTING BCPLREG 1002 INVALID REGISTRY HEADER\n'
             'IEF236I ALLOC. FOR R1N1002 GO\n'
             'IEF237I JES2 ALLOCATED TO SYSPRINT\n'
             'BCPLREG 1002 INVALID REGISTRY HEADER\n'
             'IEF142I R1N1002 GO - STEP WAS EXECUTED - COND CODE 0012\n')
        summary=('JOB 50  R1N1002\n'
                 'ASMA       IFOX00       RC=0000\n'
                 'ASMN       IFOX00       RC=0000\n'
                 'ASMR       IFOX00       RC=0000\n'
                 'ASMG       IFOX00       RC=0000\n'
                 'LKED       IEWL         RC=0000\n'
                 'GO         PGM=*.DD     RC=0012\n'
                 'JOB RESULT: SUCCESS\n')
        spec=('neg-1002','R1N1002',12,['BCPLREG 1002'],[])
        self.assertEqual(self.campaign.verify_case(spec,summary,raw)[0],'PASS')
        self.assertEqual(self.campaign.verify_case(spec,summary,
                                                   raw.replace('BCPLREG 1002 INVALID REGISTRY HEADER\nIEF142I',
                                                               'IEF142I'))[0],'FAIL')
        self.assertEqual(self.campaign.verify_case(spec,summary.replace('RC=0012','RC=0000'),raw)[0],'FAIL')

    def test_finalizers_checked_once_in_reverse_order(self):
        spec=next(x for x in self.campaign.case_spec() if x[0]=='life-stop-error')
        def build(trace):
            raw=('  BCPLMAIN BCPLMAIN  RGINIT RGINIT\n'
                 '  BCRGBEG BCPLREG BLIB BLIB R1DISP R1DISP\n'
                 '  R1FINA R1FINA  R1FINB R1FINB\n'
                 'IEF236I ALLOC. FOR R1LSERR GO\n')+trace+'\nIEF142I R1LSERR GO - STEP WAS EXECUTED - COND CODE 0007\n'
            sm=('JOB 50  R1LSERR\nASMA IFOX00 RC=0000\n'
                'LKED IEWL RC=0000\nGO PGM=*.DD RC=0007\nJOB RESULT: SUCCESS\n')
            return self.campaign.verify_case(spec,sm,raw)[0]
        good=('R1 LIFECYCLE START\nR1 TRACE FINA STOP\n'
              'BCPLREG 2001 FINALIZER RETURNED NONZERO\n'
              'R1 TRACE FINB STOP')
        self.assertEqual(build(good),'PASS')
        self.assertEqual(build(good.replace('R1 TRACE FINA STOP\n','')),'FAIL')
        self.assertEqual(build('R1 LIFECYCLE START\nR1 TRACE FINB STOP\nR1 TRACE FINA STOP\nBCPLREG 2001 FINALIZER RETURNED NONZERO'),'FAIL')
        self.assertEqual(build(good+'\nR1 TRACE FINA STOP'),'FAIL')

    def test_regression_overlay_uses_temporary_objects(self):
        core=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        reg=(ROOT/'bootstrap-toolchain/asm/bcplrgs.asm').read_text('ascii')
        empty=(ROOT/'bootstrap-toolchain/asm/bcplreg-empty.asm').read_text('ascii')
        base="""//RG000R JOB (BCPL),'TEST',CLASS=A,MSGCLASS=A
//* RUNTIME LIBRARY: OBJ; APP ASSEMBLY ONLY
//* EXPLICIT BCPLMAIN CANDIDATE: 0
//ASMAP EXEC PGM=IFOX00
//SYSLIN DD DSN=&&APOBJ,DISP=(OLD,DELETE)
//LKED EXEC PGM=IEWL
//SYSLIN DD DSN=&&APOBJ,DISP=(OLD,DELETE)
//         DD *
 INCLUDE OBJ(BCPLMAIN)
 INCLUDE OBJ(BCPLIO)
 INCLUDE OBJ(BLIB)
 ENTRY BCRG0000
/*
//GO EXEC PGM=*.LKED.SYSLMOD
"""
        jcl=self.overlay.overlay(base,core,reg,empty)
        self.assertNotIn(' INCLUDE OBJ(BCPLMAIN)',jcl)
        self.assertEqual(jcl.count('ASMR1N'),1)
        self.assertIn('&&R1NOBJ',jcl)
        self.assertIn('&&R1ROBJ',jcl)
        self.assertIn('&&R1GOBJ',jcl)
        self.assertIn(' INCLUDE OBJ(BLIB)',jcl)
        self.assertTrue(all(len(x)<=71 for x in jcl.splitlines()))


if __name__=='__main__':
    unittest.main()
