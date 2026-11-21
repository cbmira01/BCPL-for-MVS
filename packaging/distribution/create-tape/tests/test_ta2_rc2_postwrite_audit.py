"""Synthetic read-only BC0002 postwrite JES/HETMAP/immutable image checks."""
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/ta2-rc2-postwrite-audit'
loader=importlib.machinery.SourceFileLoader('audit_test',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def good_jes(job=9433):
    summary=f'JOB {job} TA2RC2WR\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
    summary+=''.join(f'T{i:04d} {"IEBGENER" if i==1 else "IEBCOPY"} RC=0000\n' for i in range(1,22))
    report=''.join(f'IEF142I TA2RC2WR T{i:04d} - STEP WAS EXECUTED - COND CODE 0000\n' for i in range(1,22))
    return summary,report

def maptext(number_start=1):
    blocks=[]
    for i in range(21):blocks.extend([3 if i==0 else 2, i+1,2])
    blocks.append(0)
    return ''.join(f'File # : {i}\nBlocks : {b}\n' for i,b in enumerate(blocks,number_start))

def labels():
    return "Label               : 'VOL1'\nVolume Serial       : 'BC0002'\n"+''.join(
        f"Label               : '{label}'\n" for i in range(21) for label in ('HDR1','HDR2','EOF1','EOF2'))

class TestAudit(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        self.root=Path(td.name);self.work=self.root/'workarea';self.work.mkdir()
    def test_good_jes(self):
        self.assertEqual(mod.validate_jes(*good_jes()),9433)
    def test_jes_step_missing(self):
        s,r=good_jes();s=s.replace('T0014 IEBCOPY RC=0000\n','')
        with self.assertRaises(mod.Refusal):mod.validate_jes(s,r)
    def test_jes_abend(self):
        s,r=good_jes()
        with self.assertRaises(mod.Refusal):mod.validate_jes(s,r+'IEF450I ABEND S0C4\n')
    def test_jes_wrong_step_rc(self):
        s,r=good_jes();s=s.replace('T0021 IEBCOPY RC=0000','T0021 IEBCOPY RC=0004')
        with self.assertRaises(mod.Refusal):mod.validate_jes(s,r)
    def test_map_64_correct(self):
        d=mod.map_diagnostic(maptext());self.assertEqual(d['file_entries'],64)
        self.assertTrue(d['strict_21_dataset_layout_pass'])
        self.assertTrue(d['sequential_from_one'])
    def test_map_64_zero_based_diagnostic(self):
        d=mod.map_diagnostic(maptext(0));self.assertEqual(d['file_entries'],64)
        self.assertTrue(d['sequential_from_zero']);self.assertFalse(d['strict_21_dataset_layout_pass'])
        self.assertEqual(len(d['first_number_or_count_discrepancies']),6)
    def test_map_64_missing_block_and_duplicate(self):
        text=maptext().replace('File # : 17\nBlocks : 6', 'File # : 17\nBlocks : 6\nBlocks : 6')
        d=mod.map_diagnostic(text);self.assertGreater(d['missing_or_repeated_block_counts'],0)
        self.assertFalse(d['strict_21_dataset_layout_pass'])
    def test_map_63_does_not_claim_success(self):
        d=mod.map_diagnostic(maptext().replace('File # : 64\nBlocks : 0\n',''))
        self.assertEqual(d['file_entries'],63);self.assertFalse(d['strict_21_dataset_layout_pass'])
    def test_sealed_original_receipt(self):
        evidence=self.work/'sealed';evidence.mkdir()
        s,r=good_jes()
        names={'write-summary.txt':s,'write-report.txt':r,'files-final.txt':maptext(),
               'labels-final.txt':labels(), 'failure.json':json.dumps({'status':'HALTED_NO_RETRY',
               'reason':'HETMAP file number/block count missing, repeated or out of order'})}
        for n,v in names.items():(evidence/n).write_text(v)
        rows=''.join(hashlib.sha256((evidence/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in sorted(names))
        (evidence/'SHA256SUMS').write_text(rows)
        with patch.multiple(mod,WORK=self.work,ORIGINAL=evidence):
            self.assertEqual(mod.original_receipt()['write-summary.txt'].decode(),s)
            (evidence/'files-final.txt').write_text('TAMPER')
            with self.assertRaisesRegex(mod.Refusal,'hash mismatch'):mod.original_receipt()
    def test_marker_and_image(self):
        tape=self.root/'mvs-state/tape';tape.mkdir(parents=True)
        image=tape/mod.IMAGE;image.write_bytes(b'aws tape bytes')
        ops=self.work/'ops';ops.mkdir();origin=ops/'evidence';origin.mkdir()
        marker=ops/'marker.json'
        data={'state':'STATEFUL_SUBMISSION_INTENT_NO_RETRY','candidate':'BCPL-0.1.0-rc2',
              'volser':'BC0002','image':mod.IMAGE,'do_not_retry':True,
              'evidence':'workarea/ops/evidence'}
        marker.write_text(json.dumps(data))
        with patch.multiple(mod,ROOT=self.root,WORK=self.work,TAPES=tape,TAPE=image,
                            ORIGINAL=origin,MARKER=marker):
            dig,sz=mod.marker_and_image()
            self.assertEqual(dig,hashlib.sha256(b'aws tape bytes').hexdigest())
            self.assertEqual(sz,len(b'aws tape bytes'))
            data['do_not_retry']=False;marker.write_text(json.dumps(data))
            with self.assertRaisesRegex(mod.Refusal,'marker differs'):mod.marker_and_image()
    def test_run_does_not_mutate_aws(self):
        s,r=good_jes()
        bytes_=b'unchanged image'
        original={'write-summary.txt':s.encode(),'write-report.txt':r.encode(),
                  'files-final.txt':maptext().encode(),'labels-final.txt':labels().encode()}
        def capture(folder,flag,name):
            sample={'-f':maptext(),'-l':labels(),'-a':maptext()}[flag]
            mod.save(folder,name+'.txt',sample.encode());return sample
        with patch.multiple(mod,ROOT=self.root,WORK=self.work,OUT=self.work/'review',
                            ORIGINAL=self.work/'original'):
            with patch.object(mod,'original_receipt',return_value=original):
                with patch.object(mod,'marker_and_image',return_value=(hashlib.sha256(bytes_).hexdigest(),len(bytes_))):
                    with patch.object(mod,'capture_map',side_effect=capture) as call:
                        self.assertEqual(mod.run(),0)
        self.assertEqual(call.call_count,3)
        folder=next((self.work/'review').iterdir())
        receipt=json.loads((folder/'result.json').read_text())
        self.assertEqual(receipt['mvs_steps'],21)
        self.assertTrue(receipt['saved_hetmap']['strict_21_dataset_layout_pass'])
        self.assertFalse(receipt['publication_authorized'])
        self.assertTrue((folder/'SHA256SUMS').exists())
    def test_saved_and_live_map_drift_refused(self):
        s,r=good_jes()
        orig={'write-summary.txt':s.encode(),'write-report.txt':r.encode(),
              'files-final.txt':maptext(0).encode(),'labels-final.txt':labels().encode()}
        def capture(folder,flag,name):
            sample=maptext() if flag in ('-f','-a') else labels()
            mod.save(folder,name+'.txt',sample.encode());return sample
        with patch.multiple(mod,ROOT=self.root,WORK=self.work,OUT=self.work/'review',
                            ORIGINAL=self.work/'original'):
            with patch.object(mod,'original_receipt',return_value=orig):
                with patch.object(mod,'marker_and_image',return_value=('a'*64,25)):
                    with patch.object(mod,'capture_map',side_effect=capture):
                        self.assertEqual(mod.run(),2)
        folder=next((self.work/'review').iterdir())
        self.assertTrue((folder/'SHA256SUMS').exists())
        self.assertEqual(json.loads((folder/'failure.json').read_text())['status'],'READ_ONLY_REVIEW_REFUSED')

if __name__=='__main__':unittest.main()
