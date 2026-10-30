#!/usr/bin/env python3
"""Prepare a temporary-only Q.4 BCPLQSAM FB80 DASD + JES punch job.

First compile test-q4-punch.bcpl with the resident demoted Cambridge
compiler. This script only generates JCL; it NEVER submits a JES job.
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
JOB = "Q4PUNCH"
FB80 = "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)"


def query_helper():
    path = HERE / "prepare-q1-query.py"
    spec = importlib.util.spec_from_file_location("q4_query", path)
    if spec is None or spec.loader is None:
        raise ValueError("accepted Q.1 helper unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def part(rows: list[str], prefix: str) -> int:
    found = [i for i, row in enumerate(rows) if row.startswith(prefix)]
    if len(found) != 1:
        raise ValueError("expected one JCL part: " + prefix)
    return found[0]


def replace_one(rows: list[str], before: str, after: str) -> None:
    if rows.count(before) != 1:
        raise ValueError("expected one card: " + before)
    rows[rows.index(before)] = after


def temp_dd(create: bool) -> list[str]:
    rows = [
        "//Q4TEMP   DD  DSN=&&Q4CARD,DISP=(NEW,PASS)," if create
        else "//Q4TEMP   DD  DSN=&&Q4CARD,DISP=(OLD,DELETE),"
    ]
    if create:
        rows.append("//             UNIT=SYSDA,SPACE=(TRK,(1,1)),")
    rows.append(FB80)
    return rows


def verifier_link() -> list[str]:
    return [
        "//LKVR     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        "//SYSLIN   DD  DSN=&&Q4VOBJ,DISP=(OLD,PASS)",
        "//         DD  *",
        " ENTRY Q4VFY",
        " NAME Q4VFY(R)",
        "/*",
        "//SYSLMOD  DD  DSN=&&Q4VLD(Q4VFY),",
        "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
        "//             DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q4PUNCH\s+JOB\b", jobcard[0]):
        raise ValueError("Q4PUNCH job card required")
    q = query_helper()
    rows = q.make_deck(
        generated, ["//Q1QUERY JOB (BCPL),'Q4 TEMPLATE',CLASS=A"],
        obj_dsn).splitlines()
    rows[:1] = jobcard
    replace_one(rows,
                "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES",
                "//* Q.4 FB80: BCPL DUAL PUT; TEMP BINARY VERIFICATION")
    helper = q.time_helper().trailer_helper()
    verifier = q.time_helper().read_cards(
        helper, HERE / "q4-punch-verify.asm")
    rows[part(rows, "//ASMN     EXEC "):part(rows, "//ASMN     EXEC ")] = \
        helper.asm_step("ASMV", "Q4VOBJ", verifier)
    rows[part(rows, "//LKED     EXEC "):part(rows, "//LKED     EXEC ")] = \
        verifier_link()
    replace_one(rows, " NAME Q1QUERY(R)", " NAME Q4PUNCH(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                "//SYSLMOD  DD  DSN=&&Q4WLD(Q4PUNCH),")
    replace_one(rows, "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
                "//WGO      EXEC PGM=*.LKED.SYSLMOD,REGION=256K,")
    replace_one(rows, "//             TIME=(,2),COND=(0,NE,LKED)",
                "//             TIME=(,2),COND=(0,NE)")
    go = part(rows, "//WGO      EXEC ")
    rows[go+2:go+2] = [
        *temp_dd(True),
        "//SYSPUNCH DD  SYSOUT=B,",
        FB80,
    ]
    if rows[-1] != "//":
        raise ValueError("inherited JCL terminator missing")
    rows.pop()
    rows += [
        "//VGO      EXEC PGM=*.LKVR.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE)",
        *temp_dd(False),
        "//QOUT     DD  SYSOUT=A,",
        FB80,
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    return verify(rows)


def verify(rows: list[str]) -> str:
    if rows[-1] != "//" or rows.count("//") != 1:
        raise ValueError("bad JCL terminator")
    for i, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"invalid JCL/IFOX card {i}: {row!r}")
    if rows.count("//SYSIN    DD  *") != 6 or rows.count("/*") != 8:
        raise ValueError("invalid source/IEWL deck boundaries")
    for step in ("ASMA", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
                 "LKVR", "LKED", "WGO", "VGO"):
        part(rows, f"//{step:<8} EXEC ")
    if not (part(rows, "//LKVR     EXEC ") <
            part(rows, "//LKED     EXEC ") <
            part(rows, "//WGO      EXEC ") <
            part(rows, "//VGO      EXEC ")):
        raise ValueError("assembler/link/GO order incorrect")
    if (rows.count(" ENTRY R0APP") != 1 or
        rows.count(" NAME Q4PUNCH(R)") != 1 or
        rows.count(" ENTRY Q4VFY") != 1 or
        rows.count(" NAME Q4VFY(R)") != 1 or
        rows.count("         BCXREQ BCPLQSAM") != 1 or
        rows.count(" INCLUDE OBJ(BCPLIO)") != 1):
        raise ValueError("incorrect Q.4 link/registration selection")
    for block in (temp_dd(True), temp_dd(False)):
        at = part(rows, block[0])
        if rows[at:at+len(block)] != block:
            raise ValueError("temporary FB80 DD lifecycle changed")
    if (rows.count("//SYSPUNCH DD  SYSOUT=B,") != 1 or
        rows[rows.index("//SYSPUNCH DD  SYSOUT=B,")+1] != FB80 or
        rows.count("//QOUT     DD  SYSOUT=A,") != 1):
        raise ValueError("JES2 punch/independent PASS routing invalid")
    for step in ("LKVR", "LKED"):
        at = part(rows, f"//{step:<8} EXEC ")
        if ("REGION=256K" not in rows[at] or
            "//             COND=(0,NE)" not in rows[at:at+4]):
            raise ValueError("native link must have dependency guard")
    for step in ("WGO", "VGO"):
        at = part(rows, f"//{step:<8} EXEC ")
        if ("REGION=256K" not in rows[at] or
            rows[at+1] != "//             TIME=(,2),COND=(0,NE)"):
            raise ValueError("native GO must have region/dependency guard")
    if any("CATLG" in row or "DISP=MOD" in row or
           (row.startswith("//") and "BOOT_DEVOBJ" in row)
           for row in rows):
        raise ValueError("permanent MVS dataset operation prohibited")
    return "\n".join(rows) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="synthetic JCL check; no credentials/files/JES")
    ap.add_argument("--generated", type=Path,
                    help="CG370 output from actual MVS BCPL compiler")
    args = ap.parse_args()
    q = query_helper()
    if args.check:
        if args.generated is not None:
            ap.error("--check and --generated are exclusive")
        sample = q.time_helper().trailer_helper().sample_generated()
        deck = make_deck(
            sample, ["//Q4PUNCH JOB (BCPL),'Q4 CHECK',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")
        print(f"PASS: Q4PUNCH synthetic {len(deck.splitlines())} cards; "
              "no JES or files")
        return
    if args.generated is None:
        ap.error("--generated required")
    source = args.generated.resolve()
    if (ROOT / "workarea").resolve() not in source.parents:
        raise ValueError("CG370 source must reside under workarea")
    generated = source.read_bytes().decode("latin-1")
    core = q.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config["datasets"]["BOOT_OBJ"]
    if (spec.get("content_type") != "object" or
        spec.get("dsorg") != "PO" or
        spec.get("recfm") != "FB" or
        int(spec.get("lrecl", 0)) != 80):
        raise ValueError("manifest BOOT_OBJ must be FB80 object PDS")
    deck = make_deck(
        generated,
        core.authenticated_job_card(config, JOB, "QSAM Q4 PUNCH",
                                    redact_password=False),
        core.full_dsn(config, spec))
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / "q4punch.jcl"
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
        raise SystemExit("Q.4 punch preparation FAILED: " + str(exc))
