"""Offline RC4 one-shot producer safety tests; no MVS, Docker or tape IO."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/ta3-rc4-production"
loader=SourceFileLoader("ta3r4production_test",str(SCRIPT))
spec=spec_from_loader(loader.name,loader)
module=module_from_spec(spec)
spec.loader.exec_module(module)


class TestProduction(unittest.TestCase):
    def test_complete_mvs_deck_and_source_mapping(self):
        gen,rc3,_=module.components()
        m,members,stage,writer=module.cards_and_identity(gen,rc3)
        source=module.source_rows(m)
        self.assertEqual(len(source),19)
        self.assertEqual(source[0][0],"HERC02.BCPL.TA2R3S.BT0003")
        self.assertEqual(source[-1][0],"HERC02.BCPL.TA2R3S.BT0021")
        self.assertEqual(len(members),8)
        self.assertEqual(len(module.MVS_STAGES),9)
        self.assertEqual(len(module.MVS_WRITES),21)
        self.assertEqual(stage.count("DISP=(NEW,CATLG,DELETE)"),2)
        self.assertEqual(writer.count(" SELECT MEMBER="),150)
        self.assertNotIn("SER=BC0003",writer)

    def test_embedded_installer_jcl_is_not_executed_staging_jcl(self):
        """Regression for the RC4 preflight halt before any MVS operation."""
        gen,rc3,_=module.components()
        m,members,stage,writer=module.cards_and_identity(gen,rc3)
        outer=rc3.jcl_control_cards(stage.splitlines())
        raw_alloc=stage.count("DISP=(NEW,CATLG,DELETE)")
        active_alloc=sum("DISP=(NEW,CATLG,DELETE)" in x for x in outer)
        self.assertEqual(raw_alloc,41)  # 2 actual, 39 embedded profiles
        self.assertEqual(active_alloc,2)
        self.assertEqual(len(members),8)
        self.assertEqual(sum(" EXEC PGM=IEBCOPY" in x for x in outer),0)
        self.assertEqual(stage.count(" EXEC PGM=IEBCOPY"),39)
        self.assertEqual(sum(" EXEC PGM=IEBGENER" in x for x in outer),9)
        self.assertEqual(sum(" EXEC PGM=IEFBR14" in x for x in outer),1)
        self.assertEqual(sum(x=="//SYSUT1 DD DATA,DLM=Z9" for x in outer),9)
        self.assertEqual(writer.count(" SELECT MEMBER="),150)

    def test_active_stage_validator_refuses_extra_real_allocation(self):
        gen,rc3,_=module.components()
        original=gen.plan
        def tampered():
            bt,members,stage,write=original()
            stage=stage.replace(
                "//OUTPDS DD DSN=HERC02.BCPL.TA3R4S.BT0002,",
                "//EXTRA DD DISP=(NEW,CATLG,DELETE)\n"
                "//OUTPDS DD DSN=HERC02.BCPL.TA3R4S.BT0002,")
            return bt,members,stage,write
        try:
            gen.plan=tampered
            with self.assertRaises(module.Refusal):
                module.cards_and_identity(gen,rc3)
        finally:
            gen.plan=original

    def test_preflight_drive_empty_only_when_mvs_agrees(self):
        class RC:
            @staticmethod
            def run_command(folder,key,command):
                return ("HHC02279I 0480 3420 * idle\n"
                        if command[1:3]==["tape","status"]
                        else "0480 3400 O-NRD\n")
        class Media:
            @staticmethod
            def parse_mvs(result):
                return "O-NRD" if "O-NRD" in result else "O"
        self.assertEqual(module.drive_prior(RC(),Media(),None,"a"),"EMPTY")
        self.assertTrue(module.drive_empty(RC(),Media(),None,"b"))

    def test_existing_immutable_bc0003_allowed_only_when_verified(self):
        old=module.original_guard
        try:
            module.original_guard=lambda:None
            class Media:
                @staticmethod
                def parse_mvs(result):return "O"
            class RC:
                @staticmethod
                def run_command(folder,key,command):
                    return ("HHC02279I 0480 3420 "+module.ORIGINAL.name+" idle\n"
                            if command[1:3]==["tape","status"] else "0480 3400 O\n")
            self.assertEqual(module.drive_prior(RC(),Media(),None,"c"),"RC3")
        finally:
            module.original_guard=old

    def test_foreign_tape_is_rejected(self):
        class RC:
            @staticmethod
            def run_command(folder,key,command):
                return ("HHC02279I 0480 3420 other-volume.aws\n"
                        if command[1:3]==["tape","status"] else "0480 3400 O\n")
        class Media:
            @staticmethod
            def parse_mvs(result):return "O"
        with self.assertRaises(module.Refusal):
            module.drive_prior(RC(),Media(),None,"c")

    def test_media_scan_never_permits_colliding_volser(self):
        prev_tapes,prev_img=module.TAPES,module.IMAGE
        try:
            with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/"workarea") as d:
                base=Path(d)
                (base/"another.aws").write_bytes(b"synthetic")
                module.TAPES=base
                module.IMAGE=base/"bcpl-0.1.0-rc4-BC0004.aws"
                class RC:
                    @staticmethod
                    def run_command(folder,key,command):
                        return "Volume Serial : 'BC0004'\n"
                class Prod:
                    @staticmethod
                    def volser_from_hetmap(output):return "BC0004"
                with self.assertRaises(module.Refusal):
                    module.media_scan(RC(),Prod(),None)
        finally:
            module.TAPES,module.IMAGE=prev_tapes,prev_img

    def test_full_stage_jcl_requires_iefbr14(self):
        """Stage must check the real allocation step, not just IEBGENER steps."""
        class RC:
            @staticmethod
            def cards(lines):return "\n".join(lines)+"\n"
            @staticmethod
            def artifact(folder,name,blob):
                (folder/name).write_text(blob,encoding="utf-8")
        expected=[("B0001","IEBGENER"),("A0002","IEFBR14"),
                  *module.MVS_STAGES[1:]]
        summary=("JOB 9393 TA3R4STG\nJOB RESULT: SUCCESS\n"
                 "HIGHEST RC: 0000\n"+
                 "".join(f"{step} {pgm} RC=0000\n" for step,pgm in expected))
        report="".join(
            f"IEF142I TA3R4STG {step} - STEP WAS EXECUTED - COND CODE 0000\n"
            for step,_ in expected)
        class Core:
            @staticmethod
            def authenticated_job_card(cfg,name,desc,redact):
                return ["//TA3R4STG JOB (X)"]
            @staticmethod
            def submit_and_wait(cfg,deck,max_rc,cursor_file):
                return 9393,summary
            @staticmethod
            def job_report(job,cursor_file):return report
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/"workarea") as d:
            folder=Path(d)
            self.assertEqual(module.stage_job(
                RC(),Core(),{},folder,"//B0001 EXEC PGM=IEBGENER\n//\n"),9393)
            Core.submit_and_wait=staticmethod(lambda cfg,deck,max_rc,cursor_file:
                (9393,summary.replace("A0002 IEFBR14 RC=0000\n","")))
            with self.assertRaises(module.Refusal):
                module.stage_job(
                    RC(),Core(),{},folder,"//B0001 EXEC PGM=IEBGENER\n//\n")

    def test_source_prefix_and_marker_never_overlap_accepted_stage(self):
        self.assertNotEqual(module.STAGE,module.SOURCE)
        self.assertEqual(module.STAGE,"HERC02.BCPL.TA3R4S.")
        self.assertEqual(module.VOL,"BC0004")
        self.assertIn("/workarea/",str(module.MARKER))
        self.assertTrue(module.IMAGE.name.endswith("BC0004.aws"))
        self.assertTrue(module.ORIGINAL.name.endswith("BC0003.aws"))


if __name__=="__main__":
    unittest.main()
