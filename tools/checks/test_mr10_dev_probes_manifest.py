"""Host-only MR10 development-probe manifest tests; no JES or MVS commands."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).with_name("check-mr10-dev-probes-manifest.py")
SPEC = importlib.util.spec_from_file_location("mr10_dev_probe_validator", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import MR10 development-probe validator")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DevelopmentProbeManifestTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mr10-probe-contract-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root / "mr10-kit-compiler/tests/dev-probes-manifest.tsv"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text(MOD.MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
        with self.manifest.open(encoding="utf-8", newline="") as handle:
            self.rows = list(csv.DictReader(handle, delimiter="\t"))
        self.make_file("mr10-kit-compiler/asm/CURRENT", "icintv19.asm\n")
        for version in ("12", "13", "14", "19"):
            self.make_file(f"mr10-kit-compiler/asm/icintv{version}.asm")
        for row in self.rows:
            self.make_file(row["source"])
            for module in row["modules"].split(";") if row["modules"] else []:
                self.make_file(module)
            for binding in row["dd_bindings"].split(";") if row["dd_bindings"] else []:
                self.make_file(binding.split("=", 1)[1])
            if row["sysin"]:
                self.make_file(row["sysin"])
            if row["oracle"].startswith("file:"):
                golden = ("VALUE FROM EXTRA = 12345\n" if row["case_id"] == "05-named-dd"
                          else "fixture\n")
                self.make_file(row["oracle"][5:], golden)

    def make_file(self, name, content="fixture\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="ascii")

    def save(self):
        with self.manifest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=MOD.FIELDS, delimiter="\t",
                                    lineterminator="\n")
            writer.writeheader()
            writer.writerows(self.rows)

    def check_failure(self, fragment):
        with self.assertRaises(MOD.ContractError) as caught:
            MOD.validate(self.root, self.manifest)
        self.assertIn(fragment, str(caught.exception))

    def test_repository_manifest_is_valid_offline(self):
        self.assertEqual(len(MOD.validate()), 17)

    def test_fixture_contract_is_valid(self):
        self.assertEqual(len(MOD.validate(self.root, self.manifest)), 17)
        self.assertEqual(len(set(row["case_id"].split("/")[0] for row in self.rows)), 11)
        self.assertEqual(sum(row["verification"] == "ACCEPTED" for row in self.rows), 1)
        self.assertEqual(sum(row["verification"] == "UNVERIFIED" for row in self.rows), 16)

    def test_identity_not_renumbered(self):
        self.rows[0]["case_id"] = "01-new-test"
        self.save()
        self.check_failure("probe identities/order")

    def test_missing_case_fails(self):
        self.rows.pop()
        self.save()
        self.check_failure("expected 17 probe contracts")

    def test_changed_historical_interpreter_fails(self):
        self.rows[1]["interpreter"] = "current"
        self.save()
        self.check_failure("historical interpreter")

    def test_missing_historical_assembler_fails(self):
        (self.root / "mr10-kit-compiler/asm/icintv13.asm").unlink()
        self.check_failure("historical interpreter")

    def test_missing_required_source_fails(self):
        (self.root / self.rows[0]["source"]).unlink()
        self.check_failure("missing or outside repository")

    def test_path_escape_fails(self):
        with self.assertRaises(MOD.ContractError) as caught:
            MOD.checked_file(self.root, "../elsewhere.bcpl", "test")
        self.assertIn("unsafe repository path", str(caught.exception))

    def test_duplicate_module_fails(self):
        name = self.rows[5]["modules"]
        self.rows[5]["modules"] = name + ";" + name
        self.save()
        self.check_failure("required modules changed")

    def test_duplicate_ddname_fails(self):
        self.rows[6]["dd_bindings"] += ";EXTRA=" + self.rows[6]["source"]
        self.save()
        self.check_failure("required DD bindings changed")

    def test_missing_dd_fixture_fails(self):
        path = self.rows[6]["dd_bindings"].split("=", 1)[1]
        (self.root / path).unlink()
        self.check_failure("missing or outside repository")

    def test_expected_negative_code_must_be_pinned(self):
        self.rows[2]["expected_code"] = "0"
        self.save()
        self.check_failure("unexpected interpreted completion code")

    def test_oracle_cannot_be_empty(self):
        self.rows[8]["oracle"] = ""
        self.save()
        self.check_failure("output oracle")

    def test_unsupported_golden_cannot_be_invented(self):
        self.rows[8]["oracle"] = "file:mr10-kit-compiler/tests/07-many-streams/dd01.txt"
        self.save()
        self.check_failure("new golden output requires separate evidence review")

    def test_acceptance_claim_not_allowed_without_evidence(self):
        self.rows[1]["verification"] = "ACCEPTED"
        self.save()
        self.check_failure("separately reviewed evidence")

    def test_removing_required_dd_fails(self):
        self.rows[8]["dd_bindings"] = ""
        self.save()
        self.check_failure("required DD bindings changed")

    def test_removing_required_module_fails(self):
        self.rows[15]["modules"] = ""
        self.save()
        self.check_failure("required modules changed")

    def test_removing_required_sysin_fails(self):
        self.rows[0]["sysin"] = ""
        self.save()
        self.check_failure("required SYSIN changed")

    def test_bad_artifacts_fails(self):
        self.rows[0]["artifacts"] = "ocode,intcode"
        self.save()
        self.check_failure("artifact requirement changed")

    def test_header_changed_fails(self):
        content = self.manifest.read_text()
        self.manifest.write_text(content.replace("case_id\tengine", "case\tengine", 1))
        self.check_failure("manifest columns")

    def test_malformed_tsv_extra_column_fails(self):
        with self.manifest.open("a", encoding="utf-8") as handle:
            handle.write("extra\t" * 20 + "\n")
        self.check_failure("expected 17 probe contracts")

    def test_05_accepted_and_pinned(self):
        record = next(row for row in self.rows if row["case_id"] == "05-named-dd")
        self.assertEqual(record["verification"], "ACCEPTED")
        self.assertEqual(record["oracle"],
                         "file:mr10-kit-compiler/tests/05-named-dd/05-named-dd.expected")

    def test_05_golden_mutation_rejected(self):
        path = self.root / "mr10-kit-compiler/tests/05-named-dd/05-named-dd.expected"
        path.write_text("VALUE FROM EXTRA = 12346\n", encoding="utf-8")
        self.check_failure("accepted golden output differs")

    def test_05_cannot_be_demoted_silently(self):
        row = next(row for row in self.rows if row["case_id"] == "05-named-dd")
        row["verification"] = "UNVERIFIED"
        self.save()
        self.check_failure("owner-accepted verification status changed")

    def test_05_cannot_switch_oracle_path(self):
        row = next(row for row in self.rows if row["case_id"] == "05-named-dd")
        row["oracle"] = "pending:extra-value-12345"
        self.save()
        self.check_failure("accepted oracle path changed")

    def test_current_selector_traversal_fails(self):
        self.make_file("mr10-kit-compiler/asm/CURRENT", "../../icintv19.asm\n")
        self.check_failure("CURRENT must select")


if __name__ == "__main__":
    unittest.main()
