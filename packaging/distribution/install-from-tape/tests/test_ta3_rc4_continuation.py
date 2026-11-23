"""RC4 interrupted-recipient preservation and no-replay recovery unit contracts."""
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec,spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/ta3-rc4-continuation"
loader=SourceFileLoader("ta3r4_continuation_test",str(SCRIPT))
spec=spec_from_loader(loader.name,loader)
module=module_from_spec(spec)
spec.loader.exec_module(module)


class FakeGen:
    MEMBERS=("INSTALL","DATASETS","RELEASE","RESTORE",
             "COPY","MR10","NATIVE","COMBINED")
    def load(self):
        return ({"datasets":[{"target_dcb":{"dsorg":"PO","recfm":"FB",
                                           "lrecl":80,"blksize":800}}
                             for _ in range(21)]},None)
    def materials(self,*_):
        return "",{"MR10":"//GO EXEC M10PROC\n//\n"}


class FakeRec:
    IMAGE_SHA="7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1"
    @staticmethod
    def profile_result(job,report,summary,positions):
        if job!="T3R4MR" or "STEP WAS EXECUTED" not in report:
            raise ValueError("not actually accepted")
        return len(positions)


class TestRecovery(unittest.TestCase):
    def make_incident(self,folder,*,tamper=False):
        root=folder
        relative="workarea/ta3-rc4-recipient/20261123T133542Z-36979"
        evidence=root/relative
        evidence.mkdir(parents=True)
        marker=root/"workarea/ta3-rc4-recipient/BC0004-recipient-one-shot.json"
        marker.write_text(json.dumps({
            "status":"OWNER_APPROVED_TA3_BC0004_TAPE_RESIDENT_PROFILES_NO_RETRY",
            "candidate":"BCPL-0.1.0-rc4","volser":"BC0004",
            "aws_sha256":FakeRec.IMAGE_SHA,"evidence":relative,
            "destinations":list(module.PREFIXES),
            "no_tape_write":True,"no_overwrite":True,
            "publication_authorized":False}))
        files={
            "failure.json":json.dumps({
                "status":"STATEFUL_NO_RETRY",
                "reason":module.CAUSE})+"\n",
            "absence-report.txt":"MVS LISTDS pass\n",
            "mr10-restore-summary.txt":"JOB 9402 T3R4MR\n"
                "JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n",
            "mr10-restore-report.txt":
                "IEF142I T3R4MR GO R0003 - STEP WAS EXECUTED - COND CODE 0000\n",
            "mr10-on-tape-profile.jcl":"//GO EXEC M10PROC\n//\n",
            "mr10-bt2-report.txt":"MVS BT0002 restored\n",
            "mr10-readback-report.txt":
                " COPY OUTDD=OUTPDS,INDD=INTAPE\n",
            "boot-report.txt":"CAMBRIDGE BCPL PROGRAMMING SYSTEM\n",
        }
        for name,value in files.items():
            (evidence/name).write_text(value)
        (evidence/"SHA256SUMS").write_text(
            "".join(hashlib.sha256(value.encode()).hexdigest()+
                    "  "+name+"\n" for name,value in sorted(files.items())))
        if tamper:
            (evidence/"mr10-readback-report.txt").write_text("changed\n")
        return evidence,marker

    def install(self,base):
        saved=(module.ROOT,module.WORK,module.INCIDENT,module.OLD_MARKER)
        module.ROOT=base
        module.WORK=base/"workarea"
        module.INCIDENT=base/"workarea/ta3-rc4-recipient/20261123T133542Z-36979"
        module.OLD_MARKER=base/"workarea/ta3-rc4-recipient/BC0004-recipient-one-shot.json"
        return saved

    def test_sealed_original_incident_proves_first_profile_without_replay(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/"workarea") as d:
            base=Path(d)
            self.make_incident(base)
            saved=self.install(base)
            try:
                info=module.original_receipt(FakeRec(),None,FakeGen())
                self.assertEqual(info["mr10_ief142i_steps"],10)
                self.assertEqual(info["mr10_restore_job"],9402)
            finally:
                module.ROOT,module.WORK,module.INCIDENT,module.OLD_MARKER=saved

    def test_any_original_receipt_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/"workarea") as d:
            base=Path(d)
            self.make_incident(base,tamper=True)
            saved=self.install(base)
            try:
                with self.assertRaises(module.Refusal):
                    module.original_receipt(FakeRec(),None,FakeGen())
            finally:
                module.ROOT,module.WORK,module.INCIDENT,module.OLD_MARKER=saved

    def test_unexpected_subsequent_profile_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/"workarea") as d:
            base=Path(d)
            evidence,_=self.make_incident(base)
            file=evidence/"native-bt2-summary.txt"
            file.write_text("unexpected partial work\n")
            oldseal=(evidence/"SHA256SUMS").read_text()
            newseal=(hashlib.sha256(file.read_bytes()).hexdigest()+
                     "  "+file.name+"\n")
            (evidence/"SHA256SUMS").write_text(oldseal+newseal)
            saved=self.install(base)
            try:
                with self.assertRaises(module.Refusal):
                    module.original_receipt(FakeRec(),None,FakeGen())
            finally:
                module.ROOT,module.WORK,module.INCIDENT,module.OLD_MARKER=saved

    def test_recovery_targets_only_native_and_combined(self):
        source=SCRIPT.read_text("utf-8")
        self.assertIn('for label in ("NATIVE","COMBINED"):',source)
        self.assertNotIn('for label in ("MR10","NATIVE","COMBINED"):',source)
        self.assertIn('not MARKER.exists() and not MARKER.is_symlink()',source)
        self.assertIn('rc3.exclusive(MARKER,',source)
        self.assertIn('rec.profile_result(name,report,summary,tuple(range(3,13)))',source)

    def test_first_installation_must_have_actual_mvs_ief142i_steps(self):
        from importlib.machinery import SourceFileLoader
        from importlib.util import module_from_spec,spec_from_loader
        p=SCRIPT.parents[1]/"scripts/ta3-rc4-recipient"
        l=SourceFileLoader("rc4_validator_fixture",str(p))
        spec=spec_from_loader(l.name,l)
        rec=module_from_spec(spec)
        spec.loader.exec_module(rec)
        expected=tuple(range(3,13))
        summary="JOB 9402 T3R4MR\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n"
        report="".join(
            f"IEF142I T3R4MR GO R{n:04d} - STEP WAS EXECUTED - COND CODE 0000\n"
            for n in expected)
        self.assertEqual(rec.profile_result("T3R4MR",report,summary,expected),10)
        with self.assertRaises(rec.Refusal):
            rec.profile_result("T3R4MR",report.replace("R0008","R0009"),
                               summary,expected)


if __name__=="__main__":
    unittest.main()
