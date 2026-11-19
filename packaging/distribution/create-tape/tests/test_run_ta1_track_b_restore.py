"""Isolated synthetic tests of TA1B restore; no JES/Hercules actions."""
import hashlib, importlib.util, importlib.machinery, io, json, os, pathlib, tempfile, types, unittest
from unittest.mock import patch, Mock

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / 'scripts/run-ta1-track-b-restore'
loader = importlib.machinery.SourceFileLoader('ta1b_restorer', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
r = importlib.util.module_from_spec(spec)
loader.exec_module(r)

class RestoreTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(dir=HERE.parents[3] / 'workarea')
        self.addCleanup(tmp.cleanup)
        self.base=pathlib.Path(tmp.name)
        self.root=self.base/'repo'
        (self.root/'mvs-state/tape').mkdir(parents=True)
        self.ops=self.root/'workarea/ta1b-operations'
        self.ops.mkdir(parents=True)
        self.tape=self.root/'mvs-state/tape/bcpl-ta1-b-20261117-01.aws'
        self.tape.write_bytes(b'SYNTHETIC AWS FIXTURE - NO LIVE MEDIA')
        digest=hashlib.sha256(self.tape.read_bytes()).hexdigest()
        self.write=self.ops/'BTA102-track-b-write-20261118T235204Z-9548'
        self.write.mkdir()
        self.log=self.ops/'readback-new'
        for name,val in {'ROOT':self.root,'OPS':self.ops,'TAPE':self.tape,'WRITE_LOG':self.write,
                         'ATTEMPT':self.ops/'BTA102-track-b-restore.json','LOG':self.log,
                         'SHA':digest}.items():
            p=patch.object(r,name,val);p.start();self.addCleanup(p.stop)
        (self.ops/'BTA102-track-b-init-write.json').write_text(json.dumps(
           {'state':'STATEFUL_ATTEMPT_STARTED','volser':'BTA102',
            'image':self.tape.name,'job':'TA1BWRIT','no_retry':True}))
        for name,content in {
           'sha256.txt':digest+'  mvs-state/tape/'+self.tape.name+'\n',
           'summary.txt':'JOB 9120  TA1BWRIT\nUNLOAD IEBCOPY RC=0000\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n',
           'labels-final.txt':'VALID SL BTA102',
           'files-final.txt':'VALID 3-8-2-0',
           'map-final.txt':'VALID 3-8-2-0',
           }.items():
            (self.write/name).write_text(content)
        self.writer=types.SimpleNamespace(
           check_summary=lambda s,n:self.assertTrue('JOB 9120' in s and n==9120),
           final_labels=lambda s:self.assertEqual(s,'VALID SL BTA102'),
           physical_files=lambda s:[3,8,2,0] if s=='VALID 3-8-2-0' else [],
           unit_ready=Mock())

    def test_successful_original_write_receipt(self):
        r.write_receipt(self.writer)
    def test_original_sha_changed(self):
        self.tape.write_bytes(b'ALTERED')
        with self.assertRaisesRegex(r.Halt,'SHA-256 differs'):r.write_receipt(self.writer)
    def test_original_job_receipt_changed(self):
        (self.write/'sha256.txt').write_text('bad\n')
        with self.assertRaisesRegex(r.Halt,'receipt mismatch'):r.write_receipt(self.writer)
    def test_source_attempt_missing(self):
        (self.ops/'BTA102-track-b-init-write.json').unlink()
        with self.assertRaisesRegex(r.Halt,'missing/unsafe'):r.write_receipt(self.writer)
    def test_source_attempt_wrong_state(self):
        p=self.ops/'BTA102-track-b-init-write.json';s=json.loads(p.read_text());s['state']='wrong';p.write_text(json.dumps(s))
        with self.assertRaisesRegex(r.Halt,'no-retry receipt mismatch'):r.write_receipt(self.writer)
    def test_source_attempt_symlink_refused(self):
        p=self.ops/'BTA102-track-b-init-write.json';p.unlink();p.symlink_to(self.write/'sha256.txt')
        with self.assertRaisesRegex(r.Halt,'missing/unsafe'):r.write_receipt(self.writer)
    def test_write_phys_layout_mismatch(self):
        (self.write/'map-final.txt').write_text('INVALID')
        with self.assertRaisesRegex(r.Halt,'physical tape layout'):r.write_receipt(self.writer)
    def test_prior_restoration_marker_refused(self):
        r.begin_once()
        with self.assertRaisesRegex(r.Halt,'already recorded'):r.check_paths()
    def test_image_symlink_refused(self):
        self.tape.unlink();self.tape.symlink_to(self.write/'summary.txt')
        with self.assertRaisesRegex(r.Halt,'missing/unsafe'):r.check_sha()
    def test_attempt_permissions_and_one_shot(self):
        r.begin_once();self.assertEqual(r.ATTEMPT.stat().st_mode&0o777,0o600)
        self.assertTrue(json.loads(r.ATTEMPT.read_text())['no_retry'])
        with self.assertRaisesRegex(r.Halt,'never retry'):r.begin_once()
    def fake_preflight(self,hercules,guest='480 3400 O /REMOV'):
        def checked(argv,name,folder):
            if argv[:4]==['tools/mvs/mvs-console','tape','status','0480']:
                return hercules
            if argv[:3]==['tools/mvs/mvs-console','mvs','D U,TAPE']:
                return guest
            raise AssertionError(argv)
        return types.SimpleNamespace(checked=checked)
    def test_tape_state_empty(self):
        p=self.fake_preflight('HHC02279I 0:0480 3420 * IO[2]\n')
        self.assertEqual(r.tape_state(p,self.writer,self.base),'empty')
        self.writer.unit_ready.assert_called_once_with(p,self.base,mounted=False)
    def test_tape_state_mounted(self):
        p=self.fake_preflight('HHC02279I 0:0480 3420 /tk5/tape/'+self.tape.name+' IO[2]\n')
        self.assertEqual(r.tape_state(p,self.writer,self.base),'mounted')
        self.writer.unit_ready.assert_called_once_with(p,self.base,mounted=True)
    def test_foreign_media_displacement_refused(self):
        p=self.fake_preflight('HHC02279I 0:0480 3420 /tk5/tape/not-ours.aws IO[2]\n')
        with self.assertRaisesRegex(r.Halt,'foreign media'):r.tape_state(p,self.writer,self.base)
        self.writer.unit_ready.assert_not_called()
    def test_same_basename_foreign_directory_refused(self):
        p=self.fake_preflight('HHC02279I 0:0480 3420 /elsewhere/tape/'+self.tape.name+' IO[2]\n')
        with self.assertRaisesRegex(r.Halt,'foreign media'):r.tape_state(p,self.writer,self.base)
        self.writer.unit_ready.assert_not_called()
    def test_busy_device_refused(self):
        p=self.fake_preflight('HHC02279I 0:0480 3420 * busy IO[2]\n')
        with self.assertRaisesRegex(r.Halt,'busy'):r.tape_state(p,self.writer,self.base)
    def test_duplicate_hercules_device_refused(self):
        line='HHC02279I 0:0480 3420 * IO[2]\n'
        p=self.fake_preflight(line+line)
        with self.assertRaisesRegex(r.Halt,'ambiguous'):r.tape_state(p,self.writer,self.base)
    def test_other_image_duplicate_volser_refused(self):
        (self.tape.parent/'another.aws').write_bytes(b'tape')
        preflight=types.SimpleNamespace(checked=lambda argv,key,folder:"Label : 'VOL1'",parse_volser=lambda s:'BTA102')
        with self.assertRaisesRegex(r.Halt,'duplicate VOLSER'):r.other_media(preflight,self.base)
    def test_other_image_symlink_refused(self):
        (self.tape.parent/'foreign.aws').symlink_to(self.tape)
        preflight=types.SimpleNamespace(checked=lambda argv,key,folder:'',parse_volser=lambda s:'ABC123')
        with self.assertRaisesRegex(r.Halt,'unknown tape media'):r.other_media(preflight,self.base)
    def fake_after(self,stat,listing):
        def checked(argv,name,folder):return stat if argv[1]=='stat' else listing
        return types.SimpleNamespace(checked=checked)
    def test_restored_dcb_members(self):
        p=self.fake_after('Dataset:   '+r.DEST+'\nDSORG:PO RECFM:U LRECL:0 BLKSIZE:6144 Volume:TSO003',
                          r.DEST+':\n    ICINT19\n')
        self.assertEqual(r.check_restored(p,self.base),'TSO003')
    def test_restored_extra_member_refused(self):
        p=self.fake_after('Dataset:   '+r.DEST+'\nDSORG:PO RECFM:U LRECL:0 BLKSIZE:6144 Volume:TSO003',
                          r.DEST+':\n    ICINT19\n    ALIAS\n')
        with self.assertRaisesRegex(r.Halt,'member inventory'):r.check_restored(p,self.base)
    def test_restored_wrong_dcb_refused(self):
        p=self.fake_after('Dataset:   '+r.DEST+'\nDSORG:PO RECFM:FB LRECL:80 BLKSIZE:800 Volume:TSO003',
                          r.DEST+':\n    ICINT19\n')
        with self.assertRaisesRegex(r.Halt,'PO/U/0/6144'):r.check_restored(p,self.base)
    def test_default_preflight_no_state_change(self):
        with patch.object(r,'helper',side_effect=[self.writer,Mock(),Mock()]), \
             patch.object(r,'precheck',return_value='empty'), \
             patch.object(r.sys,'stdout',io.StringIO()), \
             patch.object(r,'begin_once') as once,patch.object(r,'restore_job') as restore:
            self.assertEqual(r.operation(False),0)
        once.assert_not_called();restore.assert_not_called();self.assertFalse(r.ATTEMPT.exists())
    def test_confirmation_denial_no_state_change(self):
        with patch.object(r,'helper',side_effect=[self.writer,Mock(),Mock()]), \
             patch.object(r,'precheck',return_value='empty'), \
             patch.object(r.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',return_value='NO'), \
             patch.object(r.sys,'stdout',io.StringIO()), \
             patch.object(r,'begin_once') as once,patch.object(r,'restore_job') as restore:
            with self.assertRaisesRegex(r.Halt,'no explicit restore'):r.operation(True)
        once.assert_not_called();restore.assert_not_called()
    def test_two_preflights_before_attempt(self):
        def precheck(*args):
            if args[-1].name=='preflight-second':raise r.Halt('source changed')
            return 'empty'
        with patch.object(r,'helper',side_effect=[self.writer,Mock(),Mock()]), \
             patch.object(r,'precheck',side_effect=precheck), \
             patch.object(r.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',return_value='RESTORE BTA102 ICINT19'), \
             patch.object(r.sys,'stdout',io.StringIO()):
            with self.assertRaisesRegex(r.Halt,'source changed'):r.operation(True)
        self.assertFalse(r.ATTEMPT.exists())
    def test_successful_mock_restoration_one_mount_and_one_submit(self):
        commands=[]
        def checked(argv,name,folder):commands.append(argv);return 'OK'
        p=types.SimpleNamespace(checked=checked)
        with patch.object(r,'helper',side_effect=[self.writer,p,Mock()]), \
             patch.object(r,'precheck',return_value='empty'), \
             patch.object(r.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',side_effect=['RESTORE BTA102 ICINT19','SUBMIT TA1BREST BTA102']), \
             patch.object(r,'tape_state',side_effect=['empty','mounted']), \
             patch.object(r,'restore_job',return_value=9130) as submit, \
             patch.object(r,'check_restored',return_value='TSO003'), \
             patch.object(r.sys,'stdout',io.StringIO()):
            self.assertEqual(r.operation(True),0)
        submit.assert_called_once()
        self.assertEqual(len([x for x in commands if 'mount' in x]),1)
        self.assertTrue(r.ATTEMPT.exists())
    def test_tape_remains_untouched_in_mock_restore(self):
        original=self.tape.read_bytes()
        p=types.SimpleNamespace(checked=lambda a,b,c:'OK')
        with patch.object(r,'helper',side_effect=[self.writer,p,Mock()]), \
             patch.object(r,'precheck',return_value='mounted'), \
             patch.object(r.sys.stdin,'isatty',return_value=True), \
             patch('builtins.input',side_effect=['RESTORE BTA102 ICINT19','SUBMIT TA1BREST BTA102']), \
             patch.object(r,'tape_state',return_value='mounted'), \
             patch.object(r,'restore_job',return_value=9130), \
             patch.object(r,'check_restored',return_value='TSO003'), \
             patch.object(r.sys,'stdout',io.StringIO()):
            self.assertEqual(r.operation(True),0)
        self.assertEqual(self.tape.read_bytes(),original)

if __name__=='__main__':unittest.main(verbosity=1)
