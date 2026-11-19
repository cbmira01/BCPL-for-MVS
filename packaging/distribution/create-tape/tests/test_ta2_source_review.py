"""TA.2 offline negative tests for saved read-only MVS source evidence."""
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_DIR = ROOT / 'packaging/distribution/create-tape/scripts'


def imported(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(SCRIPT_DIR / filename))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


review = imported('ta2_source_review_tests', 'ta2-source-review')
source = imported('ta2_source_reviewer_preflight', 'ta2-source-preflight')


class SavedSourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / 'workarea/ta2-source-preflight/20261119T140206Z-15135'
        self.evidence.mkdir(parents=True)
        self.items = []
        self.records = []
        for i in range(18):
            key = f'SRC{i + 1:02d}'
            dsn = f'HERC02.BCPL.S{i + 1:03d}'
            selected = [f'M{n:07d}' for n in range(7 + (i == 17))]
            extras = [f'X{n:07d}' for n in range(4 + (i >= 14))]
            dcb = {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}
            item = {'key': key, 'dsn': dsn, 'dcb': dcb,
                    'selected': selected, 'sequence': i + 3}
            self.items.append(item)
            stat = (f'Dataset:   {dsn} ({key})\n'
                    '    Job:9169,  Volume:TSO003,  DSORG:PO,  RECFM:FB,  '
                    'LRECL:80,  BLKSIZE:800\n')
            listing = dsn + ':\n' + ''.join('    ' + x + '\n' for x in selected + extras)
            (self.evidence / f'{key}.stat.txt').write_text('RC=0\n' + stat)
            (self.evidence / f'{key}.ls.txt').write_text('RC=0\n' + listing)
            self.records.append({'key': key, 'source_dsn': dsn,
                                 'tape_sequence': i + 3, 'source_volume': 'TSO003',
                                 'observed_members': len(selected + extras),
                                 'selected_members': len(selected),
                                 'missing_members': [], 'development_extras': extras})
        self.summary = {'status': 'PASS (source metadata only)',
                        'source_dataset_count': 18, 'errors': [],
                        'results': self.records}
        self._save()

    def _save(self):
        (self.evidence / 'summary.json').write_text(json.dumps(self.summary, indent=2) + '\n')
        files = sorted(p for p in self.evidence.iterdir() if p.name != 'SHA256SUMS')
        (self.evidence / 'SHA256SUMS').write_text(''.join(
            hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
            for p in files))

    def audit(self):
        return review.inspect(self.evidence, self.items, source, root=self.root)

    def test_pass_127_curated_76_excluded(self):
        x = self.audit()
        self.assertEqual((x['checked_libraries'], x['curated_members'],
                          x['observed_members'], x['excluded_development_members']),
                         (18, 127, 203, 76))

    def test_relative_evidence_path_from_cwd(self):
        import os
        relative = Path(os.path.relpath(self.evidence, Path.cwd()))
        self.assertEqual(review.inspect(relative, self.items, source, root=self.root)
                         ['curated_members'], 127)

    def test_stat_checksum_drift_refused(self):
        with (self.evidence / 'SRC01.stat.txt').open('a') as f: f.write('tamper\n')
        with self.assertRaisesRegex(review.Refusal, 'checksum mismatch'): self.audit()

    def test_summary_checksum_drift_refused(self):
        with (self.evidence / 'summary.json').open('a') as f: f.write(' ') 
        with self.assertRaisesRegex(review.Refusal, 'checksum mismatch'): self.audit()

    def test_failed_inquiry_refused(self):
        p = self.evidence / 'SRC01.ls.txt'
        p.write_text(p.read_text().replace('RC=0', 'RC=2', 1))
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'return code'): self.audit()

    def test_missing_report_refused(self):
        (self.evidence / 'SRC01.ls.txt').unlink()
        with self.assertRaisesRegex(review.Refusal, 'missing/extra'): self.audit()

    def test_extra_report_refused(self):
        (self.evidence / 'surplus.txt').write_text('x')
        with self.assertRaisesRegex(review.Refusal, 'missing/extra'): self.audit()

    def test_linked_evidence_refused(self):
        p = self.evidence / 'SRC02.ls.txt'
        p.unlink()
        p.symlink_to(self.evidence / 'SRC01.ls.txt')
        with self.assertRaisesRegex(review.Refusal, 'missing/linked'): self.audit()

    def test_source_dsn_spoof_refused(self):
        p = self.evidence / 'SRC01.stat.txt'
        p.write_text(p.read_text().replace('HERC02.BCPL.S001', 'HERC02.BCPL.WRONG'))
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'mismatch'): self.audit()

    def test_wrong_dcb_refused(self):
        p = self.evidence / 'SRC01.stat.txt'
        p.write_text(p.read_text().replace('BLKSIZE:800', 'BLKSIZE:6160'))
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'DCB'): self.audit()

    def test_selected_member_missing_refused(self):
        p = self.evidence / 'SRC01.ls.txt'
        p.write_text(p.read_text().replace('    M0000001\n', ''))
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'selected member absent'): self.audit()

    def test_forged_summary_extras_refused(self):
        self.records[0]['development_extras'] = []
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'summary disagrees'): self.audit()

    def test_forged_summary_volume_refused(self):
        self.records[0]['source_volume'] = 'TSO002'
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'summary disagrees'): self.audit()

    def test_forged_summary_member_total_refused(self):
        self.records[0]['observed_members'] += 1
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'summary disagrees'): self.audit()

    def test_forged_summary_reordered_refused(self):
        self.records[0], self.records[1] = self.records[1], self.records[0]
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'summary disagrees'): self.audit()

    def test_failed_collector_summary_refused(self):
        self.summary['errors'] = ['SRC01 error']
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'failed or incomplete'): self.audit()

    def test_missing_summary_record_refused(self):
        self.records.pop()
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'result count'): self.audit()

    def test_bad_selected_count_refused(self):
        self.items[0]['selected'].pop()
        with self.assertRaisesRegex(review.Refusal, 'count drift'): self.audit()

    def test_unrecognized_run_id_refused(self):
        renamed = self.evidence.with_name('wrong-name')
        self.evidence.rename(renamed)
        self.evidence = renamed
        with self.assertRaisesRegex(review.Refusal, 'timestamped'): self.audit()

    def test_run_directory_symlink_refused(self):
        linked = self.evidence.with_name('20261119T140207Z-15136')
        linked.symlink_to(self.evidence, target_is_directory=True)
        self.evidence = linked
        with self.assertRaisesRegex(review.Refusal, 'linked'): self.audit()

    def test_duplicate_sha256_line_refused(self):
        p = self.evidence / 'SHA256SUMS'
        first = p.read_text().splitlines()[0]
        p.write_text(p.read_text() + first + '\n')
        with self.assertRaisesRegex(review.Refusal, 'duplicated'): self.audit()

    def test_bad_member_directory_refused(self):
        p = self.evidence / 'SRC01.ls.txt'
        p.write_text(p.read_text().replace('HERC02.BCPL.S001:', 'HERC02.BCPL.S999:'))
        self._save()
        with self.assertRaisesRegex(review.Refusal, 'heading'): self.audit()


if __name__ == '__main__':
    unittest.main()
