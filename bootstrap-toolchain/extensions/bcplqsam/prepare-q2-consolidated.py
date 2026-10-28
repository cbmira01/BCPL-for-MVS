#!/usr/bin/env python3
"""Prepare one Q.2 build/link/write/read/independent-check MVS job.

Two BCPL applications must first be compiled with the established
tools/bootstrap/compile-mvs into private CG370 assembler in workarea/.
The resulting ONE native Q2FULL job assembles both BCPL applications,
BCPLMAIN/BCPLRGS/BCPLQSAM, the BCX selection, and an independent
assembler verifier, links all three executables, then runs WGO/RGO/VGO.
All outputs are temporary datasets; this program NEVER submits JES.
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
WORK = ROOT / "workarea/bcplqsam-q2"
JOB = "Q2FULL"
LINK = "//LKED     EXEC PGM=IEWL,REGION=256K,"
GO = "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,"
DCB_F = "//             DCB=(RECFM=F,LRECL=80,BLKSIZE=80)"
DCB_FB = "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)"


def query_helper():
    path = HERE / "prepare-q1-query.py"
    spec = importlib.util.spec_from_file_location("q2_query", path)
    if spec is None or spec.loader is None:
        raise ValueError("Q.1 link/JCL helper is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def part(rows: list[str], prefix: str) -> int:
    matches = [i for i, row in enumerate(rows) if row.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError("expected one JCL part: " + prefix)
    return matches[0]


def replace_one(rows: list[str], old: str, new: str) -> None:
    if rows.count(old) != 1:
        raise ValueError("expected one JCL card: " + old)
    rows[rows.index(old)] = new


def link_reader(link: list[str]) -> list[str]:
    rd = list(link)
    replace_one(rd, LINK, "//LKRD     EXEC PGM=IEWL,REGION=256K,")
    replace_one(rd, "//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)",
                "//SYSLIN   DD  DSN=&&Q2RDOBJ,DISP=(OLD,PASS)")
    replace_one(rd, " NAME Q2WRIT(R)", " NAME Q2READ(R)")
    replace_one(rd, "//SYSLMOD  DD  DSN=&&Q2WLD(Q2WRIT),",
                "//SYSLMOD  DD  DSN=&&Q2RLD(Q2READ),")
    return rd


def link_verifier() -> list[str]:
    return [
        "//LKVR     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        "//SYSLIN   DD  DSN=&&Q2VOBJ,DISP=(OLD,PASS)",
        "//         DD  *",
        " ENTRY Q2VFY",
        " NAME Q2VFY(R)",
        "/*",
        "//SYSLMOD  DD  DSN=&&Q2VLD(Q2VFY),",
        "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
        "//             DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def dd(name: str, dataset: str, disposition: str, fmt: str,
       new: bool = False) -> list[str]:
    if fmt not in ("F", "FB"):
        raise ValueError("unsupported test geometry")
    rows = [f"//{name:<8} DD  DSN=&&{dataset},DISP=({disposition}),"]
    if new:
        rows.append("//             UNIT=SYSDA,SPACE=(TRK,(2,1)),")
    rows.append(DCB_F if fmt == "F" else DCB_FB)
    return rows


def go_step(step: str, load: str) -> list[str]:
    return [
        f"//{step:<8} EXEC PGM=*.{load}.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE)",
    ]


def make_deck(writer: str, reader: str, jobcard: list[str],
              obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q2FULL\s+JOB\b", jobcard[0]):
        raise ValueError("authenticated Q2FULL JOB card required")
    q = query_helper()
    base = q.make_deck(
        writer, ["//Q1QUERY JOB (BCPL),'Q.2 TEMPLATE',CLASS=A"], obj_dsn)
    rows = base.splitlines()
    rows[:1] = jobcard
    # This deck executes real QSAM OPEN/CLOSE: replace the Q.1 heading.
    replace_one(rows, "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES", "//* Q.2 CONSOLIDATED F/FB: TEMPORARY DDs; NO PDS WRITES")
    replace_one(rows, " NAME Q1QUERY(R)", " NAME Q2WRIT(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                "//SYSLMOD  DD  DSN=&&Q2WLD(Q2WRIT),")
    helper = q.time_helper().trailer_helper()
    asm_reader = helper.application_source(reader)
    verifier = q.time_helper().read_cards(
        helper, HERE / "q2-verify-copy.asm")
    i = part(rows, "//ASMN     EXEC ")
    rows[i:i] = [
        *helper.asm_step("ASMB", "Q2RDOBJ", asm_reader),
        *helper.asm_step("ASMV", "Q2VOBJ", verifier),
    ]
    link_at = part(rows, LINK)
    go_at = part(rows, GO)
    original_link = rows[link_at:go_at]
    rows[go_at:go_at] = [
        *link_reader(original_link),
        *link_verifier(),
    ]
    replace_one(rows, GO, "//WGO      EXEC PGM=*.LKED.SYSLMOD,REGION=256K,")
    replace_one(rows, "//             TIME=(,2),COND=(0,NE,LKED)",
                "//             TIME=(,2),COND=(0,NE)")
    # Writer, reader and verifier are separate GO executions in ONE JOB.
    wgo = part(rows, "//WGO      EXEC ")
    sysprint = next(
        i for i in range(wgo + 2, len(rows))
        if rows[i] == "//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,"
    )
    rows[sysprint:sysprint] = [
        *dd("QFOUT", "Q2F", "NEW,PASS", "F", new=True),
        *dd("QBOUT", "Q2B", "NEW,PASS", "FB", new=True),
        *dd("QEMPTY", "Q2E", "NEW,PASS", "F", new=True),
    ]
    # Remove the inherited final JCL job terminator; add both later GO steps.
    if rows[-1] != "//":
        raise ValueError("inherited Q.1 job terminator missing")
    rows.pop()
    rows += [
        *go_step("RGO", "LKRD"),
        *dd("QFOUT", "Q2F", "OLD,DELETE", "F"),
        *dd("QBOUT", "Q2B", "OLD,DELETE", "FB"),
        *dd("QEMPTY", "Q2E", "OLD,DELETE", "F"),
        *dd("QBCOPY", "Q2C", "NEW,PASS", "FB", new=True),
        "//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,",
        "//             BLKSIZE=132)",
        "//SYSUDUMP DD  SYSOUT=*",
        *go_step("VGO", "LKVR"),
        *dd("QBCOPY", "Q2C", "OLD,DELETE", "FB"),
        "//QOUT     DD  SYSOUT=*,",
        DCB_FB,
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    return verify(rows)


def verify(rows: list[str]) -> str:
    if not rows or not re.match(r"^//Q2FULL\s+JOB\b", rows[0]):
        raise ValueError("Q2FULL card missing")
    if rows[-1] != "//" or rows.count("//") != 1:
        raise ValueError("single final job terminator required")
    for n, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"bad fixed-card line {n}: {row!r}")
        if ("CATLG" in row or "DISP=MOD" in row or
            (row.startswith("//") and "BOOT_DEVOBJ" in row) or
            row.startswith("//EXTLIB")):
            raise ValueError("prohibited permanent MVS dataset operation")
    if rows.count("//SYSIN    DD  *") != 7 or rows.count("/*") != 10:
        raise ValueError("wrong assembler/linker in-stream card boundaries")
    for step in ("ASMA", "ASMB", "ASMV", "ASMN", "ASMR", "ASMQ",
                 "ASMG", "LKED", "LKRD", "LKVR", "WGO", "RGO", "VGO"):
        if len([r for r in rows if r.startswith(f"//{step:<8} EXEC ")]) != 1:
            raise ValueError("missing or duplicate step: " + step)
    if rows.count("         BCXREQ BCPLQSAM") != 1:
        raise ValueError("BCX registration missing or duplicated")
    if rows.count(" ENTRY R0APP") != 2 or rows.count(" ENTRY Q2VFY") != 1:
        raise ValueError("incorrect IEWL entry records")
    if rows.count(" NAME Q2WRIT(R)") != 1:
        raise ValueError("writer link output absent")
    if rows.count(" NAME Q2READ(R)") != 1:
        raise ValueError("reader link output absent")
    if rows.count(" NAME Q2VFY(R)") != 1:
        raise ValueError("verifier link output absent")
    if not part(rows, "//LKED     EXEC ") < part(rows, "//LKRD     EXEC "):
        raise ValueError("wrong writer/reader link sequence")
    # Lock each link to its own application object and load member.
    # The reader is cloned after the writer link has been renamed.
    expected_links = (
        ("LKED", "LKRD", "Q1APOBJ", "Q2WLD(Q2WRIT)", "Q2WRIT"),
        ("LKRD", "LKVR", "Q2RDOBJ", "Q2RLD(Q2READ)", "Q2READ"),
    )
    for link_step, next_step, appobj, loadmod, name in expected_links:
        begin = part(rows, f"//{link_step:<8} EXEC ")
        end = part(rows, f"//{next_step:<8} EXEC ")
        section = rows[begin:end]
        if (section.count(
                f"//SYSLIN   DD  DSN=&&{appobj},DISP=(OLD,PASS)") != 1
            or section.count(
                f"//SYSLMOD  DD  DSN=&&{loadmod},") != 1
            or section.count(f" NAME {name}(R)") != 1):
            raise ValueError(link_step + ": incorrect object/load identity")
    if not part(rows, "//LKVR     EXEC ") < part(rows, "//WGO      EXEC "):
        raise ValueError("verifier link must precede native GO")
    if not (part(rows, "//WGO      EXEC ") <
            part(rows, "//RGO      EXEC ") <
            part(rows, "//VGO      EXEC ")):
        raise ValueError("GO phases out of order")
    for name, ds, fmt in (("QFOUT", "Q2F", "F"),
                          ("QBOUT", "Q2B", "FB"),
                          ("QEMPTY", "Q2E", "F")):
        new = dd(name, ds, "NEW,PASS", fmt, new=True)
        old = dd(name, ds, "OLD,DELETE", fmt)
        if rows.count(new[0]) != 1 or rows.count(old[0]) != 1:
            raise ValueError("temporary DD lifecycle missing: " + name)
        if rows[rows.index(new[0])+1:rows.index(new[0])+3] != new[1:]:
            raise ValueError("writer DD geometry incorrect: " + name)
        if rows[rows.index(old[0])+1] != old[1]:
            raise ValueError("reader DD geometry incorrect: " + name)
    copy_new = dd("QBCOPY", "Q2C", "NEW,PASS", "FB", new=True)
    copy_old = dd("QBCOPY", "Q2C", "OLD,DELETE", "FB")
    if rows.count(copy_new[0]) != 1 or rows.count(copy_old[0]) != 1:
        raise ValueError("independent verifier copy DD lifecycle missing")
    if rows.count("//QOUT     DD  SYSOUT=*,") != 1:
        raise ValueError("independent verifier PASS output missing")
    # All jobs use 256K REGION, and every execution skips earlier failures.
    for step in ("WGO", "RGO", "VGO"):
        i = part(rows, f"//{step:<8} EXEC ")
        if "REGION=256K" not in rows[i] or "COND=(0,NE)" not in rows[i+1]:
            raise ValueError("native GO requires 256K and dependency gate")
    return "\n".join(rows) + "\n"


def allowed_generated(path: Path) -> str:
    source = path.resolve()
    if (ROOT / "workarea").resolve() not in source.parents:
        raise ValueError("CG370 source must be under ignored workarea")
    if not source.is_file():
        raise ValueError("missing compiled CG370 source")
    return source.read_bytes().decode("latin-1")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="synthetic deck; no credentials, JCL or JES writes")
    ap.add_argument("--writer", type=Path,
                    help="compiled test-q2-write.bcpl assembler in workarea")
    ap.add_argument("--reader", type=Path,
                    help="compiled test-q2-read.bcpl assembler in workarea")
    args = ap.parse_args()
    q = query_helper()
    if args.check:
        if args.writer or args.reader:
            ap.error("--check does not take real compiled source")
        sample = q.time_helper().trailer_helper().sample_generated()
        deck = make_deck(
            sample, sample, ["//Q2FULL JOB (BCPL),'Q2 OFFLINE',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")
        print(f"PASS: Q2FULL consolidated synthetic deck "
              f"{len(deck.splitlines())} cards; no JES submission")
        return
    if args.writer is None or args.reader is None:
        ap.error("--writer and --reader are both required")
    core = q.time_helper().trailer_helper().load_core()
    config = core.load_config()
    obj = config["datasets"]["BOOT_OBJ"]
    if (obj.get("content_type") != "object" or obj.get("dsorg") != "PO"
        or obj.get("recfm") != "FB" or int(obj.get("lrecl", 0)) != 80):
        raise ValueError("BOOT_OBJ manifest entry is not accepted FB80 PDS")
    deck = make_deck(
        allowed_generated(args.writer), allowed_generated(args.reader),
        core.authenticated_job_card(config, JOB, "QSAM Q2 FULL",
                                    redact_password=False),
        core.full_dsn(config, obj),
    )
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / "q2full.jcl"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as out:
        out.write(deck)
    print(f"PREPARED ONLY: {target} ({len(deck.splitlines())} cards)")
    print("SHA-256: " + hashlib.sha256(deck.encode("ascii")).hexdigest())
    print("No JES submission, production object writes, or permanent datasets")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("Q.2 campaign preparation FAILED: " + str(exc))
