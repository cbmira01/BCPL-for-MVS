#!/usr/bin/env python3
"""Stage/review one M5.2 negative-control QSAM verifier job (NO SUBMISSION).

Reuses accepted JOB 8185's immutable M5.1.2 positive v2 deck. Changes
ONLY its JOB name and a verifier-only MVI that corrupts the *expected*
132nd byte of the first REPORT FB132 record. Actual BCPL GO program,
QSAM datasets, DD assignments, EODAD paths and return logic are unchanged.
Expected: ASMAP/LKED/GO/VASM/VLINK RC0; VCHK RC12, without abend.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "workarea/native-regression/124-dynamic-dd-selected-output"
POSITIVE = WORK / "m51-fb132-dataset-v2.jcl"
POS_ASM = WORK / "m51-fb132-verifier-v2.asm"
POS_META = WORK / "m51-fb132-dataset-v2.json"
SOURCE = WORK / "runtime-pds-go.jcl"
CASE = ROOT / "native-compiler/regression/124-dynamic-dd-selected-output"
DECK = WORK / "m52-padding-negative.jcl"
ASM = WORK / "m52-padding-negative.asm"
META = WORK / "m52-padding-negative.json"
JOB = "M52PAD"
INSTRUCTION = "         MVI   EXP11+131,C'X'"
ANCHOR = "         OPEN  (DCB2,(INPUT))\n         GET   DCB1,BUF1\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def positive_verifier():
    path = ROOT / "tools/checks/m51-fb132-dataset-probe.py"
    spec = importlib.util.spec_from_file_location("m51_fb132", path)
    if not spec or not spec.loader:
        raise ValueError("M5.1.2 verified generator cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_positive() -> tuple[bytes, bytes, bytes]:
    module = positive_verifier()
    paths = [SOURCE, POSITIVE, POS_ASM, POS_META,
             CASE / "expected-report.txt", CASE / "expected-report2.txt"]
    for path in paths:
        if not path.is_file():
            raise ValueError(f"missing accepted M5.1.2 input: {path}")
    source, deck, asm = (SOURCE.read_bytes(), POSITIVE.read_bytes(),
                         POS_ASM.read_bytes())
    manifest = json.loads(POS_META.read_text(encoding="utf-8"))
    module.review_bundle(
        source, deck, asm,
        (CASE / "expected-report.txt").read_bytes(),
        (CASE / "expected-report2.txt").read_bytes(), manifest)
    return source, deck, asm


def negative_variant(positive_deck: bytes, positive_asm: bytes) -> tuple[bytes, bytes]:
    """Exact two-delta transformation of accepted positive artifacts."""
    try:
        deck = positive_deck.decode("ascii")
        asm = positive_asm.decode("ascii")
    except UnicodeError as exc:
        raise ValueError(f"positive evidence is not ASCII JCL/ASM: {exc}") from exc
    if asm.count(ANCHOR) != 1 or asm.count(INSTRUCTION) != 0:
        raise ValueError("unsupported or pre-mutated verifier assembler")
    # CL132 is padded with EBCDIC blank X'40'. Byte at +131 is the
    # final blank. MVI sets expected byte 132 to EBCDIC 'X' (X'E7').
    if asm.count("EXP11    DC    CL132'BCPL REPORT A'") != 1:
        raise ValueError("first expected FB132 record has drifted")
    altered_asm = asm.replace(
        ANCHOR, ANCHOR.replace("         GET   DCB1,BUF1\n",
                               INSTRUCTION + "\n         GET   DCB1,BUF1\n"), 1)
    if len(re.findall(r"^//M5D124B\s+JOB\b", deck, re.M)) != 1:
        raise ValueError("expected positive JOB name M5D124B")
    deck = re.sub(r"^//M5D124B(?=\s+JOB\b)", "//" + JOB,
                  deck, count=1, flags=re.M)
    original_cards = asm.rstrip("\n")
    if deck.count(original_cards) != 1:
        raise ValueError("positive deck does not contain exact verifier source")
    deck = deck.replace(original_cards, altered_asm.rstrip("\n"), 1)
    if any(len(line) > 71 for line in deck.splitlines()):
        raise ValueError("negative deck exceeds card column 71")

    original_go = positive_deck.decode("ascii").split("//VASM     EXEC", 1)
    negative_go = deck.split("//VASM     EXEC", 1)
    # The real authenticated MVS JOB card can have multiple spaces between
    # the job name and JOB; the minimal offline fixture used only one.
    # Restore JUST the name token and preserve the exact original spacing.
    if len(original_go) != 2 or len(negative_go) != 2:
        raise ValueError("compiled BCPL GO/JCL changed in negative probe")
    restored_go, restored_count = re.subn(
        rf"^//{re.escape(JOB)}(?=\s+JOB\b)", "//M5D124B",
        negative_go[0], count=1, flags=re.M)
    if restored_count != 1 or restored_go != original_go[0]:
        raise ValueError("compiled BCPL GO/JCL changed in negative probe")
    if deck.count(INSTRUCTION) != 1:
        raise ValueError("missing unique expected-padding mutation")
    if deck.count("DSN=&&M5RPT1") != 2 or deck.count("DSN=&&M5RPT2") != 2:
        raise ValueError("physical REPORT/REPORT2 dataset binding changed")
    return deck.encode("ascii"), altered_asm.encode("ascii")


def prepare() -> None:
    if any(path.exists() for path in (DECK, ASM, META)):
        raise ValueError("M5.2 output already staged; refusing overwrite")
    _, positive_deck, positive_asm = validate_positive()
    deck, asm = negative_variant(positive_deck, positive_asm)
    DECK.write_bytes(deck)
    ASM.write_bytes(asm)
    record = {
        "schema": "bcpl-m52-pad-negative-v1",
        "job": JOB,
        "expected": {
            "ASMAP": 0, "LKED": 0, "GO": 0,
            "VASM": 0, "VLINK": 0, "VCHK": 12,
        },
        "positive_deck_sha256": sha(positive_deck),
        "positive_asm_sha256": sha(positive_asm),
        "negative_deck_sha256": sha(deck),
        "negative_asm_sha256": sha(asm),
        "fault": "verifier expected FB132 byte 132 changed from EBCDIC blank X40 to X",
        "actual_bcpl_output": "unchanged",
        "status": "PREPARED_NOT_SUBMITTED",
    }
    META.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("M5.2 padding negative control PREPARED (no JES submission)")
    print("  JOB M52PAD: unchanged compiled BCPL GO and two FB132 DDs")
    print("  Injected verifier-only instruction: " + INSTRUCTION.strip())
    print("  Expected return codes: 0/0/0/0/0/12; no abend")
    for item in (DECK, ASM, META):
        print("  " + str(item.relative_to(ROOT)))


def review() -> None:
    _, positive_deck, positive_asm = validate_positive()
    if not all(path.is_file() for path in (DECK, ASM, META)):
        raise ValueError("M5.2 staged bundle incomplete")
    deck, asm = negative_variant(positive_deck, positive_asm)
    manifest = json.loads(META.read_text(encoding="utf-8"))
    if manifest.get("schema") != "bcpl-m52-pad-negative-v1" or (
        manifest.get("job") != JOB
        or manifest.get("status") != "PREPARED_NOT_SUBMITTED"
        or manifest.get("expected") != {
            "ASMAP": 0, "LKED": 0, "GO": 0,
            "VASM": 0, "VLINK": 0, "VCHK": 12,
        }
    ):
        raise ValueError("M5.2 negative manifest metadata drifted")
    for title, actual, field in (
        ("positive deck", positive_deck, "positive_deck_sha256"),
        ("positive assembler", positive_asm, "positive_asm_sha256"),
        ("negative deck", DECK.read_bytes(), "negative_deck_sha256"),
        ("negative assembler", ASM.read_bytes(), "negative_asm_sha256"),
    ):
        if sha(actual) != manifest.get(field):
            raise ValueError(f"{title}: SHA256 mismatch")
    if DECK.read_bytes() != deck or ASM.read_bytes() != asm:
        raise ValueError("negative artifacts differ from exactly regenerated probe")
    print("M5.2 padding negative offline artifact review: PASS")
    print("  Original JOB 8185 positive artifact independently revalidated")
    print("  M52PAD JCL identical except job name and one verifier instruction")
    print("  Verifier compares all 132 FB132 bytes; final padding byte altered")
    print("  Negative expected: VCHK RC0012; other steps RC0000; no abend")
    print("  No MVS job submitted by this tool")


def main(argv: list[str]) -> int:
    if argv not in (["prepare"], ["review"]):
        raise ValueError("usage: m52-padding-negative.py prepare|review")
    if argv == ["prepare"]:
        prepare()
    else:
        review()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        sys.exit(f"m52-padding-negative: {exc}")
