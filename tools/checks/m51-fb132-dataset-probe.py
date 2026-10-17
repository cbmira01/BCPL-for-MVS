#!/usr/bin/env python3
"""Prepare (never submit) an isolated M5.1.2 FB132 MVS QSAM readback job.

Takes existing regression 124 DEVOBJ/BCPLM6 runtime-pds-go.jcl and
redirects only its GO REPORT/REPORT2 to distinct temporary FB132
datasets. Adds IFOX+IEWL+independent QSAM GET/CLC verifier VCHK.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "native-compiler/regression/124-dynamic-dd-selected-output"
WORK = ROOT / "workarea/native-regression/124-dynamic-dd-selected-output"
SOURCE = WORK / "runtime-pds-go.jcl"
TARGET = WORK / "m51-fb132-dataset-v2.jcl"
ASM = WORK / "m51-fb132-verifier-v2.asm"
META = WORK / "m51-fb132-dataset-v2.json"
JOB = "M5D124B"
ENTRY = "M5V124"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verifier(records1, records2):
    if records1 != ["BCPL REPORT A", "BCPL REPORT B"] or (
            records2 != ["BCPL REPORT2 PART"]):
        raise ValueError("regression 124 immutable record fixtures drifted")
    lines = [
        f"{ENTRY}   CSECT",
        "         STM   14,12,12(13)",
        "         LR    12,15",
        f"         USING {ENTRY},12",
        "         ST    13,OLDSAVE+4",
        "         LA    13,NEWSAVE",
        "         MVI   N1,X'00'",
        "         MVI   N2,X'00'",
        "         OPEN  (DCB1,(INPUT))",
        "         OPEN  (DCB2,(INPUT))",
        "         GET   DCB1,BUF1",
        "         CLC   BUF1(132),EXP11",
        "         BNE   BAD",
        "         MVI   N1,X'01'",
        "         GET   DCB1,BUF1",
        "         CLC   BUF1(132),EXP12",
        "         BNE   BAD",
        "         MVI   N1,X'02'",
        "         GET   DCB1,BUF1",
        "         B     BAD",
        "EOD1     CLI   N1,X'02'",
        "         BNE   BAD",
        "         GET   DCB2,BUF2",
        "         CLC   BUF2(132),EXP21",
        "         BNE   BAD",
        "         MVI   N2,X'01'",
        "         GET   DCB2,BUF2",
        "         B     BAD",
        "EOD2     CLI   N2,X'01'",
        "         BNE   BAD",
        "         CLOSE (DCB1)",
        "         CLOSE (DCB2)",
        "GOOD     L     13,OLDSAVE+4",
        "         LM    14,12,12(13)",
        "         SR    15,15",
        "         BR    14",
        "BAD      CLOSE (DCB1)",
        "         CLOSE (DCB2)",
        "         L     13,OLDSAVE+4",
        "         LM    14,12,12(13)",
        "         LA    15,12",
        "         BR    14",
        "         LTORG",
        "         DS    0F",
        "OLDSAVE  DS    18F",
        "NEWSAVE  DS    18F",
        "N1       DC    X'00'",
        "N2       DC    X'00'",
        "         DS    0F",
        "BUF1     DS    CL132",
        "BUF2     DS    CL132",
        "DCB1     DCB   DDNAME=REPORT,DSORG=PS,MACRF=GM,EODAD=EOD1",
        "DCB2     DCB   DDNAME=REPORT2,DSORG=PS,MACRF=GM,EODAD=EOD2",
        f"EXP11    DC    CL132'{records1[0]}'",
        f"EXP12    DC    CL132'{records1[1]}'",
        f"EXP21    DC    CL132'{records2[0]}'",
        f"         END   {ENTRY}",
    ]
    if any(len(x) > 71 for x in lines):
        raise ValueError("IFOX source exceeds column 71")
    return "\n".join(lines) + "\n"


def transform(deck, asm):
    checks = {
        "regression 124 JOB": len(re.findall(
            r"^//RG124R\s+JOB\b", deck, re.M)) == 1,
        "DEVOBJ candidate": (
            "RUNTIME LIBRARY: DEVOBJ; APP ASSEMBLY ONLY" in deck
            and "D3 BCPLMAIN+BCPLIO CANDIDATE: 1" in deck),
        "BCPLM6": deck.count(" INCLUDE OBJ(BCPLM6)") == 1,
        "BCPLIO": deck.count(" INCLUDE OBJ(BCPLIO)") == 1,
        "GO": len(re.findall(r"^//GO\s+EXEC\b", deck, re.M)) == 1,
        "end": deck.endswith("\n//\n"),
    }
    bad = [key for key, ok in checks.items() if not ok]
    if bad:
        raise ValueError("invalid candidate source deck: " + ", ".join(bad))
    deck = re.sub(r"^//RG124R(?=\s+JOB\b)", f"//{JOB}",
                  deck, count=1, flags=re.M)
    for dd, dsn in (("REPORT", "M5RPT1"), ("REPORT2", "M5RPT2")):
        pat = (rf"^//{dd}\s+DD SYSOUT=\*,"
               r"DCB=\(RECFM=FB,LRECL=132,BLKSIZE=132\)$")
        replacement = "\n".join([
            f"//{dd:<8} DD DSN=&&{dsn},UNIT=SYSDA,",
            "//             SPACE=(TRK,(1,1)),DISP=(NEW,PASS),",
            "//             DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        ])
        deck, count = re.subn(pat, lambda _: replacement, deck,
                              count=1, flags=re.M)
        if count != 1:
            raise ValueError(f"missing expected GO {dd} SYSOUT layout")
    tail = [
        "//VASM     EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        "//SYSGO    DD DSN=&&M5VOBJ,UNIT=SYSDA,",
        "//             SPACE=(80,(100,20)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD *",
        *asm.rstrip().splitlines(),
        "/*",
        "//VLINK    EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
        "//             COND=(0,NE,VASM)",
        "//SYSLIN   DD DSN=&&M5VOBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        f" ENTRY {ENTRY}",
        f" NAME {ENTRY}(R)",
        "/*",
        f"//SYSLMOD  DD DSN=&&M5VLD({ENTRY}),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//VCHK     EXEC PGM=*.VLINK.SYSLMOD,",
        "//             COND=((0,NE,GO),(0,NE,VASM),(0,NE,VLINK))",
        "//REPORT   DD DSN=&&M5RPT1,DISP=(OLD,DELETE)",
        "//REPORT2  DD DSN=&&M5RPT2,DISP=(OLD,DELETE)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    result = deck[:-3] + "\n".join(tail) + "\n"
    if any(len(line) > 71 for line in result.splitlines()):
        raise ValueError("generated deck exceeds column 71")
    if result.count("DSN=&&M5RPT1") != 2 or (
            result.count("DSN=&&M5RPT2") != 2):
        raise ValueError("dataset writer/reader linkage changed")
    return result


def prepare():
    # Preserve first-stage v1 files as historical evidence; stage v2 separately.
    if any(path.exists() for path in (TARGET, ASM, META)):
        raise ValueError("previous M5.1.2 artifacts exist; refusing overwrite")
    if not SOURCE.exists():
        raise ValueError("regression 124 DEVOBJ runtime-pds-go.jcl missing; "
                         "do not submit MVS jobs implicitly")
    a = (CASE / "expected-report.txt").read_text(encoding="ascii").splitlines()
    b = (CASE / "expected-report2.txt").read_text(encoding="ascii").splitlines()
    asm = verifier(a, b)
    deck = transform(SOURCE.read_text(encoding="ascii"), asm)
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    WORK.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deck, encoding="ascii", newline="\n")
    ASM.write_text(asm, encoding="ascii", newline="\n")
    meta = {
        "schema": "m51-dataset-readback-v2",
        "git_sha": rev.stdout.strip(),
        "job": JOB, "writer": "GO", "verifier": "VCHK",
        "source_sha256": sha(SOURCE), "deck_sha256": sha(TARGET),
        "asm_sha256": sha(ASM),
        "report_fixture_sha256": sha(CASE / "expected-report.txt"),
        "report2_fixture_sha256": sha(CASE / "expected-report2.txt"),
        "claimed": "QSAM temporary dataset bytes IF verified",
        "not_claimed": "original JES2 SYSOUT spool record bytes",
        "state": "PREPARED_NOT_EXECUTED",
    }
    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print("M5.1.2 corrected v2 PREPARED; no MVS job submitted")
    for path in (TARGET, ASM, META):
        print("  " + str(path.relative_to(ROOT)))
    print("Inspect assembler and JCL before any manual submission.")


if __name__ == "__main__":
    try:
        if sys.argv[1:] != ["prepare"]:
            raise ValueError("usage: m51-fb132-dataset-probe.py prepare")
        prepare()
    except (OSError, ValueError, UnicodeError,
            subprocess.CalledProcessError) as exc:
        sys.exit(f"m51-fb132-dataset-probe: {exc}")
