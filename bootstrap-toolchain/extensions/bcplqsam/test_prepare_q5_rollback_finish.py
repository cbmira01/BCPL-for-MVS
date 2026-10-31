"""Offline provenance tests for Q5RBFIN; never contacts MVS or writes JES."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'q5_finish_generator', HERE / 'prepare-q5-rollback-finish.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

SOURCE_TEXT = (
    '// Q.5 provenance fixture\n'
    'IF 1 EQ 0 DO STOP(12)\n'
    '    WRITES("BCPLQSAM Q5 OPEN ROLLBACK PASS")\n'
    '    NEWLINE()\n'
    '    FINISH\n'
    '$)1\n'
)
SUMMARY = (
    'JOB 8144  Q5RFCOMP\n'
    'COMP       ICINT19      RC=0000\n'
    'SVCODE     IEBGENER     RC=0000\n'
    'JOB RESULT: SUCCESS\n'
    'HIGHEST RC: 0000\n'
)


class CorrectedCompilerEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='q5rbfin-check-')
        self.addCleanup(self.tmp.cleanup)
        work = Path(self.tmp.name)
        source = work / 'corrected.bcpl'
        compiled = work / 'rollback-finish-generated.asm'
        source.write_text(SOURCE_TEXT, encoding='ascii')
        compiled.write_bytes(b'ENTRY R0APP\n' * 311)
        evidence = work / 'q5rfcomp-attempt'
        evidence.mkdir()
        (evidence / 'source-head.txt').write_text(
            generator.SOURCE_HEAD + '\n', encoding='ascii')
        (evidence / 'compile.rc').write_text('0\n', encoding='ascii')
        (evidence / 'job-number.txt').write_text('8144\n', encoding='ascii')
        (evidence / 'source.sha256').write_text(
            hashlib.sha256(source.read_bytes()).hexdigest() +
            '  bootstrap-toolchain/extensions/bcplqsam/test-q5-open-rollback.bcpl\n',
            encoding='ascii')
        (evidence / 'summary.txt').write_text(SUMMARY, encoding='ascii')
        self.work, self.source, self.compiled = work, source, compiled
        patchers = [
            mock.patch.object(generator, 'WORK', work),
            mock.patch.object(generator, 'SOURCE', source),
            mock.patch.object(generator, 'COMPILED', compiled),
            mock.patch.object(generator, 'COMPILED_SHA256',
                              hashlib.sha256(compiled.read_bytes()).hexdigest()),
        ]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_good_evidence(self):
        self.assertEqual(
            generator.verified_compiler_code(),
            self.compiled.read_bytes())

    def test_missing_finish(self):
        self.source.write_text(
            SOURCE_TEXT.replace('    FINISH\n', ''), encoding='ascii')
        with self.assertRaisesRegex(ValueError, 'FINISH'):
            generator.verified_compiler_code()

    def test_wrong_compiler_job(self):
        (self.work / 'q5rfcomp-attempt' / 'job-number.txt').write_text(
            '8141\n', encoding='ascii')
        with self.assertRaisesRegex(ValueError, '8144'):
            generator.verified_compiler_code()

    def test_source_hash_mismatch(self):
        (self.work / 'q5rfcomp-attempt' / 'source.sha256').write_text(
            '0' * 64 + '  source.bcpl\n', encoding='ascii')
        with self.assertRaisesRegex(ValueError, 'digest'):
            generator.verified_compiler_code()

    def test_bad_assembler_checksum(self):
        self.compiled.write_bytes(b'ALTERED\n' * 311)
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            generator.verified_compiler_code()

    def test_nonzero_compiler_step(self):
        (self.work / 'q5rfcomp-attempt' / 'summary.txt').write_text(
            SUMMARY.replace('ICINT19      RC=0000', 'ICINT19      RC=0008'),
            encoding='ascii')
        with self.assertRaisesRegex(ValueError, 'ICINT19'):
            generator.verified_compiler_code()

    def test_missing_compiled_output(self):
        self.compiled.unlink()
        with self.assertRaises(OSError):
            generator.verified_compiler_code()


if __name__ == '__main__':
    unittest.main()
