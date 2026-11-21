"""Synthetic tests for the actual MVS read-only Cambridge QSAM fingerprint job."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
P = ROOT/'packaging/distribution/compiler-source/rc2-qsam-fidelity.py'
spec = importlib.util.spec_from_file_location('qsam_verify',P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def reference(raw):
    rows = raw[:-1].decode('ascii').split('\n')
    wire = b''.join(x.encode('cp037').ljust(80,b'\x40') for x in rows)
    fnv = 0x811c9dc5
    for octet in wire:
        fnv ^= octet
        fnv = (fnv*0x01000193)%(2**32)
    t=0
    for line in rows[::-1]:
        if line.strip(' '):break
        t+=1
    return {'count':len(rows),'trail':t,'fnv':fnv,'sum':sum(wire)%(2**32)}


class QsamFidelityTests(unittest.TestCase):
    def test_true_80_byte_padding_and_empty_records(self):
        for b in (b'A\n', b'A\n\n\n',b'\n', b'ABC \nX\n'):
            with self.subTest(raw=b):
                self.assertEqual(mod.fingerprint(b), reference(b))

    def test_hash_checks_space_vs_no_space(self):
        self.assertEqual(mod.fingerprint(b'A\n'),mod.fingerprint(b'A   \n'))
        self.assertNotEqual(mod.fingerprint(b'A\n'),mod.fingerprint(b'A\n\n'))

    def test_refuse_unrepresentable_record(self):
        for b in (b'',b'A',b'A\r\n',b'A\x00\n',b'A\t\n', b'A'*81+b'\n',b'\xff\n'):
            with self.subTest(b=b), self.assertRaises(mod.Refusal):
                mod.fingerprint(b)

    def test_assembler_cards_and_source_expansion(self):
        source=mod.source_cards()
        self.assertGreater(len(source),90)
        self.assertEqual(source[-1].strip(),'END   BCSRCV')
        self.assertTrue(all(len(x)<=71 and x.isascii() for x in source))
        for text in ('GET   QDCB,AREA','FNVHASH','MACRF=GM,EODAD=ATEOD','M     4,PRIME'):
            self.assertTrue(any(text in line for line in source))

    def test_full_jcl_constrained_15_reads(self):
        deck=mod.render_jcl(["//BCSRCRD  JOB (BCPL),'TA2',CLASS=A,MSGCLASS=A"])
        self.assertEqual(deck.count(' EXEC PGM=*.LKED.SYSLMOD'),15)
        self.assertEqual(deck.count('//QIN      DD DSN='),15)
        self.assertEqual(deck.count('//QOUT     DD SYSOUT='),15)
        self.assertIn("//GO0001   EXEC PGM=*.LKED.SYSLMOD,PARM='BCPL',",deck)
        self.assertIn("//GO0015   EXEC PGM=*.LKED.SYSLMOD,PARM='PROGRAM',",deck)
        self.assertNotIn('DISP=(NEW',deck)
        self.assertFalse(any(len(l)>80 for l in deck.splitlines()))

    def test_reject_altered_selected_names(self):
        with self.assertRaisesRegex(mod.Refusal,'canonical'):
            mod.render_jcl(['//J JOB'],names=('BLIB',))

    def report(self):
        rows=[]
        exp={}
        for i,name in enumerate(mod.NAMES,1):
            m={'count':i+100,'trail':1 if name in ('LIBHDR','TRNHDR') else 2 if name=='BLIB' else 0,
               'fnv':i*999,'sum':i*456}
            exp[name]=dict(m)
            rows.append('BCSRC MEMBER='+name.ljust(8)+' COUNT='+f'{m["count"]:08X}'
                         +' TRAIL='+f'{m["trail"]:08X}'+' FNV='+f'{m["fnv"]:08X}'
                         +' SUM='+f'{m["sum"]:08X}')
        return '\n'.join(rows)+'\n',exp

    def test_report_15_exact(self):
        data,exp=self.report()
        parsed=mod.parse_report(data,exp)
        self.assertEqual(len(parsed),15)
        self.assertTrue(all(x['match'] for x in parsed))

    def test_report_mismatch_including_blank_count(self):
        data,exp=self.report()
        data=data.replace('TRAIL=00000002','TRAIL=00000000',1)
        parsed=mod.parse_report(data,exp)
        self.assertEqual(sum(not x['match'] for x in parsed),1)
        self.assertEqual([x['member'] for x in parsed if not x['match']],['BLIB'])

    def test_report_unknown_or_missing(self):
        data,exp=self.report()
        for changed in (data.replace('BLIB    ', 'DEMO    ',1),
                        data.replace('BCSRC MEMBER=BLIB    ', 'BCSRC MEMBER=BCPL    ',1),
                        data.replace('BCSRC MEMBER=BLIB    ','BROKEN MEMBER=BLIB    ',1),
                        data+data.splitlines()[0]+'\n'):
            with self.subTest(changed=changed[:60]),self.assertRaises(mod.Refusal):
                mod.parse_report(changed,exp)

    def test_summarized_step_check(self):
        data='\n'.join('GO%04d RUNMOD RC=0000'%i for i in range(1,16))+'\n'
        mod.summary_steps(data)
        with self.assertRaises(mod.Refusal):
            mod.summary_steps(data.replace('GO0008 RUNMOD RC=0000','GO0008 RUNMOD RC=0008'))
        with self.assertRaises(mod.Refusal):
            mod.summary_steps(data[:-25])


if __name__=='__main__':unittest.main()
