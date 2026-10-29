#!/usr/bin/env python3
"""Prepare Q.3 independent IFOX writer + native BCPL V READ job.

The BCPL reader must first be compiled with tools/bootstrap/compile-mvs.
No compiler/JES submission or permanent MVS dataset write occurs here.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "workarea/bcplqsam-q3"
JOB = "Q3VREAD"


def query_helper():
    path = HERE / "prepare-q1-query.py"
    spec = importlib.util.spec_from_file_location("q3_query", path)
    if spec is None or spec.loader is None:
        raise ValueError("accepted Q.1 integration helper missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def part(rows: list[str], prefix: str) -> int:
    found = [i for i, row in enumerate(rows) if row.startswith(prefix)]
    if len(found) != 1:
        raise ValueError("expected one JCL part " + prefix)
    return found[0]


def replace_one(rows: list[str], before: str, after: str) -> None:
    if rows.count(before) != 1:
        raise ValueError("expected one JCL card " + before)
    rows[rows.index(before)] = after


def dataset_dd(disposition: str, create: bool) -> list[str]:
    rows = [
        "//QVDATA   DD  DSN=&&Q3V,DISP=(" + disposition + "),",
    ]
    if create:
        rows += ["//             UNIT=SYSDA,SPACE=(TRK,(2,1)),"]
    rows += ["//             DCB=(RECFM=V,LRECL=100,BLKSIZE=104)"]
    return rows


def writer_link() -> list[str]:
    return [
        "//LKWR     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        "//SYSLIN   DD  DSN=&&Q3WOBJ,DISP=(OLD,PASS)",
        "//         DD  *",
        " ENTRY Q3VWRT",
        " NAME Q3VWRT(R)",
        "/*",
        "//SYSLMOD  DD  DSN=&&Q3WLD(Q3VWRT),",
        "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
        "//             DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def verify(rows: list[str]) -> str:
    if not rows or not re.match(r"^//Q3VREAD\s+JOB\b", rows[0]):
        raise ValueError("authenticated Q3VREAD job name missing")
    if rows.count("//") != 1 or rows[-1] != "//":
        raise ValueError("JCL termination invalid")
    if any(len(row) > 71 or not row.isascii() or "\t" in row
           for row in rows):
        raise ValueError("JCL/IFOX card outside fixed-column limits")
    if rows.count("//SYSIN    DD  *") != 6 or rows.count("/*") != 8:
        raise ValueError("assembler/linker stream boundaries incorrect")
    steps = ("ASMA", "ASMW", "ASMN", "ASMR", "ASMQ", "ASMG",
             "LKWR", "LKED", "WGO", "RGO")
    for step in steps:
        part(rows, f"//{step:<8} EXEC ")
    if not (part(rows, "//ASMA     EXEC ") <
            part(rows, "//ASMW     EXEC ") <
            part(rows, "//ASMN     EXEC ") <
            part(rows, "//LKWR     EXEC ") <
            part(rows, "//LKED     EXEC ") <
            part(rows, "//WGO      EXEC ") <
            part(rows, "//RGO      EXEC ")):
        raise ValueError("execution order incorrect")
    if (rows.count(" ENTRY Q3VWRT") != 1 or
        rows.count(" ENTRY R0APP") != 1 or
        rows.count(" NAME Q3VWRT(R)") != 1 or
        rows.count(" NAME Q3VRED(R)") != 1 or
        rows.count("         BCXREQ BCPLQSAM") != 1):
        raise ValueError("link-edit and registration identities incorrect")
    if rows.count("//SYSLIN   DD  DSN=&&Q3WOBJ,DISP=(OLD,PASS)") != 1:
        raise ValueError("independent writer object not linked")
    if rows.count("//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)") != 1:
        raise ValueError("compiled BCPL reader object missing")
    for disposition, create in (("NEW,PASS", True),
                                ("OLD,DELETE", False)):
        block = dataset_dd(disposition, create)
        at = part(rows, block[0])
        if rows[at:at+len(block)] != block:
            raise ValueError("temporary V DD geometry/lifecycle changed")
    if part(rows, "//WGO      EXEC ") >= part(rows, "//RGO      EXEC "):
        raise ValueError("writer must execute before reader")
    for step in ("WGO", "RGO"):
        pos = part(rows, f"//{step:<8} EXEC ")
        if "REGION=256K" not in rows[pos] or "COND=(0,NE)" not in rows[pos+1]:
            raise ValueError("missing native GO region/dependency guard")
    if any("CATLG" in row or "DISP=MOD" in row or
           (row.startswith("//") and not row.startswith("//*") and
            "BOOT_DEVOBJ" in row) for row in rows):
        raise ValueError("prohibited permanent MVS dataset operation")
    if rows.count(" INCLUDE OBJ(BCPLIO)") != 1:
        raise ValueError("production BCPLIO reference missing")
    return "\n".join(rows) + "\n"


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q3VREAD\s+JOB\b", jobcard[0]):
        raise ValueError("Q3VREAD JOB card required")
    q = query_helper()
    sample = q.make_deck(
        generated,
        ["//Q1QUERY JOB (BCPL),'Q3 TEMPLATE',CLASS=A"],
        obj_dsn)
    rows = sample.splitlines()
    rows[:1] = jobcard
    replace_one(
        rows,
        "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES",
        "//* Q.3 V READ: INDEPENDENT WRITER; TEMPORARY DASD ONLY")
    helper = q.time_helper().trailer_helper()
    writer = q.time_helper().read_cards(helper, HERE / "q3-v-writer.asm")
    at = part(rows, "//ASMN     EXEC ")
    rows[at:at] = helper.asm_step("ASMW", "Q3WOBJ", writer)
    at = part(rows, "//LKED     EXEC ")
    rows[at:at] = writer_link()
    replace_one(rows, " NAME Q1QUERY(R)", " NAME Q3VRED(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                "//SYSLMOD  DD  DSN=&&Q3RLD(Q3VRED),")
    replace_one(
        rows,
        "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        "//RGO      EXEC PGM=*.LKED.SYSLMOD,REGION=256K,")
    replace_one(rows, "//             TIME=(,2),COND=(0,NE,LKED)",
                "//             TIME=(,2),COND=(0,NE)")
    at = part(rows, "//RGO      EXEC ")
    rows[at:at] = [
        "//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE)",
        *dataset_dd("NEW,PASS", True),
        "//SYSUDUMP DD  SYSOUT=*",
    ]
    at = part(rows, "//RGO      EXEC ")
    rows[at+2:at+2] = dataset_dd("OLD,DELETE", False)
    return verify(rows)


def verifier_link() -> list[str]:
    return [
        "//LKVR     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        "//SYSLIN   DD  DSN=&&Q3VOBJ,DISP=(OLD,PASS)",
        "//         DD  *",
        " ENTRY Q3VFY",
        " NAME Q3VFY(R)",
        "/*",
        "//SYSLMOD  DD  DSN=&&Q3VLD(Q3VFY),",
        "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
        "//             DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def make_write_deck(generated: str, jobcard: list[str],
                    obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q3VWRIT\s+JOB\b", jobcard[0]):
        raise ValueError("Q3VWRIT JOB card required")
    q = query_helper()
    rows = q.make_deck(
        generated, ["//Q1QUERY JOB (BCPL),'Q3 TEMPLATE',CLASS=A"],
        obj_dsn).splitlines()
    rows[:1] = jobcard
    replace_one(
        rows,
        "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES",
        "//* Q.3 V WRITE: BCPL PUT; INDEPENDENT IFOX RDW READER")
    helper = q.time_helper().trailer_helper()
    verifier = q.time_helper().read_cards(
        helper, HERE / "q3-v-verify.asm")
    at = part(rows, "//ASMN     EXEC ")
    rows[at:at] = helper.asm_step("ASMV", "Q3VOBJ", verifier)
    at = part(rows, "//LKED     EXEC ")
    rows[at:at] = verifier_link()
    replace_one(rows, " NAME Q1QUERY(R)", " NAME Q3VPUT(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                "//SYSLMOD  DD  DSN=&&Q3WLD(Q3VPUT),")
    replace_one(
        rows, "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        "//WGO      EXEC PGM=*.LKED.SYSLMOD,REGION=256K,")
    replace_one(rows, "//             TIME=(,2),COND=(0,NE,LKED)",
                "//             TIME=(,2),COND=(0,NE)")
    at = part(rows, "//WGO      EXEC ")
    rows[at+2:at+2] = dataset_dd("NEW,PASS", True)
    if rows[-1] != "//":
        raise ValueError("inherited job terminator missing")
    rows.pop()
    rows += [
        "//VGO      EXEC PGM=*.LKVR.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE)",
        *dataset_dd("OLD,DELETE", False),
        "//QOUT     DD  SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for step in ("ASMA", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
                 "LKVR", "LKED", "WGO", "VGO"):
        part(rows, f"//{step:<8} EXEC ")
    if (rows.count("//SYSIN    DD  *") != 6 or
        rows.count("/*") != 8 or
        rows.count(" ENTRY R0APP") != 1 or
        rows.count(" ENTRY Q3VFY") != 1 or
        rows.count("         BCXREQ BCPLQSAM") != 1):
        raise ValueError("Q3VWRIT native source/link boundaries invalid")
    if not (part(rows, "//LKVR     EXEC ") <
            part(rows, "//LKED     EXEC ") <
            part(rows, "//WGO      EXEC ") <
            part(rows, "//VGO      EXEC ")):
        raise ValueError("Q3VWRIT execution order invalid")
    for disposition, new in (("NEW,PASS", True),
                             ("OLD,DELETE", False)):
        block = dataset_dd(disposition, new)
        at = part(rows, block[0])
        if rows[at:at+len(block)] != block:
            raise ValueError("Q3VWRIT temporary V DD mismatch")
    if (rows.count("//QOUT     DD  SYSOUT=*,") != 1 or
        rows.count("//") != 1 or
        any(len(row) > 71 or not row.isascii() or "\t" in row
            for row in rows)):
        raise ValueError("Q3VWRIT invalid IFOX/JCL card or output")
    if any("CATLG" in row or "DISP=MOD" in row for row in rows):
        raise ValueError("Q3VWRIT permanent output prohibited")
    return "\n".join(rows) + "\n"



def limit_dataset_dd(fmt: str, disposition: str,
                     create: bool) -> list[str]:
    if fmt not in ("v", "vb"):
        raise ValueError("Q.3 limit format must be V or VB")
    recfm = fmt.upper()
    blksize = 1028 if fmt == "v" else 2052
    rows = ["//QVDATA   DD  DSN=&&Q3L,DISP=(" + disposition + "),"]
    if create:
        rows.append("//             UNIT=SYSDA,SPACE=(TRK,(4,2)),")
    rows.append(f"//             DCB=(RECFM={recfm},"
                f"LRECL=1024,BLKSIZE={blksize})")
    return rows


def limit_job(fmt: str, writing: bool) -> str:
    if fmt not in ("v", "vb"):
        raise ValueError("unrecognized limit format")
    tag = "VL" if fmt == "v" else "VB"
    return "Q3" + tag + ("WRT" if writing else "RED")


def limit_link(writing: bool) -> list[str]:
    step = "LKVR" if writing else "LKWR"
    member = "Q3LMV" if writing else "Q3LMW"
    obj = "Q3LOBJ"
    load = "Q3LLD"
    return [
        f"//{step:<8} EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        f"//SYSLIN   DD  DSN=&&{obj},DISP=(OLD,PASS)",
        "//         DD  *",
        f" ENTRY {member}",
        f" NAME {member}(R)",
        "/*",
        f"//SYSLMOD  DD  DSN=&&{load}({member}),",
        "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
        "//             DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def make_limit_deck(generated: str, jobcard: list[str],
                    obj_dsn: str, fmt: str, writing: bool) -> str:
    job = limit_job(fmt, writing)
    if not jobcard or not re.match(r"^//" + job + r"\s+JOB\b",
                                   jobcard[0]):
        raise ValueError("Q.3 limit JOB card name mismatch")
    q = query_helper()
    rows = q.make_deck(
        generated, ["//Q1QUERY JOB (BCPL),'Q3 TEMPLATE',CLASS=A"],
        obj_dsn).splitlines()
    rows[:1] = jobcard
    replace_one(
        rows,
        "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES",
        "//* Q.3 1024 V/VB: BCPL AND INDEPENDENT IFOX; TEMP DASD")
    helper = q.time_helper().trailer_helper()
    member = "q3-limit-verify.asm" if writing else "q3-limit-writer.asm"
    cards = q.time_helper().read_cards(helper, HERE / member)
    at = part(rows, "//ASMN     EXEC ")
    rows[at:at] = helper.asm_step("ASML", "Q3LOBJ", cards)
    at = part(rows, "//LKED     EXEC ")
    rows[at:at] = limit_link(writing)
    appname = "Q3LPUT" if writing else "Q3LRED"
    load = "Q3LWLD" if writing else "Q3LRLD"
    replace_one(rows, " NAME Q1QUERY(R)", f" NAME {appname}(R)")
    replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                f"//SYSLMOD  DD  DSN=&&{load}({appname}),")
    step = "WGO" if writing else "RGO"
    replace_one(
        rows, "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        f"//{step:<8} EXEC PGM=*.LKED.SYSLMOD,REGION=256K,")
    replace_one(rows, "//             TIME=(,2),COND=(0,NE,LKED)",
                "//             TIME=(,2),COND=(0,NE)")
    at = part(rows, f"//{step:<8} EXEC ")
    if writing:
        rows[at+2:at+2] = limit_dataset_dd(fmt, "NEW,PASS", True)
        if rows[-1] != "//":
            raise ValueError("inherited job terminator missing")
        rows.pop()
        rows += [
            "//VGO      EXEC PGM=*.LKVR.SYSLMOD,REGION=256K,",
            "//             TIME=(,2),COND=(0,NE)",
            *limit_dataset_dd(fmt, "OLD,DELETE", False),
            "//QOUT     DD  SYSOUT=*,",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSUDUMP DD  SYSOUT=*",
            "//",
        ]
    else:
        rows[at:at] = [
            "//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,",
            "//             TIME=(,2),COND=(0,NE)",
            *limit_dataset_dd(fmt, "NEW,PASS", True),
            "//SYSUDUMP DD  SYSOUT=*",
        ]
        at = part(rows, "//RGO      EXEC ")
        rows[at+2:at+2] = limit_dataset_dd(fmt, "OLD,DELETE", False)
    asm_steps = ("ASMA", "ASML", "ASMN", "ASMR", "ASMQ", "ASMG")
    link_steps = ("LKVR", "LKED") if writing else ("LKWR", "LKED")
    go_steps = ("WGO", "VGO") if writing else ("WGO", "RGO")
    for step in (*asm_steps, *link_steps, *go_steps):
        part(rows, f"//{step:<8} EXEC ")
    if (rows.count("//") != 1 or rows[-1] != "//" or
        rows.count("//SYSIN    DD  *") != 6 or
        rows.count("/*") != 8 or
        rows.count(" ENTRY R0APP") != 1 or
        rows.count("         BCXREQ BCPLQSAM") != 1 or
        rows.count(f" NAME {appname}(R)") != 1):
        raise ValueError("Q.3 limit native deck structure invalid")
    if any(len(row) > 71 or not row.isascii() or "\t" in row
           for row in rows):
        raise ValueError("Q.3 limit JCL/IFOX card width invalid")
    if any("CATLG" in row or "DISP=MOD" in row or
           (row.startswith("//") and "BOOT_DEVOBJ" in row)
           for row in rows):
        raise ValueError("Q.3 limit permanent MVS modification prohibited")
    for disposition, create in (("NEW,PASS", True),
                                ("OLD,DELETE", False)):
        block = limit_dataset_dd(fmt, disposition, create)
        at = part(rows, block[0])
        if rows[at:at+len(block)] != block:
            raise ValueError("Q.3 limit dataset lifecycle invalid")
    return "\n".join(rows) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="synthetic cards only; no credentials or JES")
    ap.add_argument("--write", action="store_true",
                    help="native BCPL WRITE and independent IFOX reader")
    ap.add_argument("--limit", choices=("v", "vb"),
                    help="1024-byte V/VB ceiling campaign")
    ap.add_argument("--generated", type=Path,
                    help="actual BCPL compiler CG370 output in workarea")
    args = ap.parse_args()
    q = query_helper()
    if args.check:
        if args.generated is not None:
            ap.error("--check and --generated are exclusive")
        source = q.time_helper().trailer_helper().sample_generated()
        if args.limit:
            job = limit_job(args.limit, args.write)
            deck = make_limit_deck(
                source, [f"//{job} JOB (BCPL),'Q3 CHECK',CLASS=A"],
                "HERC02.BCPL.BOOT.OBJ", args.limit, args.write)
        elif args.write:
            deck = make_write_deck(
                source, ["//Q3VWRIT JOB (BCPL),'Q3 CHECK',CLASS=A"],
                "HERC02.BCPL.BOOT.OBJ")
        else:
            deck = make_deck(
                source, ["//Q3VREAD JOB (BCPL),'Q3 CHECK',CLASS=A"],
                "HERC02.BCPL.BOOT.OBJ")
        print(f"PASS: Q3 {'WRITE' if args.write else 'READ'} synthetic "
              f"{len(deck.splitlines())} cards, 10 steps; no JES")
        return
    if args.generated is None:
        ap.error("--generated required for actual BCPL test")
    source_path = args.generated.resolve()
    if (ROOT / "workarea").resolve() not in source_path.parents:
        raise ValueError("CG370 source must be under ignored workarea")
    generated = source_path.read_bytes().decode("latin-1")
    core = q.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config["datasets"]["BOOT_OBJ"]
    if (spec.get("content_type") != "object" or
        spec.get("dsorg") != "PO" or
        spec.get("recfm") != "FB" or
        int(spec.get("lrecl", 0)) != 80):
        raise ValueError("manifest BOOT_OBJ must be an FB80 object PDS")
    job = (limit_job(args.limit, args.write) if args.limit
           else ("Q3VWRIT" if args.write else JOB))
    jobcard = core.authenticated_job_card(
        config, job, "QSAM Q3 LIMIT" if args.limit else "QSAM Q3 V",
        redact_password=False)
    obj = core.full_dsn(config, spec)
    if args.limit:
        deck = make_limit_deck(
            generated, jobcard, obj, args.limit, args.write)
    else:
        deck = (make_write_deck(generated, jobcard, obj) if args.write
                else make_deck(generated, jobcard, obj))
    WORK.mkdir(parents=True, exist_ok=True)
    dest = WORK / (
        f"{job.lower()}.jcl" if args.limit
        else ("q3vwrite.jcl" if args.write else "q3vread.jcl"))
    fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as out:
        out.write(deck)
    print(f"PREPARED ONLY: {dest} ({len(deck.splitlines())} cards)")
    print("No JES submission, object installation, or permanent datasets")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("Q.3 V READ preparation FAILED: " + str(exc))
