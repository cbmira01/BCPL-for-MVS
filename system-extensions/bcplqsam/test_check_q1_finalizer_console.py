"""Exercise Q.1 finalizer WTO checker with genuine and false observations."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

script=Path(__file__).with_name('check-q1-finalizer-console.py')
spec=importlib.util.spec_from_file_location('q1_console',script)
assert spec and spec.loader
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def fixtures(profile='finish'):
    job,rc=c.JOB[profile]
    summary=f'JOB 6627  {job}\nGO         PGM=*.DD     RC={rc:04d}\n'
    console=(f'12:00:00 IEF403I {job} - STARTED\n'
             '12:00:01 OTHER MESSAGE\n'
             '12:00:02 BCPLQSAM Q1 FINALIZER 16 CLOSE PASS\n'
             f'12:00:03 IEF404I {job} - ENDED\n')
    return summary,console


class ConsoleTests(unittest.TestCase):
    def test_verified_finish_and_stop(self):
        for profile in c.JOB:
            with self.subTest(profile=profile):
                self.assertEqual(c.review(profile,*fixtures(profile)),(True,[]))

    def test_missing_wto_or_missing_boundaries(self):
        s,c0=fixtures()
        for log in (c0.replace(c.TRACE,'NO TRACE'),
                    c0.replace('IEF404I','SOMETHING'),
                    c0.replace('IEF403I','SOMETHING'),
                    c0.replace('IEF404I Q16FIN - ENDED','IEF404I OTHER - ENDED')):
            with self.subTest(log=log[:40]):
                self.assertFalse(c.review('finish',s,log)[0])

    def test_listing_or_memory_is_not_wto(self):
        s,c0=fixtures()
        for fake in ("690          WTO   'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS'",
                     "00095C C2C3D7D3D8E2C1D4 695+ DC C'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS' MESSAGE TEXT",
                     "0A9A40   F0F0F0F0 BCPLQSAM Q1 FINALIZER 16 CLOSE PASS"):
            log=c0.replace('12:00:02 '+c.TRACE,fake)
            with self.subTest(fake=fake[:35]):
                self.assertFalse(c.review('finish',s,log)[0])

    def test_duplicate_run_and_bad_return(self):
        s,c0=fixtures()
        self.assertFalse(c.review('finish',s,c0+c0)[0])
        self.assertFalse(c.review('finish',s.replace('RC=0000','RC=0008'),c0)[0])
        self.assertFalse(c.review('finish',s.replace('Q16FIN','Q16STP'),c0)[0])

    def test_nonzero_finalizer_or_abend(self):
        s,c0=fixtures()
        for failure in (c.ERROR,'IEF450I Q16FIN GO - ABEND S322'):
            log=c0.replace('12:00:01 OTHER MESSAGE',failure)
            self.assertFalse(c.review('finish',s,log)[0])

    def test_read_only_no_decks(self):
        source=script.read_text()
        self.assertNotIn('submit-jcl',source)
        self.assertNotIn('subprocess',source)
        self.assertNotIn('unlink(',source)


if __name__=='__main__':unittest.main()
