"""Structural/safety tests for the one-deck test-only overlay."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

p=Path(__file__).with_name('prepare-q1-finalizer-diagnostic.py')
s=importlib.util.spec_from_file_location('q1fd_prepare',p)
assert s and s.loader
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

ASM='QSMFIN   CSECT\n'+m.ENTRY+m.LOOP+m.EXIT+'QSMCTRL  CSECT\n'


class PrepareTests(unittest.TestCase):
    def test_three_calls_and_three_distinct_wto_lists(self):
        output=m.instrument_asm(ASM)
        self.assertEqual(output.count('         L     15,=A(QFPROBE)'),3)
        self.assertEqual(output.count('QFPROBE  CSECT'),1)
        for phase in ('E','L','X'):
            self.assertEqual(output.count(f"'Q1F:{phase}:"),1)
        self.assertEqual(output.count('         WTO   MF=(E,'),3)
        self.assertTrue(all(len(line)<=71 for line in output.splitlines()))

    def test_source_mutation_duplicate_and_bad_cards_fail(self):
        for src in (ASM.replace(m.LOOP,'REPLACED\n'),ASM+ASM,
                    ASM.replace('QSMCTRL  CSECT\n','X\n')):
            with self.assertRaises(ValueError):m.instrument_asm(src)
        with self.assertRaises(ValueError):m.instrument_asm(ASM+'x'*73+'\n')

    def test_full_deck_changes_only_allowed_spans(self):
        rows=["//Q16FIN JOB (BCPL),'TEST',CLASS=A",'//ASMQ     EXEC PGM=IFOX00',
              '//SYSIN    DD  *',*ASM.splitlines(),'/*',
              ' NAME Q16FIN(R)', '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
              '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,']
        deck='\n'.join(rows)+'\n'
        def verified(a,job,profile):
            if not a[0].startswith(f'//{job} JOB') or profile!='finish':
                raise ValueError('invalid header')
            return '\n'.join(a)+'\n'
        def span(a,step):
            return a.index('//SYSIN    DD  *')+1,a.index('/*')
        fake=SimpleNamespace(verify=verified,source_span=span,
                             replace_one=lambda a,x,y:a.__setitem__(a.index(x),y))
        with patch.object(m,'load_campaign',return_value=fake):
            output=m.instrument_deck(deck,ASM)
            self.assertIn(' NAME Q1FDIAG(R)',output)
            self.assertIn('//SYSLMOD  DD  DSN=&&Q1LOAD(Q1FDIAG),',output)
            self.assertTrue(output.startswith('//Q1FDIAG JOB'))
            with self.assertRaises(ValueError):m.instrument_deck(deck.replace(m.ENTRY,'BAD\n'),ASM)

    def test_rejects_output_outside_workarea(self):
        with self.assertRaises(ValueError):
            m.under_workarea(Path('/tmp/q1fd-outside.jcl'))

    def test_only_finalizer_instrumented(self):
        output=m.instrument_asm(ASM)
        self.assertEqual(output.count('QSMFIN   CSECT'),1)
        self.assertEqual(output.count('QSMCTRL  CSECT'),1)
        self.assertIn(m.ENTRY_NEW,output)
        self.assertIn(m.LOOP_NEW,output)
        self.assertIn(m.EXIT_NEW,output)
        self.assertIn('         STM   14,12,12(13)',output)
        self.assertIn('         LM    14,12,12(13)',output)

    def test_rejects_non_ascii_and_bad_initial_source(self):
        with self.assertRaises(ValueError):
            m.instrument_asm(ASM.replace('QSMFIN', 'QSMFİN'))
        with self.assertRaises(ValueError):
            m.instrument_asm(m.instrument_asm(ASM))

    def test_never_submit_never_overwrite(self):
        src=p.read_text()
        for token in ('subprocess','submit-jcl','os.remove','unlink('):
            self.assertNotIn(token,src)
        self.assertIn('os.O_EXCL',src)

if __name__=='__main__':unittest.main()
