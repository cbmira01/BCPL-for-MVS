"""Independent 21-dataset HETMAP structure tests; no guest or Docker calls."""
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc2-aws-review'
loader = importlib.machinery.SourceFileLoader('ta2_rc2_aws', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(n=21):
    labels = ["Label               : 'VOL1'", "Volume Serial       : 'BC0002'"]
    files = []
    for seq in range(1, n+1):
        name = f'BCPL.BT{seq:04d}'
        for what in ('HDR1', 'HDR2', 'EOF1', 'EOF2'):
            labels.append(f"Label               : '{what}'")
            if what in ('HDR1', 'EOF1'):
                labels.extend([f"Dataset ID          : '{name}'",
                               "Volume Serial       : 'BC0002'",
                               f"Dataset Sequence    : '{seq:04d}'"])
        files.extend([3 if seq == 1 else 2, 7 if seq == 12 else 3, 2])
    files.append(0)
    body=''.join(f'File # : {i}\nBlocks : {count}\n' for i,count in enumerate(files,1))
    footer=f'Summary             :\nFiles               : {len(files)}\nBlocks              : {sum(files)}\nUncompressed bytes  : 1957296\n'
    return '\n'.join(labels)+'\n', body+footer


class TestAWS(unittest.TestCase):
    def setUp(self): self.labels,self.files=fixture()
    def test_21_and_64_files(self):
        out=mod.evaluate(self.labels,self.files)
        self.assertEqual(out['logical_datasets'], 21)
        self.assertEqual(out['physical_files'], 64)
        self.assertEqual(out['payload_blocks'], 7+3*20)
        self.assertEqual(out['dataset_names'][-1], 'BCPL.BT0021')
    def test_wrong_volser(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels.replace("'BC0002'", "'BC0001'",1),self.files)
    def test_wrong_midstream_volser(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels.replace("'BC0002'", "'BC0001'"),self.files)
    def test_wrong_header_name(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels.replace("'BCPL.BT0011'", "'BCPL.BT0012'"),self.files)
    def test_wrong_eof_sequence(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels.replace("'0011'", "'0001'"),self.files)
    def test_label_missing(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels.replace("Label               : 'HDR2'", "",1),self.files)
    def test_unexpected_extra_label(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels+"Label               : 'EOV1'\n",self.files)
    def test_empty_data_file(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('Blocks : 7', 'Blocks : 0'))
    def test_unexpected_header_size(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('Blocks : 3', 'Blocks : 2',1))
    def test_terminal_nonempty(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('File # : 64\nBlocks : 0','File # : 64\nBlocks : 1'))
    def test_duplicate_file(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('Summary             :', 'File # : 65\nBlocks : 0\nSummary             :',1))
    def test_wrong_count(self):
        labels,files=fixture(20)
        with self.assertRaises(mod.Refusal): mod.evaluate(labels,files)
    def test_missing_blocks(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('Blocks : 7','',1))
    def test_wrong_numbering(self):
        with self.assertRaises(mod.Refusal): mod.evaluate(self.labels,self.files.replace('File # : 22','File # : 23'))
    def test_no_guess_on_short_input(self):
        with self.assertRaises(mod.Refusal): mod.evaluate('VOL1','File # : 1\nBlocks : 0')

    def test_real_hetmap_footer_does_not_duplicate_file_64_blocks(self):
        result=mod.files_report(self.files)
        self.assertEqual(len(result),64)
        self.assertEqual(result[-1],0)
    def test_missing_footer_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'summary missing'):
            mod.evaluate(self.labels, self.files.split('Summary')[0])
    def test_duplicate_footer_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'summary missing'):
            mod.evaluate(self.labels, self.files + self.files[self.files.index('Summary'):])
    def test_footer_block_total_mismatch_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'does not reconcile'):
            mod.evaluate(self.labels, self.files.replace('Blocks              : 152','Blocks              : 9999'))
    def test_footer_file_count_mismatch_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'does not reconcile'):
            mod.evaluate(self.labels, self.files.replace('Files               : 64','Files               : 63'))
    def test_double_file_block_rejected(self):
        with self.assertRaisesRegex(mod.Refusal,'number/block'):
            mod.evaluate(self.labels, self.files.replace('File # : 64\nBlocks : 0','File # : 64\nBlocks : 0\nBlocks : 0'))

if __name__=='__main__': unittest.main()
