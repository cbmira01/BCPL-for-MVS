"""Offline tests for shared tape JCL and evidence checks; no MVS operations."""
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import release as r


def fixture(count=5):
    rows = [{'sequence': 1, 'kind': 'sequential_text', 'group': 'common',
             'producer_source_dsn': 'TEST.STAGE.BT0001',
             'target_dcb': {'dsorg': 'PS', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}}]
    for n in range(2, count+1):
        rows.append({'sequence': n, 'kind': 'pds_unload',
                     'group': 'common' if n < 4 else 'mr10' if n % 2 == 0 else 'native',
                     'producer_source_dsn': f'TEST.STAGE.BT{n:04d}',
                     'members': ['COPY'] if n == 2 else ['ONE', 'TWO'],
                     'target_dsn_template': f'{{HLQ}}.BCPL.D{n:04d}',
                     'target_dcb': {'dsorg': 'PO', 'recfm': 'U', 'lrecl': 0, 'blksize': 6144}
                         if n == 4 else {'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800}})
    return {'schema_version': 1, 'phase': 'candidate', 'release': {'candidate_id': 'EXAMPLE'},
            'volume': {'volser': 'BC0010', 'format': 'aws', 'labeling': 'SL',
                       'volume_ordinal': 1, 'registry_reservation': 'EXAMPLE'}, 'datasets': rows,
            'profiles': {'mr10-only': ['common', 'mr10'], 'native-only': ['common', 'native'],
                         'combined': ['common', 'mr10', 'native']}}


def hetmap(vol, count):
    labels = ["Label : 'VOL1'", f"Volume Serial : '{vol}'"]
    blocks = []
    for n in range(1, count+1):
        for kind in ('HDR1', 'HDR2', 'EOF1', 'EOF2'):
            labels.append(f"Label : '{kind}'")
            if kind in ('HDR1', 'EOF1'):
                labels += [f"Dataset ID : 'BCPL.BT{n:04d}'", f"Volume Serial : '{vol}'",
                           f"Dataset Sequence : '{n:04d}'"]
        blocks.extend([3 if n == 1 else 2, n, 2])
    blocks.append(0)
    files = ''.join(f'File # : {n}\nBlocks : {b}\n' for n, b in enumerate(blocks, 1))
    return '\n'.join(labels)+'\n', files+f'Summary :\nFiles : {len(blocks)}\nBlocks : {sum(blocks)}\n'


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.m = fixture()
        self.sizes = {n: (9, 2, 7) for n in range(3, 6)}

    def install(self, profile='combined'):
        return r.render_install_jcl(self.m, self.sizes, profile, hlq='HERC02', site='NEW',
                                    tape_unit='480', dasd_unit='SYSDA', dasd_vol='TSO002')

    def test_writer(self):
        deck = r.render_write_jcl(self.m, unit='481')
        self.assertEqual(deck.count('EXEC PGM=IEBGENER'), 1)
        self.assertEqual(deck.count('EXEC PGM=IEBCOPY'), 4)
        self.assertEqual(deck.count(' SELECT MEMBER='), 7)
        self.assertEqual(deck.count('UNIT=481'), 5)
        self.assertEqual(deck.count('RETAIN,SER=BC0010'), 4)
        self.assertEqual(deck.count('COND=(0,NE)'), 4)
        self.assertIn('LABEL=(5,SL),DISP=(NEW,KEEP,KEEP)', deck)
        self.assertTrue(all(len(l) <= 80 for l in deck.splitlines()))
        self.assertEqual(r.render_write_jcl(self.m, legacy_header=True).splitlines()[0],
                         '//* TA.2 FROZEN CANDIDATE EXAMPLE')

    def test_writer_refusals(self):
        for key, value in [('producer_source_dsn', 'BAD\n//EVIL'),
                           ('producer_source_dsn', 'TEST.STAGE.BT0001'),
                           ('members', []), ('members', ['ONE', 'ONE']), ('members', ['9BAD']),
                           ('sequence', 9), ('kind', 'sequential_text')]:
            with self.subTest(key=key, value=value):
                m = deepcopy(self.m)
                m['datasets'][1][key] = value
                with self.assertRaises(r.Refusal):
                    r.render_write_jcl(m)
        for vol in ('BC0000', 'Q00001', 'BTA101'):
            m = deepcopy(self.m)
            m['volume']['volser'] = vol
            with self.assertRaises(r.Refusal):
                r.render_write_jcl(m)
        with self.assertRaises(r.Refusal):
            r.render_write_jcl(self.m, unit='480,DISP=OLD')
        with self.assertRaises(r.Refusal):
            r.checked_lines(['//A DD X\n//B DD X'])

    def test_install_profiles(self):
        for profile, positions in [('mr10-only', (3, 4)), ('native-only', (3, 5)), ('combined', (3, 4, 5))]:
            with self.subTest(profile=profile):
                deck = self.install(profile)
                self.assertEqual(r.profile_positions(self.m, profile), positions)
                self.assertEqual(deck.count('EXEC PGM=IEBCOPY'), len(positions))
                self.assertEqual(deck.count('DISP=(NEW,CATLG,DELETE)'), len(positions))
                self.assertEqual(deck.count('DIST.INST(COPY)'), len(positions))
                self.assertEqual(deck.count('RECFM=U,BLKSIZE=6144'), int(4 in positions))
                self.assertNotIn('DD *', deck)
                self.assertNotIn('DD DATA', deck)
                self.assertTrue(deck.endswith('//\n'))

    def test_install_refusals(self):
        for key, value in [('target_dsn_template', '{HLQ}.BCPL.DIST.INST'),
                           ('target_dsn_template', '{HLQ}.BCPL.D0003'),
                           ('target_dcb', {'dsorg': 'PO', 'recfm': 'VB'})]:
            old = self.m['datasets'][3][key]
            self.m['datasets'][3][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(r.Refusal):
                self.install()
            self.m['datasets'][3][key] = old
        self.sizes.pop(4)
        with self.assertRaises(r.Refusal):
            self.install()

    def test_tape_structure(self):
        for n in (1, 5, 21, 22):
            labels, files = hetmap('BC0010', n)
            result = r.evaluate_hetmap(labels, files, volser='BC0010', count=n)
            self.assertEqual(result['physical_files'], 3*n+1)
            self.assertEqual(result['payload_blocks'], n*(n+1)//2)
            self.assertEqual(result['dataset_names'][-1], f'BCPL.BT{n:04d}')

    def test_tape_refusals(self):
        labels, files = hetmap('BC0010', 5)
        for l, f in [(labels.replace('BC0010', 'BC0011', 1), files),
                     (labels.replace('BCPL.BT0003', 'BCPL.BT0002', 1), files),
                     (labels.replace("Label : 'HDR2'", '', 1), files),
                     (labels, files.replace('File # : 16\nBlocks : 0', 'File # : 16\nBlocks : 1')),
                     (labels, files.replace('Files : 16', 'Files : 99')),
                     (labels, files.split('Summary')[0]),
                     (labels, files.replace('File # : 2', 'File # : 3', 1))]:
            with self.assertRaises(r.Refusal):
                r.evaluate_hetmap(l, f, volser='BC0010', count=5)

    def test_mr10(self):
        cases = [{'step': 'R01', 'name': 'case', 'title': 'Test', 'golden': ['RP: A 1'], 'expected_code': 0}]
        report = 'EXECUTION CYCLES = 1, CODE = 0\nTEST: Test\nEXP: A 1\nRP: A 1\nEXECUTION CYCLES = 2, CODE = 0\n'
        self.assertTrue(r.inspect_mr10(report, cases)['exp_contract_met'])
        for text in (report.replace('EXP: A 1', ''), report.replace('EXP: A 1', 'EXP: A 2'),
                     report.replace('RP: A 1', 'RP: A 2'), report.replace('TEST: Test', 'TEST: Wrong'),
                     report.replace('CODE = 0', 'CODE = 4'), 'RP: orphan\n'+report, report+report,
                     report.replace('EXECUTION CYCLES = 2, CODE = 0', '')):
            self.assertFalse(r.inspect_mr10(text, cases)['exp_contract_met'])
        with self.assertRaises(r.Refusal):
            r.inspect_mr10('', [])

    def test_canonical_panel(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lines, jcl = [], []
            for i, name in enumerate(r.MR10_CASES, 1):
                src, gold = f'{i}.bcpl', f'{i}.expected'
                (root/src).write_text(f'LET START() BE WRITEF("TEST: {name}*N")\n')
                (root/gold).write_text(f'RP: A {i}\n')
                lines.append('\t'.join((name, 'cat', src, '', '', gold, '0')))
                jcl.append(f'//* EXECUTE CASE {i:02d}: {name}')
            m, j = root/'manifest.tsv', root/'run.jcl'
            m.write_text('\n'.join(lines)+'\n'); j.write_text('\n'.join(jcl)+'\n')
            self.assertEqual(len(r.read_mr10_panel(root, m, j)), 12)
            m.write_text(m.read_text().replace('scalar-vector', 'wrong'))
            with self.assertRaises(r.Refusal):
                r.read_mr10_panel(root, m, j)

    def test_frozen_rc4_rendering(self):
        # Byte digests of the historical renderer's output for the frozen
        # manifest and accepted allocation budget; not tape-byte acceptance.
        root = Path(__file__).resolve().parents[2]
        base = root/'packaging/distribution'
        m = r.read_manifest(base/'manifest/releases/BCPL-0.1.0-rc4.yaml')
        budget = json.loads((base/'create-tape/ta2-stage-space-proposal-20261119.json').read_text())
        sizes = {row['sequence']: (row['primary_tracks'], row['secondary_tracks'], row['directory_blocks'])
                 for row in budget['targets']}
        sizes[21] = (100, 10, 10)
        for row in m['datasets']:
            n = row['sequence']
            row['producer_source_dsn'] = ('HERC02.BCPL.TA3R4S.' if n <= 2 else 'HERC02.BCPL.TA2R3S.') + f'BT{n:04d}'
        digest = lambda text: hashlib.sha256(text.encode('ascii')).hexdigest()
        writer = r.render_write_jcl(m, legacy_header=True)
        self.assertEqual(digest(writer), '3fe498b6513e53add9ff6b22f76cd9fb1caa79c6ca28e80f629d500f501c5976')
        self.assertEqual(writer.count(' SELECT MEMBER='), 150)
        for profile, site, expected in (
            ('mr10-only', 'R4MR', 'cb5cc716837de6c611232b8347ba592d8d6f8bf66dfecab02aa0bb4d0ecea4b6'),
            ('native-only', 'R4NT', 'b17f4e5ec5e84516879db0fc7ee512dfee270b5ca95887f1d68c35e6d7a039e6'),
            ('combined', 'R4CB', '02e706b46a0a84da1da7a07662b93c77b3e33e9c669c839ffceafe63e678a83c'),
        ):
            with self.subTest(profile=profile):
                deck = r.render_install_jcl(m, sizes, profile, hlq='HERC02', site=site,
                                            tape_unit='480', dasd_unit='SYSDA', dasd_vol='TSO002')
                self.assertEqual(digest(deck), expected)

    def test_cli_manifest_and_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            m, s, a = p/'release.yaml', p/'sources.json', p/'alloc.json'
            m.write_text(json.dumps(self.m))
            s.write_text(json.dumps({str(row['sequence']): row['producer_source_dsn'] for row in self.m['datasets']}))
            a.write_text(json.dumps(self.sizes))
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(r.main(['write-jcl', '--manifest', str(m), '--source-map', str(s), '--unit', '480']), 0)
                self.assertIn('LABEL=(5,SL)', out.getvalue())
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(r.main(['install-jcl', '--manifest', str(m), '--allocations', str(a), '--profile', 'combined',
                                         '--hlq', 'HERC02', '--site', 'NEW', '--tape-unit', '480', '--dasd-unit', 'SYSDA', '--dasd-vol', 'TSO002']), 0)
                self.assertEqual(out.getvalue(), self.install())
            s.write_text('{"1":"TEST.A","1":"TEST.B"}')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(r.main(['write-jcl', '--manifest', str(m), '--source-map', str(s), '--unit', '480']), 2)
            m.write_text('invalid: [')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(r.main(['write-jcl', '--manifest', str(m), '--source-map', str(s), '--unit', '480']), 2)


if __name__ == '__main__':
    unittest.main()
