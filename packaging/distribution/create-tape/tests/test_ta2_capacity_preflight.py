"""TA.2 synthetic, offline parsing and safety tests for read-only MVS capacity."""
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / 'packaging/distribution/create-tape/scripts'


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(SCRIPTS / path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


cap = load('ta2_capacity_tests', 'ta2-capacity-preflight')
source = load('ta2_capacity_source_tests', 'ta2-source-preflight')


class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.items = []
        self.blocks = []
        for j in range(18):
            key = f'TEST{j:02d}'
            dsn = f'HERC02.BCPL.TEST{j:02d}'
            dc = dict(dsorg='PO', recfm='U' if j == 9 else 'FB',
                      lrecl=0 if j == 9 else 80,
                      blksize=6144 if j == 9 else 800)
            members = ['A'] * (8 if j == 17 else 7)
            self.items.append(dict(key=key, dsn=dsn, dcb=dc,
                                   sequence=j + 3, selected=members))
            self.blocks.append(f'Dataset:   {dsn} ({key})\n'
                               f'    Job:1234,  Volume:TSO003,  DSORG:PO,  RECFM:{dc["recfm"]},  '
                               f'LRECL:{dc["lrecl"]},  BLKSIZE:{dc["blksize"]}\n'
                               '    Tracks: allocated 30, through HWM 21, tail free 9, '
                               'utilization 70.0%, extents 1\n'
                               '    Directory blocks: allocated 10, used 5, unused 5\n')
        self.report = ''.join(self.blocks)
        self.receipt = dict(status='PASS (saved MVS source metadata only)',
                            checked_libraries=18, curated_members=127,
                            excluded_development_members=76)

    def runreconcile(self, report=None, receipt=None):
        return cap.reconcile(self.report if report is None else report,
                             self.items, source, self.receipt if receipt is None else receipt)

    def test_complete_source_metadata_and_space_pass(self):
        result = self.runreconcile()
        self.assertEqual((result['libraries'], result['selected_members'],
                          result['excluded_development_members']), (18, 127, 76))
        self.assertEqual((result['results'][9]['source_volume'],
                          result['results'][9]['tracks_through_hwm']), ('TSO003', 21))

    def test_missing_source_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'missing'):
            self.runreconcile(''.join(self.blocks[1:]))

    def test_duplicate_source_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'duplicate'):
            self.runreconcile(self.report + self.blocks[1])

    def test_bad_source_identity_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'DSN differs'):
            self.runreconcile(self.report.replace('HERC02.BCPL.TEST00', 'HERC02.BCPL.WRONG'))

    def test_wrong_dcb_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'DCB'):
            self.runreconcile(self.report.replace('BLKSIZE:800', 'BLKSIZE:816', 1))

    def test_source_volume_absent_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'volume'):
            self.runreconcile(self.report.replace('Volume:TSO003', 'VoluXX:TSO003', 1))

    def test_unavailable_iehlist_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'IEHLIST'):
            self.runreconcile(self.report.replace('Tracks: allocated 30, through HWM 21, tail free 9, '
                                                   'utilization 70.0%, extents 1', 'Tracks: unavailable', 1))

    def test_unavailable_directory_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'IEHLIST'):
            self.runreconcile(self.report.replace('Directory blocks: allocated 10, used 5, unused 5',
                                                   'Directory blocks: unavailable', 1))

    def test_inconsistent_track_counts_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'inconsistent DASD'):
            self.runreconcile(self.report.replace('through HWM 21', 'through HWM 22', 1))

    def test_inconsistent_directory_counts_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'inconsistent source PDS'):
            self.runreconcile(self.report.replace('used 5, unused 5', 'used 8, unused 5', 1))

    def test_multiple_space_rows_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'unambiguous'):
            self.runreconcile(self.report.replace('    Directory blocks: allocated 10, used 5, unused 5\n',
                                                   '    Directory blocks: allocated 10, used 5, unused 5\n'
                                                   '    Directory blocks: allocated 10, used 5, unused 5\n', 1))

    def test_missing_metadata_receipt_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'not passed'):
            self.runreconcile(receipt={**self.receipt, 'curated_members': 126})

    def test_missing_or_extra_source_count_refused(self):
        self.items.pop()
        with self.assertRaisesRegex(cap.Refusal, '18 distinct'):
            self.runreconcile()

    def test_empty_stat_output_refused(self):
        with self.assertRaisesRegex(cap.Refusal, 'no managed'):
            self.runreconcile('')


if __name__ == '__main__':
    unittest.main()


class CapacityPersistenceTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def test_success_receipt_includes_source_pins(self):
        review = {'summary_sha256': 'a' * 64, 'sha256sums_sha256': 'b' * 64,
                  'evidence_directory': 'workarea/ta2-source-preflight/20261119T140206Z-15135'}
        cap.put(self.dir / 'dspal-stat-all.txt', b'RC=0\nDataset: TEST\n')
        cap.persist(self.dir, review, {'status': 'PASS'})
        import json
        obj = json.loads((self.dir / 'summary.json').read_text())
        self.assertEqual(obj['source_review_summary_sha256'], 'a' * 64)
        self.assertIn('source_evidence_directory', obj)
        self.assertEqual(len((self.dir / 'SHA256SUMS').read_text().splitlines()), 2)

    def test_never_overwrite_existing_evidence(self):
        cap.put(self.dir / 'original.txt', b'original')
        with self.assertRaisesRegex(cap.Refusal, 'overwritten'):
            cap.put(self.dir / 'original.txt', b'modified')
        self.assertEqual((self.dir / 'original.txt').read_bytes(), b'original')

    def test_failed_inquiry_receipt_is_explicitly_refused(self):
        import json
        cap.put(self.dir / 'dspal-stat-all.txt', b'RC=2\nERROR\n')
        cap.record_failure(self.dir, 'MVS inquiry failed')
        self.assertEqual(json.loads((self.dir / 'failure.json').read_text())['status'], 'REFUSED')
        self.assertEqual(len((self.dir / 'SHA256SUMS').read_text().splitlines()), 2)
