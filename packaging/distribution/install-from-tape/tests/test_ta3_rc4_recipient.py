"""TA.3 RC4 tape-resident three-profile recipient: offline refusal/contract tests."""
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec,spec_from_loader
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/ta3-rc4-recipient"
loader=SourceFileLoader("ta3r4_recipient_tests",str(SCRIPT))
spec=spec_from_loader(loader.name,loader)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRecipient(unittest.TestCase):
    def materials(self):
        ref,rem,gen,rc3,load=mod.tools()
        m,sizes=gen.load()
        bt,members=gen.materials(m,sizes)
        return ref,rem,gen,m,members

    def test_three_isolated_mvs_profile_selections(self):
        ref,rem,gen,m,members=self.materials()
        selected=mod.selection(m,gen)
        self.assertEqual(
            [(x[0],len(x[3]),x[4]) for x in selected.values()],
            [("HERC02.BCPL.R4MR",11,94),
             ("HERC02.BCPL.R4NT",11,71),
             ("HERC02.BCPL.R4CB",20,150)])
        self.assertEqual(sum(x[4] for x in selected.values()),315)
        self.assertEqual(sum(len(x[3]) for x in selected.values()),42)
        self.assertEqual(len(members),8)

    def test_profile_deck_from_tape_sysout_exact_copy(self):
        source=self.materials()[-1]["MR10"]
        report=("JES2 SPOOL START\n"+
                "".join(" "+line+"\n" for line in source.splitlines())+
                "IEF142I T3R4PR P0001 - STEP WAS EXECUTED\n")
        self.assertEqual(mod.extract_profile(report,source),source)

    def test_profile_missing_or_reordered_record_refused(self):
        source=self.materials()[-1]["NATIVE"]
        lines=source.splitlines()
        report="\n".join(lines[:10]+lines[11:])
        with self.assertRaises(mod.Refusal):
            mod.extract_profile(report,source)

    def test_profile_tampered_card_refused(self):
        source=self.materials()[-1]["COMBINED"]
        report=source.replace("VOL=(PRIVATE,RETAIN,SER=BC0004)",
                              "VOL=(PRIVATE,RETAIN,SER=BC0003)",1)
        with self.assertRaises(mod.Refusal):
            mod.extract_profile(report,source)

    def test_real_mvs_readback_targets_correct_installed_pds(self):
        for name,site,job in (("MR10","R4MR","T3R4MR"),
                              ("NATIVE","R4NT","T3R4NT"),
                              ("COMBINED","R4CB","T3R4CB")):
            body=mod.readback_deck("HERC02.BCPL."+site,name)
            self.assertIn("HERC02.BCPL."+site+".DIST.INST("+name+")",body)
            self.assertIn("HERC02.BCPL."+site+".DIST.INST(COPY)",body)
            self.assertEqual(body.count("EXEC PGM=IEBGENER"),2)
            self.assertNotIn("DISP=(NEW,CATLG,DELETE)",body)
            self.assertTrue(body.endswith("//\n"))

    def test_actual_ief142i_procedure_orderings(self):
        summary=("JOB 9399 T3R4MR\nJOB RESULT: SUCCESS\n"
                 "HIGHEST RC: 0000\nR0003 IEBCOPY RC=0000\n"
                 "R0004 IEBCOPY RC=0000\n")
        for ordering in ("GO R0003","R0003 GO","GO.R0003"):
            second=("GO R0004" if ordering=="GO R0003" else
                    "GO.R0004" if ordering=="GO.R0003" else "R0004 GO")
            report=(f"IEF142I T3R4MR {ordering} - "
                    "STEP WAS EXECUTED - COND CODE 0000\n"+
                    f"IEF142I T3R4MR {second} - "
                    "STEP WAS EXECUTED - COND CODE 0000\n")
            self.assertEqual(
                mod.profile_result("T3R4MR",report,summary,(3,4)),2)

    def test_actual_missing_ief142i_refused(self):
        summary="JOB RESULT: SUCCESS\nHIGHEST RC: 0000\nR0003 IEBCOPY RC=0000\n"
        report="IEF142I T3R4MR GO R0003 - STEP WAS EXECUTED - COND CODE 0000\n"
        with self.assertRaises(mod.Refusal):
            mod.profile_result("T3R4MR",report,summary,(3,4))

    def test_bootstrap_and_installer_retarget_only_new_tape(self):
        ref,_,_,m,_=self.materials()
        body=mod.boot_and_installer(ref,"HERC02.BCPL.R4MR")
        self.assertEqual(set(body),{"TA3BOOT","TA3BT2"})
        self.assertTrue(all("BC0003" not in b for b in body.values()))
        self.assertTrue(all("BC0004" in b for b in body.values()))
        self.assertIn(
            "DSN=HERC02.BCPL.R4MR.DIST.INST,",
            body["TA3BT2"])

    def test_accepted_production_receipt_and_tamper_refusal(self):
        oldroot,oldprod,oldmarker=mod.ROOT,mod.PROD,mod.PROD_MARKER
        work=SCRIPT.parents[4]/"workarea"
        work.mkdir(exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(dir=work) as tmp:
                mod.ROOT=Path(tmp)
                mod.PROD=mod.ROOT/"workarea/ta3-rc4-production"
                mod.PROD_MARKER=mod.PROD/"BC0004-one-shot-production.json"
                rel="workarea/ta3-rc4-production/20261123T130731Z-36363"
                evidence=mod.ROOT/rel
                evidence.mkdir(parents=True)
                mod.PROD_MARKER.write_text(json.dumps({
                    "status":"OWNER_APPROVED_TA3_RC4_STAGE_AND_WRITE_NO_RETRY",
                    "candidate":"BCPL-0.1.0-rc4","volser":mod.VOL,
                    "original_bc0003_sha256":mod.ORIGINAL_SHA,
                    "overwrite_existing":False,
                    "publication_authorized":False,
                    "evidence":rel}))
                result={
                    "status":"TA3_RC4_MVS_TWO_DATASET_STAGE_AND_21_DATASET_SL_AWS_WRITE_PASS",
                    "volser":mod.VOL,"sha256":mod.IMAGE_SHA,
                    "original_bc0003_sha256":mod.ORIGINAL_SHA,
                    "mvs_jobs":{
                        "preflight":9393,"stage":9394,
                        "staged_catalog":9395,
                        "installer_directory":9396,
                        "tape_write":9397},
                    "installer_members":8,
                    "logical_datasets":21,"aws_physical_files":64}
                files={
                    "result.json":json.dumps(result)+"\n",
                    "stage-report.txt":"MVS stage PASS\n",
                    "write-report.txt":"MVS write PASS\n",
                    "aws-labels.txt":"VOL1 BC0004\n",
                    "aws-files.txt":"64 files\n",
                    "members-report.txt":"8 members\n"}
                for name,blob in files.items():
                    (evidence/name).write_text(blob)
                seal="".join(hashlib.sha256(blob.encode()).hexdigest()+
                             "  "+name+"\n" for name,blob in sorted(files.items()))
                (evidence/"SHA256SUMS").write_text(seal)
                self.assertEqual(mod.production_receipt(),rel)
                (evidence/"members-report.txt").write_text("tampered\n")
                with self.assertRaises(mod.Refusal):
                    mod.production_receipt()
        finally:
            mod.ROOT,mod.PROD,mod.PROD_MARKER=oldroot,oldprod,oldmarker


if __name__=="__main__":
    unittest.main()
