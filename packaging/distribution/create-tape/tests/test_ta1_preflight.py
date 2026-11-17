"""TA.1 safeguards: strictly offline tests, no live JES/Hercules calls."""
import importlib.machinery
import importlib.util
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'ta1-preflight'
loader = importlib.machinery.SourceFileLoader('ta1_preflight', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
ROOT = Path(__file__).resolve().parents[4]


class TestTa1Preflight(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        path = self.root / 'packaging/distribution/create-tape/jcl'
        path.mkdir(parents=True)
        for job in mod.FILES:
            shutil.copyfile(ROOT / 'packaging/distribution/create-tape/jcl' /
                            (job + '.jcl'), path / (job + '.jcl'))
        self.tapes = self.root / 'mvs-state/tape'
        self.tapes.mkdir(parents=True)

    def test_valid_proposal_passes_offline(self):
        mod.validate_contract(self.root)
        mod.validate_image_absent(self.root)

    def test_missing_or_added_write_step_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('//UNLOAD   EXEC PGM=IEBCOPY',
                                             '//EXTRA    EXEC PGM=IEBGENER\n//UNLOAD   EXEC PGM=IEBCOPY'))
        with self.assertRaisesRegex(mod.Refusal, 'step/program'):
            mod.validate_contract(self.root)

    def test_mismatched_second_label_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('LABEL=(2,SL)', 'LABEL=(1,SL)'))
        with self.assertRaisesRegex(mod.Refusal, 'standard labels'):
            mod.validate_contract(self.root)

    def test_missing_condition_gate_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('COND=(0,NE,BOOTSTRP)', 'COND=(0,EQ,BOOTSTRP)'))
        with self.assertRaisesRegex(mod.Refusal, 'successful first step'):
            mod.validate_contract(self.root)

    def test_source_change_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('HERC02.BCPL.DIST.DOCS', 'HERC02.BCPL.BOOT.OBJ'))
        with self.assertRaisesRegex(mod.Refusal, 'dataset identity'):
            mod.validate_contract(self.root)

    def test_first_step_retention_required(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('PRIVATE,RETAIN,SER', 'PRIVATE,SER'))
        with self.assertRaisesRegex(mod.Refusal, 'retention'):
            mod.validate_contract(self.root)

    def test_existing_image_refused(self):
        (self.tapes / mod.IMAGE).write_bytes(b'partial tape evidence')
        with self.assertRaisesRegex(mod.Refusal, 'NEVER overwrite'):
            mod.validate_image_absent(self.root)

    def test_dangling_symlink_refused(self):
        (self.tapes / mod.IMAGE).symlink_to(self.root / 'no-such-image')
        with self.assertRaisesRegex(mod.Refusal, 'NEVER overwrite'):
            mod.validate_image_absent(self.root)

    def test_symlinked_tape_directory_refused(self):
        self.tapes.rmdir()
        self.tapes.symlink_to(self.root / 'target-folder')
        with self.assertRaisesRegex(mod.Refusal, 'unsafe'):
            mod.validate_image_absent(self.root)

    def test_long_card_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text('//* ' + 'A'*80 + '\n' + p.read_text())
        with self.assertRaisesRegex(mod.Refusal, 'width'):
            mod.validate_contract(self.root)

    def test_restore_old_target_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AR002.jcl'
        p.write_text(p.read_text().replace('DISP=(NEW,CATLG,DELETE)', 'DISP=OLD'))
        with self.assertRaisesRegex(mod.Refusal, 'new scratch DASD'):
            mod.validate_contract(self.root)

    def test_wrong_restored_dcb_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AR002.jcl'
        p.write_text(p.read_text().replace('BLKSIZE=800', 'BLKSIZE=400'))
        with self.assertRaisesRegex(mod.Refusal, 'restored DCB'):
            mod.validate_contract(self.root)

    def test_wrong_tape_unit_refused(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text(p.read_text().replace('UNIT=480', 'UNIT=481'))
        with self.assertRaisesRegex(mod.Refusal, 'wrong tape units'):
            mod.validate_contract(self.root)

    def test_mvs_job_card_rejected(self):
        p = self.root / 'packaging/distribution/create-tape/jcl/TA1AWRIT.jcl'
        p.write_text('//BADJOB JOB CLASS=A\n' + p.read_text())
        with self.assertRaisesRegex(mod.Refusal, 'JOB card'):
            mod.validate_contract(self.root)


if __name__ == '__main__':
    unittest.main()
