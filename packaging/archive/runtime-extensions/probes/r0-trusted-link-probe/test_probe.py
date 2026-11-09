"""Credential-free R.0 Decision A source/ownership/JCL regression suite."""
from __future__ import annotations

import copy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import unittest

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location('r0_a_make', HERE / 'make-jobs.py')
make = module_from_spec(spec)
spec.loader.exec_module(make)
rv = spec_from_file_location('r0_a_verify', HERE / 'verify-report.py')
verify = module_from_spec(rv)
rv.loader.exec_module(verify)


class TrustedLinkTest(unittest.TestCase):
    def jobcard(self, profile):
        name = make.PROFILES[profile][0]
        return [f"//{name:<8} JOB (BCPL),'R0 A LINK',CLASS=A,MSGCLASS=A"]

    def test_all_profiles_have_unique_output_and_card_shapes(self):
        self.assertEqual(len(make.PROFILES), 10)
        self.assertEqual(len(set(row[0] for row in make.PROFILES.values())), 10)
        self.assertEqual(len(set(row[2] for row in make.PROFILES.values())), 10)
        for p, (job, code, marker) in make.PROFILES.items():
            with self.subTest(profile=p):
                src = make.sources(p)
                deck = make.make_deck(p, self.jobcard(p), src)
                self.assertEqual(deck.count('//SYSIN    DD  *'), 4)
                self.assertEqual(deck.splitlines().count('/*'), 5)
                self.assertEqual(deck.count('DISP=(OLD,DELETE)'), 4)
                self.assertIn('PARM=\'NCAL,LIST,XREF,MAP\'', deck)
                self.assertIn(' NAME R0ATRST(R)',deck)
                self.assertIn(' ENTRY R0ATST',deck)
                self.assertIn(marker,deck)
                self.assertIn(f"EXPECT   DC    F'{code}'",deck)
                self.assertNotIn('BOOT_OBJ', '\n'.join(row for row in deck.splitlines() if row.startswith('//SYSLIN')))
                self.assertTrue(all(len(row)<=71 and row.isascii() for row in deck.splitlines()))

    def test_export_owner_labels_are_present(self):
        src=make.sources('valid')
        make.verify_source_owners(src)
        self.assertIn('ENTRY R0RB,R0RE',src['ASMR'])
        self.assertIn('ENTRY R0PB,R0PE',src['ASMP'])
        self.assertIn('ENTRY R0FUNC,R0FIN',src['ASMF'])
        self.assertIn('EXTRN R0RB,R0RE,R0PB,R0PE,R0FUNC,R0FIN',src['ASMD'])

    def test_substituted_source_owner_rejected_before_submit(self):
        src=make.sources('valid')
        bad=copy.deepcopy(src)
        bad['ASMR']=bad['ASMR'].replace('R0AREG   CSECT','R0EVIL   CSECT')
        with self.assertRaises(ValueError): make.verify_source_owners(bad)
        with self.assertRaises(ValueError): make.make_deck('valid',self.jobcard('valid'),bad)

    def test_export_symbol_definition_moved_to_wrong_csect(self):
        src=make.sources('valid')
        bad=copy.deepcopy(src)
        bad['ASMR']=bad['ASMR'].replace('R0RB     DC', 'R0FAKE   DC')
        with self.assertRaises(ValueError): make.verify_source_owners(bad)

    def test_duplicate_entry_clause_rejected(self):
        src=make.sources('valid')
        bad=copy.deepcopy(src)
        bad['ASMP']=bad['ASMP'].replace('ENTRY R0PB,R0PE',
                                      'ENTRY R0PB,R0PE\n         ENTRY R0PB,R0PE')
        with self.assertRaises(ValueError): make.verify_source_owners(bad)

    def test_extent_checks_precede_record_dereferences(self):
        asm=(HERE/'validator.asm').read_text('ascii')
        self.assertLess(asm.index('BNZ   REGEXT'),asm.index("CLC   0(4,8)"))
        self.assertLess(asm.index('BNZ   PKGEXT'),asm.index("CLC   0(4,1)"))
        self.assertLess(asm.index('C     2,=A(R0PE)'),asm.index("CLC   0(4,1)"))
        self.assertIn('LA    6,1013',asm)
        self.assertNotIn('BALR  14,15',asm)

    def test_expected_profiles_hit_specific_faults(self):
        self.assertIn('L     9,=A(R0RB)',make.sources('regzero')['ASMD'])
        self.assertIn('L     8,=A(R0RB+1)',make.sources('regunal')['ASMD'])
        self.assertIn('DC    A(R0PB)\n         DC    A(R0PB)',make.sources('pkgbound')['ASMR'])
        self.assertIn("DC    F'40'",make.sources('reglen')['ASMR'])
        self.assertIn("DC    F'60'",make.sources('pkglen')['ASMP'])
        self.assertIn('DC    A(R0FIN)',make.sources('goodhook')['ASMP'])
        self.assertIn('DC    A(R0FUNC)',make.sources('badhook')['ASMP'])

    def test_bad_jobcard_rejected(self):
        for bad in ([],['//BAD JOB'],['//R0ALINK JOB (BCPL)']):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                make.make_deck('valid',bad)

    def test_source_provenance_hashes(self):
        src=make.sources('valid')
        manifest=make.manifest('valid',src,'abc123')
        self.assertEqual(manifest['github_revision'],'abc123')
        self.assertEqual(manifest['symbol_owner_expectations']['R0PB'],'R0APKG')
        for step,text in src.items():
            self.assertEqual(manifest['source_sha256'][step],hashlib.sha256(text.encode('ascii')).hexdigest())
        self.assertNotEqual(make.manifest('valid',src)['source_sha256']['ASMD'],
                            make.manifest('badhook',make.sources('badhook'))['source_sha256']['ASMD'])

    def test_actual_output_line_required_once(self):
        marker=make.PROFILES['valid'][2]
        verify.verify('header\n'+marker+'\n','valid')
        for text in (marker+'\n'+marker+'\n', '  '+marker+'\n',
                     'assembler DC CL80\''+marker+'\'\n', 'WRONG\n'):
            with self.subTest(text=text),self.assertRaises(ValueError):
                verify.verify(text,'valid')

    def test_jcl_credential_guard(self):
        with self.assertRaises(ValueError):
            make.checked_source('//PASSWORD=TOPSECRET','wrong')
        with self.assertRaises(ValueError):
            make.checked_source(' ' * 72,'wide')
        with self.assertRaises(ValueError):
            make.make_deck('valid', ['//WRONG   JOB (BCPL)'])

if __name__=='__main__': unittest.main(verbosity=2)
