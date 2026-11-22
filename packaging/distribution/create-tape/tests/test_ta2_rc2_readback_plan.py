"""Offline strict TA.2 readback JCL and guard tests (no MVS operations)."""
import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock
import tempfile
import types
import hashlib
import json
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ta2-rc2-readback-plan'
loader=importlib.machinery.SourceFileLoader('ta2_rc2_rb_plan',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fake_plan():
    result=[]
    for n in range(1,22):
        d={'dsorg':'PS' if n==1 else 'PO',
           'recfm':'U' if n==12 else 'FB',
           'lrecl':0 if n==12 else 80,
           'blksize':6144 if n==12 else 800}
        members=([] if n==1 else ['INSTALL','DATASETS','RELEASE','RESTORE'] if n==2
                 else [f'M{k:07d}' for k in range(110)] if n==3
                 else [f'S{k:07d}' for k in range(15)] if n==21 else ['MISC'])
        result.append({'target_dcb':d,'members':members,
                       'producer_source_dsn':f'HERC02.BCPL.TA2STG.BT{n:04d}'})
    return {'volume':{'volser':'BC0002'},'datasets':result}

def stage_budget():
    return {'status':'VOLUME_APPROVED_SPACE_AND_WRITE_UNAPPROVED',
            'volume':'TSO002', 'primary_total':645,'secondary_total':65,
            'targets':[{'sequence':i,'primary_tracks':135 if i==20 else 30,
                        'secondary_tracks':14 if i==20 else 3,'directory_blocks':7}
                       for i in range(3,21)]}

class ReadbackPlanTests(unittest.TestCase):
    def setUp(self):
        self.original=mod.SPACE
        self.tmpfile=Path('/tmp/never-read-stage-budget')
        self.budget=stage_budget()
        self.real_read=Path.read_text
        self.data=fake_plan()
        self.rows=self.alloc()
    def alloc(self):
        original=mod.SPACE
        with patch.object(Path,'read_text',autospec=True,
                          side_effect=lambda path:json.dumps(self.budget) if path==original else self.real_read(path)):
            return mod.rows(self.data)
    def test_contract_and_21_allocations(self):
        self.assertEqual(len(self.rows),21)
        self.assertEqual(sum(len(r['members']) for r in self.rows),146)
        self.assertEqual(sum(r['space'][0] for r in self.rows),770)
        self.assertEqual(sum(r['space'][1] for r in self.rows),81)
        self.assertEqual(self.rows[11]['dcb']['recfm'],'U')
        self.assertEqual(self.rows[-1]['space'],(100,10,10))
    def test_twenty_one_exact_read_steps(self):
        s=mod.render(self.rows,'TSO002')
        self.assertEqual(s.count(' EXEC PGM=IEBGENER'),1)
        self.assertEqual(s.count(' EXEC PGM=IEBCOPY'),20)
        self.assertEqual(s.count('DISP=OLD'),21)
        self.assertEqual(s.count('DISP=(NEW,CATLG,DELETE)'),21)
        self.assertEqual(s.count('VOL=(PRIVATE,RETAIN,SER=BC0002)'),21)
        self.assertEqual(s.count('LABEL=('),21)
        self.assertEqual(s.count('DSN=HERC02.BCPL.TA2RB.BT'),21)
    def test_21st_step_and_load_library_preserved(self):
        s=mod.render(self.rows,'TSO002')
        self.assertIn('//R0021 EXEC PGM=IEBCOPY',s)
        self.assertIn('LABEL=(21,SL)',s)
        block=s.split('//R0012 EXEC')[1].split('//R0013 EXEC')[0]
        self.assertIn('DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144',block)
    def test_no_tape_output_or_stage_modifications(self):
        s=mod.render(self.rows,'TSO002')
        self.assertNotIn('OUTTAPE',s)
        self.assertNotIn('DSN=HERC02.BCPL.TA2STG.',s)
        self.assertNotIn('DISP=(NEW,KEEP',s)
    def test_cards_fit_column_71(self):
        s=mod.render(self.rows,'TSO002')
        self.assertTrue(all(len(row)<=80 for row in s.splitlines()))
        self.assertTrue(all(len(row)<=71 for row in s.splitlines()
                 if row.startswith('//') and not row.startswith('//*')))
    def test_no_implicit_dasd_choice(self):
        self.assertNotEqual(hashlib.sha256(mod.render(self.rows,'TSO002').encode()).hexdigest(),
                            hashlib.sha256(mod.render(self.rows,'TSO003').encode()).hexdigest())
    def test_reject_reserved_or_invalid_volser(self):
        for v in ('BC0002','BTA101','BTA102','BTO001','BAD-V','SEVEN77',''):
            with self.subTest(v=v),self.assertRaises(mod.Refusal):mod.render(self.rows,v)
    def test_refuse_wrong_sequence(self):
        p=self.rows.copy();p[-1]=dict(p[-1],n=20)
        with self.assertRaises(mod.Refusal):mod.render(p,'TSO002')
    def test_refuse_changed_load_dcb(self):
        p=fake_plan();p['datasets'][11]['target_dcb']={'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800}
        with self.assertRaisesRegex(mod.Refusal,'BT0012 DCB changed'):
            with patch.object(Path,'read_text',autospec=True,side_effect=lambda _:json.dumps(self.budget)):
                mod.rows(p)
    def test_refuse_budget_drift(self):
        budget=stage_budget();budget['primary_total']=0
        with self.assertRaises(mod.Refusal):
            with patch.object(Path,'read_text',autospec=True,side_effect=lambda _:json.dumps(budget)):
                mod.rows(fake_plan())
    def test_no_mvs_readback_submission_in_plan(self):
        content=SCRIPT.read_text()
        self.assertNotIn('TA2RC2RB JOB',content)
        self.assertNotIn("'hetinit'",content)
        self.assertNotIn("'tape','mount'",content)
        self.assertNotIn("'--run'",content)
    def test_readonly_mvs_preflight_checks_sources_and_target(self):
        s=SCRIPT.read_text()
        self.assertIn('core.stat_deck(config,names+sources)',s)
        self.assertIn('core.dataset_missing(report',s)
        self.assertIn('target.vtoc_observation(vrept,volume,names)',s)
        self.assertIn('producer.check_docker(folder)',s)

    def test_drive_identity_exact_validated_mount(self):
        row=("HHC02279I 0:0480 3420 /tk5/tape/"+mod.IMAGE.name)
        self.assertEqual(mod.device_identity(row)[0], 'MOUNTED_BC0002')
        self.assertEqual(mod.device_identity("HHC02279I 0480 3420 /tk5/tape/"+mod.IMAGE.name)[0],
                         'MOUNTED_BC0002')
    def test_drive_identity_empty(self):
        self.assertEqual(mod.device_identity('HHC02279I 0:0480 3420 *')[0], 'EMPTY')
    def test_drive_identity_foreign_and_prefix_collision(self):
        for path in ['/tk5/tape/other.aws', '/tk5/tape/'+mod.IMAGE.name+'.bak']:
            with self.subTest(path=path):
                self.assertEqual(mod.device_identity('HHC02279I 0:0480 3420 '+path)[0],
                                 'FOREIGN_OR_UNRECOGNIZED')
    def test_drive_identity_ambiguous_and_busy_refused(self):
        row='HHC02279I 0:0480 3420 /tk5/tape/'+mod.IMAGE.name
        self.assertEqual(mod.device_identity(row+' busy')[0], 'BUSY')
        self.assertEqual(mod.device_identity(row+'\n'+row)[0], 'UNVERIFIED')
        self.assertEqual(mod.device_identity('HHC02279I 0:0480 3390 *')[0], 'UNVERIFIED')
    def test_device_review_writes_only_new_private_evidence(self):
        base=SCRIPT.parents[4]/'workarea'
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as root:
            root=Path(root)
            work=root/'workarea';work.mkdir()
            out=work/'ta2-rc2-readback-preflight';out.mkdir()
            failed=out/'first';failed.mkdir()
            original='HHC02279I 0:0480 3420 *'
            mounted='HHC02279I 0:0480 3420 /tk5/tape/'+mod.IMAGE.name
            def sealed(_,required):
                self.assertEqual(required,{'mounted-hercules.txt','failure.json'})
                return {'mounted-hercules.txt':original.encode(),
                        'failure.json':json.dumps({'status':'READ_ONLY_REFUSED',
                        'reason':'Hercules 0480 does not hold exact BC0002 candidate'}).encode()}
            def capture(folder,name,args):
                self.assertNotIn('mount',args)
                self.assertNotIn('devinit',args)
                v=mounted if name=='drive-hercules' else 'MVS 480 3400 O'
                mod.save(folder/(name+'.txt'),v.encode())
                return v
            def seal(folder):
                import hashlib
                contents=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
                                 for p in sorted(folder.iterdir()) if p.is_file())
                mod.save(folder/'SHA256SUMS',contents.encode())
            producer=types.SimpleNamespace(sealed=sealed,check_docker=lambda _:None,
                         capture=capture,seal_evidence=seal)
            media=types.SimpleNamespace(parse_mvs=lambda _:'O')
            def loader(name,path):
                return producer if 'producer' in name else media
            with patch.multiple(mod,ROOT=root,WORK=work,OUT=out,FAILED=failed):
                with patch.object(mod,'load',side_effect=loader):
                    with patch.object(mod,'original_image',return_value=mod.SHA):
                        self.assertEqual(mod.inspect_drive(),0)
            folder=next(p for p in out.iterdir() if p!=failed)
            record=json.loads((folder/'result.json').read_text())
            self.assertEqual(record['original_drive_class'],'EMPTY')
            self.assertEqual(record['current_drive_class'],'MOUNTED_BC0002')
            self.assertFalse(record['stateful_execution_authorized'])
            self.assertTrue((folder/'SHA256SUMS').exists())
    def test_empty_drive_allows_readonly_dasd_preflight(self):
        response=('HHC02279I 0:0480 3420 * IO[3171] maxsize=0 eotmargin=128K deonirq=N')
        queried=[]
        def capture(folder,name,args):
            queried.append((name,tuple(args)))
            return response if name=='mounted-hercules' else '480 3400 O-NRD'
        producer=types.SimpleNamespace(capture=capture)
        media=types.SimpleNamespace(parse_mvs=lambda text:'O-NRD')
        self.assertEqual(mod.preflight_device(producer,media,Path('/ignored')),
                         ('EMPTY','O-NRD'))
        self.assertEqual(len(queried),2)
        self.assertEqual([name for name,_ in queried],['mounted-hercules','mounted-mvs'])
        self.assertTrue(all(('tape','mount') not in cmd and 'devinit' not in cmd
                            for _,cmd in queried))
    def test_mounted_exact_drive_allows_readonly_dasd_preflight(self):
        response='HHC02279I 0:0480 3420 /tk5/tape/'+mod.IMAGE.name
        p=types.SimpleNamespace(capture=lambda folder,name,args:
                                response if name=='mounted-hercules' else '480 3400 O')
        m=types.SimpleNamespace(parse_mvs=lambda x:'O')
        self.assertEqual(mod.preflight_device(p,m,Path('/ignored')),
                         ('MOUNTED_BC0002','O'))
    def test_preflight_rejects_foreign_and_busy_without_guest_inquiry(self):
        for line in ('HHC02279I 0:0480 3420 /tk5/tape/foreign.aws',
                     'HHC02279I 0:0480 3420 /tk5/tape/'+mod.IMAGE.name+' busy',
                     'unrecognized DEVLIST'):
            calls=[]
            def capture(folder,name,args):
                calls.append(name)
                return line
            p=types.SimpleNamespace(capture=capture)
            m=types.SimpleNamespace(parse_mvs=lambda _:'O')
            with self.subTest(line=line),self.assertRaises(mod.Refusal):
                mod.preflight_device(p,m,Path('/ignored'))
            self.assertEqual(calls,['mounted-hercules'])
    def test_preflight_rejects_inconsistent_mvs_state(self):
        for drive,state in (('*','O'),
                            ('/tk5/tape/'+mod.IMAGE.name,'O-NRD')):
            response='HHC02279I 0:0480 3420 '+drive
            p=types.SimpleNamespace(capture=lambda folder,name,args:
                                    response if name=='mounted-hercules' else state)
            m=types.SimpleNamespace(parse_mvs=lambda _ : state)
            with self.subTest(state=state,drive=drive),self.assertRaisesRegex(mod.Refusal,'conflicts'):
                mod.preflight_device(p,m,Path('/ignored'))
    def test_original_image_not_changed_in_live_preflight(self):
        text=SCRIPT.read_text()
        self.assertIn('drive_state,mvs_state=preflight_device(producer,media,folder)',text)
        self.assertIn('original_image()',text)
        self.assertIn("'hercules_drive_state':drive_state",text)
        self.assertIn("'mvs_drive_state':mvs_state",text)
        self.assertNotIn("'tape','mount'",text)

    def test_device_review_original_failure_mismatch_refuses(self):
        base=SCRIPT.parents[4]/'workarea'
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as root:
            root=Path(root);work=root/'workarea';work.mkdir()
            out=work/'ta2-rc2-readback-preflight';out.mkdir();failed=out/'failed';failed.mkdir()
            p=types.SimpleNamespace(sealed=lambda *_:{'mounted-hercules.txt':b'empty',
                       'failure.json':b'{}'})
            with patch.multiple(mod,ROOT=root,WORK=work,OUT=out,FAILED=failed):
                with patch.object(mod,'load',return_value=p):
                    with self.assertRaisesRegex(mod.Refusal,'unexpected identity'):
                        mod.inspect_drive()

if __name__=='__main__':unittest.main()
