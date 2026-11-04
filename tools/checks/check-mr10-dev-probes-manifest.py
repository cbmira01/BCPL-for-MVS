#!/usr/bin/env python3
"""Host-only contract check for the proposed MR10 development-probe suite.

This script NEVER invokes MR10, JES, or a compiler. The manifest is a
contract inventory. Six owner-approved cases have accepted golden baselines.
"""
from __future__ import annotations

import csv
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "mr10-kit-compiler/tests/dev-probes-manifest.tsv"
PROBES = ROOT / "mr10-kit-compiler/tests"
FIELDS = (
    "case_id", "engine", "interpreter", "source", "modules",
    "dd_bindings", "sysin", "expected_code", "oracle", "artifacts",
    "verification",
)
# Historical group numbers are NOT sequential case numbers for the
# 00-regression-panel. Preserve these IDs when introducing a runner.
SPECS = (
    ("01-echo-test", "run-intcode", "current", "echo-sysin.int"),
    ("02-honors-thesis-and-mapstore/honors-thesis", "run-intcode", "v12",
     "intcode-v12-honors-thesis.int"),
    ("02-honors-thesis-and-mapstore/mapstore", "run-intcode", "v13",
     "intcode-v13-mapstore.int"),
    ("03-compile-richards-factorial/compile", "compile-and-run", "current",
     "richards-factorial-test.bcpl"),
    ("03-compile-richards-factorial/v14-intcode", "run-intcode", "v14",
     "compiled-factorial-v14.int"),
    ("04-module-test", "compile-and-run", "current", "module-test-1.bcpl"),
    ("05-named-dd", "compile-and-run", "current", "main.bcpl"),
    ("06-dynamic-streams", "compile-and-run", "current", "main.bcpl"),
    ("07-many-streams", "compile-and-run", "current", "main.bcpl"),
    ("08-character-translation", "compile-and-run", "current",
     "character-translation.bcpl"),
    ("09-multiple-assignment", "compile-and-run", "current",
     "multiple-assignment.bcpl"),
    ("10-coroutines/compiler-probe", "compile-and-run", "current",
     "compiler-probe.bcpl"),
    ("10-coroutines/frame-layout-probe", "compile-and-run", "current",
     "frame-layout-probe.bcpl"),
    ("10-coroutines/fixed-stack-producer-consumer", "compile-and-run",
     "current", "fixed-stack-producer-consumer.bcpl"),
    ("10-coroutines/resumeco-chain", "compile-and-run", "current",
     "resumeco-chain.bcpl"),
    ("10-coroutines/create-delete-static-pool", "compile-and-run", "current",
     "create-delete-static-pool.bcpl"),
    ("11-getvec-freevec", "compile-and-run", "current", "getvec-freevec.bcpl"),
)
# Freeze critical inputs in this pre-execution contract: merely checking
# that *listed* paths exist would allow required DDs or modules to disappear.
TEST_BASE = "mr10-kit-compiler/tests/"
LIB_BASE = "mr10-kit-compiler/library/"
INT_BASE = "mr10-kit-compiler/source/"
RUNTIME_MODULES = f"{INT_BASE}blibi.int;{INT_BASE}iclib.int"
COROUTINE_MODULES = f"{LIB_BASE}getvec-freevec.bcpl;{LIB_BASE}coroutines.bcpl"
REQUIRED_MODULES = {
    "01-echo-test": RUNTIME_MODULES,
    "03-compile-richards-factorial/v14-intcode": RUNTIME_MODULES,
    "04-module-test": f"{TEST_BASE}04-module-test/module-test-2.bcpl",
    "10-coroutines/resumeco-chain": COROUTINE_MODULES,
    "10-coroutines/create-delete-static-pool": COROUTINE_MODULES,
    "11-getvec-freevec": f"{LIB_BASE}getvec-freevec.bcpl",
}
REQUIRED_DDS = {
    "05-named-dd": f"EXTRA={TEST_BASE}05-named-dd/extra.bcpl",
    "06-dynamic-streams": ";".join(
        f"LEVEL{i}={TEST_BASE}06-dynamic-streams/level{i}.bcpl"
        for i in range(1, 4)),
    "07-many-streams": ";".join(
        f"DD{i:02d}={TEST_BASE}07-many-streams/dd{i:02d}.txt"
        for i in range(1, 13)),
    "08-character-translation": f"PUNCT={TEST_BASE}08-character-translation/punct.txt",
}
REQUIRED_SYSIN = {"01-echo-test": f"{TEST_BASE}01-echo-test/best-of-times.txt"}
ARTIFACT_CASES = {
    "03-compile-richards-factorial/compile", "08-character-translation",
    "10-coroutines/compiler-probe", "10-coroutines/frame-layout-probe",
}

ACCEPTED_GOLDENS = {
    "04-module-test": tuple(
        f"F({i}), = {n}" for i, n in enumerate(
            (1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800), 1)),
    "05-named-dd": ("VALUE FROM EXTRA = 12345",),
    "06-dynamic-streams": ("DEEPEST GET VALUE = 24680",),
    "07-many-streams": (
        "OPENED 12 STREAMS",
        *(f"DD{i} = STREAM {i:02d}" for i in range(1, 13)),
        "ALL 12 STREAMS READ AND CLOSED",
    ),
    "09-multiple-assignment": (
        "SWAP BEFORE A=1 B=2", "SWAP AFTER  A=2 B=2",
        "EUCLID BEFORE A=1071 B=462", "EUCLID AFTER  A=462 B=0",
    ),
    "11-getvec-freevec": (
        "ALLOCATED A B C", "A DATA 101 109", "B DATA 201 219",
        "C DATA 301 329", "REUSED B BLOCK",
        "COALESCED ALLOC 777 888", "GETVEC FREEVEC OK",
    ),
}


DDNAME = re.compile(r"[A-Z@#$][A-Z0-9@#$]{0,7}\Z")
PENDING = re.compile(r"pending:[a-z][a-z0-9-]+\Z")
ASM_NAME = re.compile(r"icintv[0-9]+\.asm\Z")


class ContractError(ValueError):
    """Manifest is not a safe, well-formed proposed probe inventory."""


def require(test: bool, reason: str) -> None:
    if not test:
        raise ContractError(reason)


def checked_file(root: Path, value: str, label: str) -> Path:
    path = Path(value)
    require(bool(value) and not path.is_absolute() and
            ".." not in path.parts and "\\" not in value,
            f"{label}: unsafe repository path: {value!r}")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(),
            f"{label}: missing or outside repository: {value!r}")
    return resolved


def items(value: str, label: str) -> list[str]:
    if not value:
        return []
    terms = value.split(";")
    require(all(terms) and len(terms) == len(set(terms)),
            f"{label}: empty or duplicate entry")
    return terms


def validate(root: Path = ROOT, manifest: Path | None = None) -> list[dict[str, str]]:
    manifest = manifest or root / "mr10-kit-compiler/tests/dev-probes-manifest.tsv"
    try:
        with manifest.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            require(tuple(reader.fieldnames or ()) == FIELDS,
                    "unexpected MR10 development-probe manifest columns")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ContractError(f"cannot read probe manifest: {exc}") from exc

    require(len(rows) == len(SPECS),
            f"expected {len(SPECS)} probe contracts; found {len(rows)}")
    spec_by_id = {entry[0]: entry for entry in SPECS}
    found = [row["case_id"] for row in rows]
    require(found == [entry[0] for entry in SPECS],
            "probe identities/order differ from the 11 historical groups")

    current = root / "mr10-kit-compiler/asm/CURRENT"
    try:
        filename = current.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError) as exc:
        raise ContractError(f"cannot read CURRENT interpreter selector: {exc}") from exc
    require(bool(ASM_NAME.fullmatch(filename)),
            "CURRENT must select one ICINT assembler filename")
    checked_file(root, f"mr10-kit-compiler/asm/{filename}", "CURRENT")

    groups = set()
    for row in rows:
        ident = row["case_id"]
        require(None not in row and all(value is not None for value in row.values()),
                f"{ident}: malformed TSV row")
        _, engine, interpreter, source_name = spec_by_id[ident]
        require(row["engine"] == engine and row["interpreter"] == interpreter,
                f"{ident}: execution engine or historical interpreter was changed")
        if interpreter != "current":
            checked_file(root, f"mr10-kit-compiler/asm/icint{interpreter}.asm",
                         f"{ident}: historical interpreter")
        group = ident.split("/", 1)[0]
        groups.add(group)
        folder = f"mr10-kit-compiler/tests/{group}"
        require(row["source"] == f"{folder}/{source_name}",
                f"{ident}: source identity differs from historical probe")
        source = checked_file(root, row["source"], f"{ident}: source")
        require(source.suffix == (".bcpl" if engine == "compile-and-run" else ".int"),
                f"{ident}: wrong source kind")
        require(row["modules"] == REQUIRED_MODULES.get(ident, ""),
                f"{ident}: required modules changed")
        require(row["dd_bindings"] == REQUIRED_DDS.get(ident, ""),
                f"{ident}: required DD bindings changed")
        require(row["sysin"] == REQUIRED_SYSIN.get(ident, ""),
                f"{ident}: required SYSIN changed")
        module_list = items(row["modules"], f"{ident}: modules")
        for module in module_list:
            path = checked_file(root, module, f"{ident}: module")
            require(path.suffix == (".bcpl" if engine == "compile-and-run" else ".int"),
                    f"{ident}: module type does not match execution engine")
        seen_dds = set()
        for binding in items(row["dd_bindings"], f"{ident}: DD bindings"):
            require(binding.count("=") == 1,
                    f"{ident}: invalid DD binding: {binding!r}")
            ddname, filename = binding.split("=", 1)
            require(bool(DDNAME.fullmatch(ddname)) and ddname not in seen_dds,
                    f"{ident}: invalid or duplicate DDNAME: {ddname!r}")
            seen_dds.add(ddname)
            checked_file(root, filename, f"{ident}: DD {ddname}")
        if row["sysin"]:
            require(engine == "run-intcode", f"{ident}: SYSIN support not declared for engine")
            checked_file(root, row["sysin"], f"{ident}: SYSIN")
        expected_code = -1 if ident.endswith("/mapstore") else 0
        require(row["expected_code"] == str(expected_code),
                f"{ident}: unexpected interpreted completion code")
        oracle = row["oracle"]
        if ident in ACCEPTED_GOLDENS:
            expected_path = f"mr10-kit-compiler/tests/{ident}/{ident}.expected"
            require(oracle == f"file:{expected_path}",
                    f"{ident}: accepted oracle path changed")
            golden = checked_file(root, expected_path, f"{ident}: accepted golden")
            expected_text = "\n".join(ACCEPTED_GOLDENS[ident]) + "\n"
            require(golden.read_text(encoding="utf-8") == expected_text,
                    f"{ident}: accepted golden output differs from owner-approved baseline")
        elif oracle.startswith("file:"):
            checked_file(root, oracle[5:], f"{ident}: expected output")
            require(ident.endswith("/honors-thesis"),
                    f"{ident}: new golden output requires separate evidence review")
        else:
            require(bool(PENDING.fullmatch(oracle)),
                    f"{ident}: unrecognized or missing output oracle")
        artifacts = row["artifacts"]
        require(artifacts == ("ocode,intcode" if ident in ARTIFACT_CASES else "none"),
                f"{ident}: artifact requirement changed")
        require(artifacts in ("none", "ocode,intcode"),
                f"{ident}: unknown artifact contract")
        require(engine == "compile-and-run" or artifacts == "none",
                f"{ident}: run-intcode cannot generate BCPL compiler artifacts")
        if ident in ACCEPTED_GOLDENS:
            require(row["verification"] == "ACCEPTED",
                    f"{ident}: owner-accepted verification status changed")
        else:
            require(row["verification"] == "UNVERIFIED",
                    f"{ident}: acceptance or blocking requires a separately reviewed evidence record")

    require(groups == {f"{i:02d}-{name}" for i, name in (
        (1, "echo-test"), (2, "honors-thesis-and-mapstore"),
        (3, "compile-richards-factorial"), (4, "module-test"),
        (5, "named-dd"), (6, "dynamic-streams"), (7, "many-streams"),
        (8, "character-translation"), (9, "multiple-assignment"),
        (10, "coroutines"), (11, "getvec-freevec"))},
        "a historical development-probe group is missing")
    return rows


def main() -> int:
    try:
        records = validate()
    except ContractError as exc:
        print(f"MR10 DEVELOPMENT PROBE MANIFEST: FAIL ({exc})", file=sys.stderr)
        return 2
    accepted = sum(row["verification"] == "ACCEPTED" for row in records)
    print(f"MR10 DEVELOPMENT PROBE MANIFEST: PASS "
          f"({len(records)} entries; {accepted} ACCEPTED, "
          f"{len(records) - accepted} UNVERIFIED; 11 historical groups; host-only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
