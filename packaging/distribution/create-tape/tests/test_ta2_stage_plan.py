"""Synthetic, independent TA.2 stage planning and MVS receipt refusal tests."""
import hashlib
import copy
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT / 'packaging/distribution/create-tape/scripts/ta2-stage-plan'
loader = importlib.machinery.SourceFileLoader('ta2_stage_plan_test', str(TOOL))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)


class FakeCapacity:
    class Refusal(ValueError):
        pass

    def __init__(self, records):
        self.records = records

    def reconcile(self, report, items, source, receipt):
        if report != 'MVS CAPACITY ORIGINAL\n':
            if report == 'MVS CAPACITY DRIFT\n':
                x = self.record(items, receipt)
                x['results'][0]['tracks_allocated'] = 99
                return x
            raise self.Refusal('invalid MVS capacity report')
        return self.record(items, receipt)

    def record(self, items, receipt):
        return {'status': 'PASS (read-only source capacity observation)',
                'libraries': 18, 'selected_members': 127,
                'excluded_development_members': receipt['excluded_development_members'],
                'results': copy.deepcopy(self.records),
                'qualification': 'IEHLIST tracks through HWM are not exact curated member footprint; staging allocation unapproved'}


class StagePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_dir = self.root / 'workarea/ta2-capacity-preflight/20261119T150315Z-16868'
        self.run_dir.mkdir(parents=True)
        self.items = []
        self.rows = []
        for i in range(18):
            n = i + 3
            member_count = 8 if i == 17 else 7
            key = f'SRC{i+1:02d}'
            dsn = f'HERC02.BCPL.S{i+1:03d}'
            item = {'key': key, 'dsn': dsn, 'sequence': n,
                    'dcb': {'dsorg': 'PO', 'recfm': 'U' if n == 12 else 'FB',
                            'lrecl': 0 if n == 12 else 80,
                            'blksize': 6144 if n == 12 else 800},
                    'selected': [f'M{x:07d}' for x in range(member_count)]}
            row = {'key': key, 'dsn': dsn, 'sequence': n,
                   'source_volume': 'TSO003', 'selected_members': member_count,
                   'tracks_allocated': 20+i, 'tracks_through_hwm': 16+i,
                   'tracks_free_tail': 4, 'extents': 1,
                   'directory_allocated': 10, 'directory_used': 7, 'directory_free': 3}
            self.items.append(item)
            self.rows.append(row)
        self.reviewed = {'evidence_directory': 'workarea/ta2-source-preflight/20261119T140206Z-15135',
                         'summary_sha256': 'a'*64,
                         'sha256sums_sha256': 'b'*64,
                         'excluded_development_members': 76}
        self.capacity = FakeCapacity(self.rows)
        self.saved = self.capacity.record(self.items, self.reviewed)
        self.saved.update({'source_evidence_directory': self.reviewed['evidence_directory'],
                           'source_review_summary_sha256': self.reviewed['summary_sha256'],
                           'source_review_sha256sums_sha256': self.reviewed['sha256sums_sha256']})
        self.report = 'RC=0\nMVS CAPACITY ORIGINAL\n'
        self._save()

    def _save(self):
        (self.run_dir / 'summary.json').write_text(json.dumps(self.saved, indent=2) + '\n')
        (self.run_dir / 'dspal-stat-all.txt').write_text(self.report)
        lines = [hashlib.sha256((self.run_dir / filename).read_bytes()).hexdigest() +
                 '  ' + filename for filename in ('summary.json', 'dspal-stat-all.txt')]
        (self.run_dir / 'SHA256SUMS').write_text('\n'.join(lines) + '\n')

    def raw(self):
        return mod.read_capacity(self.root, self.run_dir)

    def replay(self):
        return mod.replay_capacity(self.raw(), self.reviewed, self.items,
                                   self.capacity, types.SimpleNamespace(Refusal=ValueError))

    def test_pass_saved_evidence(self):
        result = self.replay()
        self.assertEqual((result['libraries'], result['selected_members'],
                          result['excluded_development_members']), (18,127,76))

    def test_worksheet_no_unapproved_names_or_space(self):
        plan = mod.make_worksheet(self.replay(), self.items)
        self.assertEqual((plan['source_pds'], plan['selected_members'],
                          plan['excluded_development_members']), (18, 127, 76))
        self.assertEqual([x['tape_sequence'] for x in plan['sources']], list(range(3,21)))
        self.assertTrue(all(x['staging_dsn'] is None and x['stage_space'] is None
                            and not x['allocation_approved'] for x in plan['sources']))
        self.assertEqual(plan['sources'][9]['source_dcb']['recfm'], 'U')
        self.assertEqual(plan['sources'][9]['source_dcb']['blksize'], 6144)
        self.assertEqual(sum(len(x['selected_members']) for x in plan['sources']), 127)

    def test_checksum_stat_drift(self):
        (self.run_dir/'dspal-stat-all.txt').write_text('changed\n')
        with self.assertRaisesRegex(mod.Refusal, 'checksum drift'): self.raw()

    def test_checksum_summary_drift(self):
        (self.run_dir/'summary.json').write_text('changed\n')
        with self.assertRaisesRegex(mod.Refusal, 'checksum drift'): self.raw()

    def test_failed_mvs_inquiry(self):
        self.report=self.report.replace('RC=0','RC=2')
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'RC=0'): self.replay()

    def test_no_mvs_rc_header(self):
        self.report=self.report.replace('RC=0\n','')
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'RC=0'): self.replay()

    def test_summary_is_not_accepted_by_itself(self):
        self.saved['results'][0]['tracks_allocated'] += 1
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'summary mismatch'): self.replay()

    def test_receipt_source_evidence_bindings(self):
        self.saved['source_review_summary_sha256'] = 'c'*64
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'bind'): self.replay()

    def test_receipt_wrong_extras(self):
        self.saved['excluded_development_members'] = 999
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'summary mismatch'): self.replay()

    def test_empty_checksum_list(self):
        (self.run_dir/'SHA256SUMS').write_text('')
        with self.assertRaisesRegex(mod.Refusal, 'incomplete'): self.raw()

    def test_duplicate_checksum(self):
        p=self.run_dir/'SHA256SUMS'
        p.write_text(p.read_text()+p.read_text().splitlines()[0]+'\n')
        with self.assertRaisesRegex(mod.Refusal, 'duplicate'): self.raw()

    def test_bad_checksum_entry(self):
        p=self.run_dir/'SHA256SUMS'
        p.write_text(p.read_text().replace('  summary.json',' summary.json'))
        with self.assertRaisesRegex(mod.Refusal, 'malformed'): self.raw()

    def test_extra_file(self):
        (self.run_dir/'anything').write_text('x')
        with self.assertRaisesRegex(mod.Refusal, 'missing/unexpected'): self.raw()

    def test_missing_file(self):
        (self.run_dir/'summary.json').unlink()
        with self.assertRaisesRegex(mod.Refusal, 'missing/unexpected'): self.raw()

    def test_symlinked_saved_file(self):
        path=self.run_dir/'summary.json'
        path.unlink()
        path.symlink_to(self.run_dir/'dspal-stat-all.txt')
        with self.assertRaisesRegex(mod.Refusal, 'missing/linked'): self.raw()

    def test_symlinked_run_directory(self):
        path=self.run_dir.with_name('20261119T150316Z-16869')
        path.symlink_to(self.run_dir, target_is_directory=True)
        with self.assertRaisesRegex(mod.Refusal, 'unsafe capacity run'): mod.read_capacity(self.root,path)

    def test_run_path_outside_private_root(self):
        with self.assertRaisesRegex(mod.Refusal, 'unsafe capacity run'): mod.read_capacity(self.root, self.root)

    def test_wrong_directory_name(self):
        path=self.run_dir.with_name('NOT_A_RUN')
        self.run_dir.rename(path)
        with self.assertRaisesRegex(mod.Refusal, 'unsafe capacity run'): mod.read_capacity(self.root,path)

    def test_compare_current_unchanged(self):
        self.assertEqual(mod.compare_current('MVS CAPACITY ORIGINAL\n', self.replay(),
                        self.items, self.capacity,
                        types.SimpleNamespace(Refusal=ValueError), self.reviewed)['libraries'], 18)

    def test_compare_current_drift(self):
        with self.assertRaisesRegex(mod.Refusal, 'current MVS source'):
            mod.compare_current('MVS CAPACITY DRIFT\n', self.replay(), self.items,
                                self.capacity, types.SimpleNamespace(Refusal=ValueError), self.reviewed)

    def test_noncontiguous_sequence(self):
        self.items[0]['sequence']=25
        with self.assertRaisesRegex(mod.Refusal, 'sequence/source mismatch'): mod.make_worksheet(self.replay(),self.items)

    def test_duplicate_selected_member(self):
        self.items[0]['selected'][0]=self.items[0]['selected'][1]
        with self.assertRaisesRegex(mod.Refusal, 'duplicate selected'): mod.make_worksheet(self.replay(),self.items)

    def test_wrong_selected_count(self):
        self.items[0]['selected'].pop()
        with self.assertRaisesRegex(mod.Refusal, 'selection count mismatch'): mod.make_worksheet(self.replay(),self.items)

    def test_unknown_summary_field(self):
        self.saved['unexpected']='x'
        self._save()
        with self.assertRaisesRegex(mod.Refusal, 'unexpected/missing fields'): self.replay()

    def test_bad_summary_json(self):
        (self.run_dir/'summary.json').write_text('INVALID\n')
        self._save()  # reset valid before corrupting with fresh checksum
        (self.run_dir/'summary.json').write_text('NOT JSON\n')
        p=self.run_dir/'SHA256SUMS'
        contents=[]
        for f in ('summary.json','dspal-stat-all.txt'):
            contents.append(hashlib.sha256((self.run_dir/f).read_bytes()).hexdigest()+'  '+f)
        p.write_text('\n'.join(contents)+'\n')
        with self.assertRaisesRegex(mod.Refusal, 'JSON'): self.replay()

    def _live(self, *, mvs_rc=0, mvs_report='MVS CAPACITY ORIGINAL\n', review_error=None):
        """Run the full entry point with faked MVS; assert no write calls."""
        source = types.SimpleNamespace(
            core=lambda: types.SimpleNamespace(
                load=lambda path: {'phase': 'design'} if 'ta0-inventory' in str(path) else {},
                check=lambda *args, **kwargs: {'logical_datasets': 20}),
            expected_sources=lambda manifest, dspal: self.items,
            Refusal=ValueError)
        def inspect(evidence, items, source):
            if review_error:
                raise mod.Refusal(review_error)
            return self.reviewed
        reviewer = types.SimpleNamespace(inspect=inspect)
        modules = iter([source, reviewer, self.capacity])
        def importer(name, path):
            return next(modules)
        report = Mock(returncode=mvs_rc, stdout=mvs_report, stderr='')
        fake_process = Mock(return_value=report)
        outroot = self.root / 'workarea/ta2-stage-plan'
        with patch.object(mod, 'ROOT', self.root), patch.object(mod, 'OUT', outroot), \
             patch.object(mod, 'import_script', side_effect=importer), \
             patch.object(mod.subprocess, 'run', fake_process):
            rc = mod.main(['--live', '--source-evidence', self.reviewed['evidence_directory'],
                           '--capacity-evidence', str(self.run_dir)])
        return rc, fake_process, outroot

    def test_live_entry_is_read_only(self):
        rc, executed, folder = self._live()
        self.assertEqual(rc, 0)
        executed.assert_called_once()
        self.assertEqual(executed.call_args.args[0], ['tools/datasets/dspal', 'stat'])
        evidence_dirs = list(folder.iterdir())
        self.assertEqual(len(evidence_dirs), 1)
        evidence = evidence_dirs[0]
        self.assertEqual({p.name for p in evidence.iterdir()},
                         {'dspal-stat-all.txt','stage-worksheet.json','SHA256SUMS'})
        worksheet = json.loads((evidence/'stage-worksheet.json').read_text())
        self.assertEqual(worksheet['selected_members'], 127)
        self.assertTrue(all(entry['staging_dsn'] is None for entry in worksheet['sources']))
        checksum_lines = (evidence/'SHA256SUMS').read_text().splitlines()
        self.assertEqual(len(checksum_lines), 2)
        for line in checksum_lines:
            h, filename = line.split('  ')
            self.assertEqual(h, hashlib.sha256((evidence/filename).read_bytes()).hexdigest())

    def test_live_mvs_query_failure_preserves_receipt(self):
        rc, executed, folder = self._live(mvs_rc=8)
        self.assertEqual(rc, 1)
        executed.assert_called_once()
        evidence, = folder.iterdir()
        self.assertEqual({p.name for p in evidence.iterdir()},
                         {'dspal-stat-all.txt','failure.json','SHA256SUMS'})
        self.assertIn('failed', json.loads((evidence/'failure.json').read_text())['reason'])

    def test_live_mvs_metadata_drift_preserves_refusal(self):
        rc, executed, folder = self._live(mvs_report='MVS CAPACITY DRIFT\n')
        self.assertEqual(rc, 1)
        executed.assert_called_once()
        evidence, = folder.iterdir()
        self.assertEqual(json.loads((evidence/'failure.json').read_text())['status'], 'REFUSED')
        self.assertFalse((evidence/'stage-worksheet.json').exists())

    def test_failed_source_review_prevents_any_mvs_query(self):
        rc, executed, folder = self._live(review_error='source failed')
        self.assertEqual(rc, 1)
        executed.assert_not_called()
        self.assertFalse(folder.exists())

    def test_live_missing_evidence_refuses_without_mvs(self):
        with patch.object(mod.subprocess, 'run') as executed:
            self.assertEqual(mod.main(['--live']), 1)
            executed.assert_not_called()

    def test_nonlive_inert(self):
        self.assertEqual(mod.main([]), 0)
        self.assertEqual(mod.main(['--source-evidence',str(self.run_dir)]), 1)


if __name__=='__main__': unittest.main()
