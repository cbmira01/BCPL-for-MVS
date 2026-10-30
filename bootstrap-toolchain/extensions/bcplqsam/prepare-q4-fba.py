#!/usr/bin/env python3
"""Prepare Q.4 FBA133 native BCPL/IFOX printer verification, no JES submit.

Compile test-q4-fba.bcpl using the resident demoted Cambridge compiler
before preparing authenticated JCL. Reuse the accepted Q4PUNCH linkage
pattern, replacing only the test verifier and record-output DDs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "workarea/bcplqsam-q4"
JOB = "Q4FBA"
FBA133 = "//             DCB=(RECFM=FBA,LRECL=133,BLKSIZE=133)"


def punch_helper():
    path = HERE / "prepare-q4-punch.py"
    spec = importlib.util.spec_from_file_location("q4_fba_punch", path)
    if spec is None or spec.loader is None:
        raise ValueError("accepted Q.4 punch helper unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def part(rows: list[str], prefix: str) -> int:
    hits = [i for i, row in enumerate(rows) if row.startswith(prefix)]
    if len(hits) != 1:
        raise ValueError("expected exactly one JCL part: " + prefix)
    return hits[0]


def replace_one(rows: list[str], old: str, new: str) -> None:
    if rows.count(old) != 1:
        raise ValueError("expected exactly one JCL card: " + old)
    rows[rows.index(old)] = new


def replace_block(rows: list[str], old: list[str], new: list[str]) -> None:
    if not old or rows.count(old[0]) != 1:
        raise ValueError("expected one JCL block: " + repr(old[0] if old else old))
    pos = rows.index(old[0])
    if rows[pos:pos + len(old)] != old:
        raise ValueError("unexpected existing JCL block: " + old[0])
    rows[pos:pos + len(old)] = new


def temp_dd(create: bool) -> list[str]:
    rows = [
        "//Q4TEMP   DD  DSN=&&Q4FBA,DISP=(NEW,PASS)," if create
        else "//Q4TEMP   DD  DSN=&&Q4FBA,DISP=(OLD,DELETE),"
    ]
    if create:
        rows.append("//             UNIT=SYSDA,SPACE=(TRK,(1,1)),")
    rows.append(FBA133)
    return rows


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q4FBA\s+JOB\b", jobcard[0]):
        raise ValueError("Q4FBA job card required")
    p = punch_helper()
    rows = p.make_deck(
        generated, ["//Q4PUNCH JOB (BCPL),'Q4 FBA TEMPLATE',CLASS=A"],
        obj_dsn).splitlines()
    rows[:1] = jobcard
    replace_one(rows,
                "//* Q.4 FB80: BCPL DUAL PUT; TEMP BINARY VERIFICATION",
                "//* Q.4 FBA133 ASA: TEMP READBACK; JES PRINTER CLASS A")
    q = p.query_helper()
    helper = q.time_helper().trailer_helper()
    verifier = q.time_helper().read_cards(
        helper, HERE / "q4-fba-verify.asm")
    asmv = part(rows, "//ASMV     EXEC ")
    asmn = part(rows, "//ASMN     EXEC ")
    rows[asmv:asmn] = helper.asm_step("ASMV", "Q4VOBJ", verifier)
    replace_one(rows, " ENTRY Q4VFY", " ENTRY Q4FAV")
    replace_one(rows, " NAME Q4VFY(R)", " NAME Q4FAV(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q4VLD(Q4VFY),",
                "//SYSLMOD  DD  DSN=&&Q4VLD(Q4FAV),")
    replace_one(rows, " NAME Q4PUNCH(R)", " NAME Q4FBA(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q4WLD(Q4PUNCH),",
                "//SYSLMOD  DD  DSN=&&Q4WLD(Q4FBA),")
    replace_block(rows, p.temp_dd(True), temp_dd(True))
    replace_block(rows, p.temp_dd(False), temp_dd(False))
    replace_block(rows, ["//SYSPUNCH DD  SYSOUT=B,", p.FB80],
                  ["//Q4PRINT  DD  SYSOUT=A,", FBA133])
    # QOUT carries the IFOX verification marker; it remains FB80.
    return verify(rows)


def verify(rows: list[str]) -> str:
    if (not rows or not re.match(r"^//Q4FBA\s+JOB\b", rows[0])
        or rows[-1] != "//" or rows.count("//") != 1):
        raise ValueError("invalid Q4FBA job or end card")
    for i, row in enumerate(rows, 1):
        if len(row) > 71 or not row.isascii() or "\t" in row:
            raise ValueError(f"bad fixed-column card {i}: {row!r}")
    if rows.count("//SYSIN    DD  *") != 6 or rows.count("/*") != 8:
        raise ValueError("wrong IFOX/IEWL source-deck boundaries")
    steps = ("ASMA", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
             "LKVR", "LKED", "WGO", "VGO")
    for step in steps:
        part(rows, f"//{step:<8} EXEC ")
    if not (part(rows, "//ASMV     EXEC ") <
            part(rows, "//ASMN     EXEC ") <
            part(rows, "//LKVR     EXEC ") <
            part(rows, "//LKED     EXEC ") <
            part(rows, "//WGO      EXEC ") <
            part(rows, "//VGO      EXEC ")):
        raise ValueError("Q4FBA native source/link/run ordering invalid")
    for disposition in (True, False):
        block = temp_dd(disposition)
        at = part(rows, block[0])
        if rows[at:at + len(block)] != block:
            raise ValueError("temporary FBA133 dataset lifecycle changed")
    printer = "//Q4PRINT  DD  SYSOUT=A,"
    at = part(rows, printer)
    if rows[at + 1] != FBA133 or rows.count(FBA133) != 3:
        raise ValueError("printer FBA133 geometry or routing changed")
    if rows.count("//QOUT     DD  SYSOUT=A,") != 1 or (
        rows[rows.index("//QOUT     DD  SYSOUT=A,") + 1] !=
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)"
    ):
        raise ValueError("independent verifier output invalid")
    for card in (" ENTRY R0APP", " ENTRY Q4FAV", " NAME Q4FAV(R)",
                 " NAME Q4FBA(R)", "         BCXREQ BCPLQSAM",
                 " INCLUDE OBJ(BCPLIO)"):
        if rows.count(card) != 1:
            raise ValueError("missing/duplicate native linkage: " + card)
    for step in ("LKVR", "LKED"):
        at = part(rows, f"//{step:<8} EXEC ")
        if ("REGION=256K" not in rows[at] or
            "//             COND=(0,NE)" not in rows[at:at + 4]):
            raise ValueError("missing IEWL region/dependency guard")
    for step in ("WGO", "VGO"):
        at = part(rows, f"//{step:<8} EXEC ")
        if ("REGION=256K" not in rows[at] or
            rows[at + 1] != "//             TIME=(,2),COND=(0,NE)"):
            raise ValueError("missing GO region/dependency guard")
    if any("CATLG" in row or "DISP=MOD" in row or
           (row.startswith("//") and "BOOT_DEVOBJ" in row) or
           "SYSOUT=B" in row
           for row in rows):
        raise ValueError("permanent allocation or unwanted punch routing")
    return "\n".join(rows) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="synthetic JCL only; no credentials/files/JES")
    ap.add_argument("--generated", type=Path,
                    help="real compiler CG370 output under workarea")
    args = ap.parse_args()
    p = punch_helper()
    q = p.query_helper()
    t0 = q.time_helper()
    if args.check:
        if args.generated is not None:
            ap.error("--check and --generated are exclusive")
        source = t0.trailer_helper().sample_generated()
        deck = make_deck(source,
                         ["//Q4FBA JOB (BCPL),'Q4 FBA CHECK',CLASS=A"],
                         "HERC02.BCPL.BOOT.OBJ")
        print(f"PASS: Q4FBA synthetic {len(deck.splitlines())} cards; "
              "no JES or files")
        return
    if args.generated is None:
        ap.error("--generated required for authenticated JCL")
    source = args.generated.resolve()
    if (ROOT / "workarea").resolve() not in source.parents:
        raise ValueError("CG370 source must reside under workarea")
    generated = source.read_bytes().decode("latin-1")
    core = t0.trailer_helper().load_core()
    config = core.load_config()
    obj = config["datasets"]["BOOT_OBJ"]
    if (obj.get("content_type") != "object" or obj.get("dsorg") != "PO"
        or obj.get("recfm") != "FB" or int(obj.get("lrecl", 0)) != 80):
        raise ValueError("manifest BOOT_OBJ must be FB80 object PDS")
    deck = make_deck(
        generated,
        core.authenticated_job_card(config, JOB, "QSAM Q4 FBA",
                                    redact_password=False),
        core.full_dsn(config, obj))
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / "q4fba.jcl"
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as out:
        out.write(deck)
    print(f"PREPARED ONLY: {target} ({len(deck.splitlines())} cards)")
    print("SHA-256: " + hashlib.sha256(deck.encode("ascii")).hexdigest())
    print("No JES submission, installed object or Hercules modification")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("Q.4 FBA preparation FAILED: " + str(exc))
