"""Synthetic MVS GET tests for TA.2 historical-source readback. No JES used."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "packaging/distribution/compiler-source/rc2-cambsource-record-readback.py"
spec = importlib.util.spec_from_file_location("ta2_rc2_readback", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
MEMBERS = ["BCPL", "BLIB", "CG", "CGHDR", "EDITMAIN", "IOS", "LIBHDR", "PM",
           "SYN", "SYNHDR", "TRN", "TRNHDR", "MAKEOBJ", "MAKELIB", "PROGRAM"]
MAPPING = {name: "richards-bcpltape/" + name.lower() for name in MEMBERS}
MANIFEST = {"datasets": [None] * 20 + [{"members": MEMBERS}]}
DSPAL = {"datasets": {"CAMB_SOURCE": {"members": MAPPING}}}
POP_RECEIPT = ("JOB 9325: batch 1/2 CAMB_SOURCE (8 members), 1.0s\n"
               "JOB 9326: batch 2/2 CAMB_SOURCE (7 members), 1.0s\n"
               "populate completed: 15 ready member(s) written\n")
AFTER = "HERC02.BCPL.CAMBRIDG.SOURCE:\n" + "".join(
    "    " + name + "\n" for name in MEMBERS)


class RecordReadbackTests(unittest.TestCase):
    def test_normalized_fixed_records(self):
        text, count, trimmed = mod.normalize_expected(b"ABC  \n\nX \n")
        self.assertEqual((text, count, trimmed), ("ABC\n\nX\n", 3, 2))

    def test_invalid_source_records(self):
        for data in (b"", b"ABC", b"A\r\n", b"A\tB\n",
                     b"A" * 81 + b"\n", b"\xff\n", b"X\x00\n"):
            with self.subTest(raw=data), self.assertRaises(mod.Refusal):
                mod.normalize_expected(data)

    def test_job_id_strict(self):
        path = Path("workarea/ta2-rc2-cambsource-record-readback/BCPL.txt")
        value = f"get completed as JOB 9417: CAMB_SOURCE(BCPL) -> {path}\n"
        self.assertEqual(mod.get_job_id(value, "BCPL", path), 9417)
        for bad in (value.replace("9417", "?"),
                    value.replace("BCPL)", "CGA)"),
                    value + "extraneous\n"):
            with self.subTest(text=bad), self.assertRaises(mod.Refusal):
                mod.get_job_id(bad, "BCPL", path)

    def test_textual_differences_rejected(self):
        mod.verify_text("A\n\nB\n", "A\n\nB\n")
        for text in ("A\nB\n", "A\n\nB \n", "A\n\nC\n"):
            with self.assertRaises(mod.Refusal):
                mod.verify_text("A\n\nB\n", text)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ta2-rc2-readback-", dir=ROOT / "workarea")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "workarea"
        self.work.mkdir()
        self.pop = self.work / "ta2-rc2-cambsource-population-once"
        self.pop.mkdir()
        (self.pop / "populate.stdout.txt").write_text(POP_RECEIPT)
        (self.pop / "after-members.txt").write_text(AFTER)
        (self.pop / "directory-verified.txt").write_text("OK\n")
        self.readback = self.work / "ta2-rc2-cambsource-record-readback"
        self.sources = {p: (m + "  \n\nEND\n").encode("ascii")
                        for m, p in MAPPING.items()}
        self.readiness = SimpleNamespace(
            FROZEN="78baec9a8546e4ab09caee779aa2b675379272f3",
            source_manifest=lambda: (MANIFEST, DSPAL),
            verify_sources=lambda *args: ([(m, 3) for m in MEMBERS], [MEMBERS[:8], MEMBERS[8:]]),
            check_frozen_source=lambda path: self.sources[path],
            inspect_listing=lambda listing, members: ("complete" if listing == AFTER else "partial"),
        )
        self.population = SimpleNamespace(check_population_receipt=lambda x: [9325, 9326]
                                          if x == POP_RECEIPT else [0, 0])

    def invoke(self, *, modified_member=None, fail_member=None):
        called = []
        def fake_get(member, rel):
            called.append(member)
            target = self.root / rel
            if fail_member == member:
                return SimpleNamespace(returncode=2, stdout="", stderr="MVS failed\n")
            raw = self.sources[MAPPING[member]]
            text, _, _ = mod.normalize_expected(raw)
            if member == modified_member:
                text = text.replace("END", "BROKEN")
            target.write_text(text, encoding="utf-8")
            return SimpleNamespace(returncode=0, stdout="", stderr=(
                f"get completed as JOB {9400 + len(called)}: CAMB_SOURCE({member}) -> {rel}\n"))
        def module(name, path):
            return self.readiness if "readiness" in name else self.population
        with patch.object(mod, "ROOT", self.root), patch.object(mod, "WORK", self.work), \
             patch.object(mod, "POPULATION", self.pop), patch.object(mod, "READBACK", self.readback), \
             patch.object(mod, "load", side_effect=module), \
             patch.object(mod, "mvs_get", side_effect=fake_get):
            return mod.run(), called

    def test_exact_15_full_run(self):
        status, called = self.invoke()
        self.assertEqual((status, called), (0, MEMBERS))
        result = json.loads((self.readback / "receipt.json").read_text())
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["population_jobs"], [9325, 9326])
        self.assertEqual(result["total_records"], 45)
        self.assertEqual(len(result["members"]), 15)
        self.assertEqual({r["job"] for r in result["members"]}, set(range(9401, 9416)))
        self.assertEqual(result["raw_ebcdic_byte_fidelity"], "not-asserted")
        self.assertTrue(all(r["match"] for r in result["members"]))

    def test_bad_content_stops_and_keeps_evidence(self):
        with self.assertRaisesRegex(mod.Refusal, "differs"):
            self.invoke(modified_member="CG")
        saved = json.loads((self.readback / "receipt.json").read_text())
        self.assertEqual(saved["status"], "incomplete")
        self.assertEqual([m["member"] for m in saved["members"]], MEMBERS[:3])
        self.assertFalse(saved["members"][-1]["match"])

    def test_mvs_failure_preserves_prior_members(self):
        with self.assertRaisesRegex(mod.Refusal, "MVS readback failed"):
            self.invoke(fail_member="BLIB")
        saved = json.loads((self.readback / "receipt.json").read_text())
        self.assertEqual(len(saved["members"]), 1)
        self.assertTrue((self.readback / "BLIB.stderr.txt").exists())

    def test_not_retryable_in_same_evidence_dir(self):
        self.assertEqual(self.invoke()[0], 0)
        with self.assertRaisesRegex(mod.Refusal, "already exists"):
            self.invoke()

    def test_population_job_mismatch_refused(self):
        (self.pop / "populate.stdout.txt").write_text("OTHER\n")
        with patch.object(mod, "POPULATION", self.pop), patch.object(mod, "WORK", self.work):
            with self.assertRaisesRegex(mod.Refusal, "differs"):
                mod.verify_population(self.population, self.readiness, MANIFEST)

    def test_evidence_symlink_refused(self):
        f = self.pop / "after-members.txt"
        f.unlink()
        f.symlink_to(self.pop / "populate.stdout.txt")
        with patch.object(mod, "POPULATION", self.pop), patch.object(mod, "WORK", self.work):
            with self.assertRaisesRegex(mod.Refusal, "unsafe"):
                mod.verify_population(self.population, self.readiness, MANIFEST)


if __name__ == "__main__":
    unittest.main()
