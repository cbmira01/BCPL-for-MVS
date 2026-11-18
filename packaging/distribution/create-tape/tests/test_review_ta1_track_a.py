"""Synthetic-only tests for read-only MVS Track A receipt and HETMAP reviewer."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / 'scripts/review-ta1-track-a'
loader = importlib.machinery.SourceFileLoader('review_ta1', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
ROOT = Path(__file__).resolve().parents[4]


def labels():
    x = ["Label               : 'VOL1'\nVolume Serial       : 'BTA101'\n"]
    for seq, dsn in ((1, 'BCPL.BT0001'), (2, 'BCPL.BT0002')):
        for tag in ('HDR1', 'HDR2', 'EOF1', 'EOF2'):
            x.append(f"Label               : '{tag}'\n")
            if tag in ('HDR1', 'EOF1'):
                x.append(f"Dataset ID          : '{dsn}    '\n"
                         f"Dataset Sequence    : '{seq:04d}'\n")
    return ''.join(x)


def physical(values=(3, 4, 2, 2, 25, 2, 0)):
    return ''.join(f"---------------------\nFile #              : {i}\n"
                   f"Blocks              : {n}\n" for i, n in enumerate(values, 1))


def job(name, number, steps):
    rows = ''.join(f'{s:<10} {"IEBCOMPR" if s.startswith("CMP") else "IEBCOPY":<12} RC=0000\n'
                   for s in steps)
    return f'JOB {number}  {name}\n\nSTEP       PROGRAM      RESULT\n{rows}\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'


class ReviewTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.write = self.root / 'write'
        self.read = self.root / 'read'
        self.write.mkdir(); self.read.mkdir()
        self.tape = self.root / 'fresh.aws'
        self.tape.write_bytes(b'isolated two dataset AWS synthetic fixture')
        digest = hashlib.sha256(self.tape.read_bytes()).hexdigest()
        for name, val in [('WRITE', self.write), ('READ', self.read), ('IMAGE', self.tape), ('SHA', digest)]:
            p = mock.patch.object(m, name, val)
            p.start(); self.addCleanup(p.stop)
        self.populate()

    def populate(self):
        (self.write / 'sha256.txt').write_text(m.SHA + '  mvs-state/tape/' + m.IMAGE.name)
        (self.write / 'labels-final.txt').write_text(labels())
        (self.write / 'files-final.txt').write_text(physical())
        (self.write / 'map-final.txt').write_text(labels() + physical())
        for key, (number, steps) in m.JOBS.items():
            source = self.write if key == 'TA1AWRIT' else self.read
            summary = 'summary.txt' if key == 'TA1AWRIT' else f'summary-{key}.txt'
            receipt = 'submit.txt' if key == 'TA1AWRIT' else f'submit-{key}.txt'
            (source / summary).write_text(job(key, number, steps))
            (source / receipt).write_text(f'{key}: JES JOB {number} returned accepted RC=0\n')
        for org, dsn in [('PS', 'HERC02.BCPL.TA1A.FBREST'), ('PO', 'HERC02.BCPL.TA1A.PDSREST')]:
            (self.read / f'stat-{org}.txt').write_text(f'Dataset: {dsn}\n DSORG:{org}  RECFM:FB LRECL:80 BLKSIZE:800\n')
        (self.read / 'members-restored.txt').write_text('RECORDS:\n' + ''.join(f'    {s}\n' for s in sorted(m.MEMBERS)))

    def test_complete_fixture(self):
        self.assertEqual(m.review()['physical_files'], [3, 4, 2, 2, 25, 2, 0])

    def test_filemark_incorrect(self):
        (self.write / 'files-final.txt').write_text(physical([3,4,2,2,25,2]))
        with self.assertRaisesRegex(m.InvalidEvidence, 'expected 7 physical'):
            m.review()

    def test_noncontiguous_file_ids(self):
        text = physical().replace('File #              : 6', 'File #              : 9')
        with self.assertRaisesRegex(m.InvalidEvidence, 'not contiguous'):
            m.file_layout(text)

    def test_header_blocks_wrong(self):
        (self.write / 'files-final.txt').write_text(physical([2,4,2,2,25,2,0]))
        with self.assertRaisesRegex(m.InvalidEvidence, 'unexpected header'):
            m.review()

    def test_empty_second_data_file(self):
        with self.assertRaisesRegex(m.InvalidEvidence, 'data files are empty'):
            m.file_layout(physical([3,4,2,2,0,2,0]))

    def test_all_and_files_mismatch(self):
        (self.write / 'map-final.txt').write_text(physical([3,4,2,2,24,2,0]))
        with self.assertRaisesRegex(m.InvalidEvidence, 'physical file counts disagree'):
            m.review()

    def test_modified_aws_rejected(self):
        self.tape.write_bytes(b'overwritten')
        with self.assertRaisesRegex(m.InvalidEvidence, 'checksum changed'):
            m.review()

    def test_abend_flag_rejected(self):
        f = self.read / 'summary-TA1ACOMP.txt'
        f.write_text(f.read_text() + 'ABEND: detected\n')
        with self.assertRaisesRegex(m.InvalidEvidence, 'unexpected failure'):
            m.review()

    def test_wrong_jes_number_rejected(self):
        f = self.read / 'summary-TA1AR002.txt'
        f.write_text(f.read_text().replace('9086', '9999'))
        with self.assertRaisesRegex(m.InvalidEvidence, 'wrong JES job'):
            m.review()

    def test_second_compare_missing_rejected(self):
        f = self.read / 'summary-TA1ACOMP.txt'
        f.write_text(f.read_text().replace('CMPPDS', 'REMOVED'))
        with self.assertRaisesRegex(m.InvalidEvidence, 'step identities'):
            m.review()

    def test_restored_member_omission_rejected(self):
        f = self.read / 'members-restored.txt'
        f.write_text(f.read_text().replace('    INSTALL\n', ''))
        with self.assertRaisesRegex(m.InvalidEvidence, 'seven-member'):
            m.review()

    def test_unlinked_receipt_rejected(self):
        f = self.read / 'members-restored.txt'
        f.unlink()
        f.symlink_to(self.write / 'labels-final.txt')
        with self.assertRaisesRegex(m.InvalidEvidence, 'missing/unsafe'):
            m.review()

    def test_wrong_label_sequence_rejected(self):
        f = self.write / 'labels-final.txt'
        f.write_text(f.read_text().replace("Dataset Sequence    : '0002'", "Dataset Sequence    : '0003'"))
        with self.assertRaisesRegex(m.InvalidEvidence, 'dataset sequence mismatch'):
            m.review()


if __name__ == '__main__':
    unittest.main()
