#!/usr/bin/env python3
"""Generate read-only R.0 application/installed-BLIB trailer inspection JCL."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "workarea/runtime-extensions-r0-trailers"
JOB = "R0TRAIL"
APP = "R0APP"


def load_core():
    path = ROOT / "tools/datasets/dspal-core.py"
    spec = importlib.util.spec_from_file_location("r0trailer_core", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"missing dspal implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_asm(text: str, name: str) -> list[str]:
    rows = text.rstrip("\n").splitlines()
    if not rows:
        raise ValueError(f"{name}: empty assembler source")
    for number, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"{name}:{number}: invalid IFOX card {row!r}")
        if row == "/*" or row.startswith("//"):
            raise ValueError(f"{name}:{number}: unexpected JCL delimiter")
    return rows


def application_source(source: str) -> list[str]:
    # Mirrors only the narrow, proven native-regression CSECT adapter.
    source = "".join(ch if ord(ch) < 128 else "?" for ch in source)
    rows = checked_asm(source, "CG370 application")
    cs = [i for i, row in enumerate(rows) if re.fullmatch(r"\s*CSECT\s*", row)]
    extern = [i for i, row in enumerate(rows)
              if re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", row)]
    ends = [i for i, row in enumerate(rows)
            if re.fullmatch(r"\s*END(?:\s+.*)?", row)]
    if len(cs) != 1 or len(extern) != 1 or len(ends) != 1:
        raise ValueError("require one unnamed CSECT, EXTRN BCPLMAIN, END")
    if not any(re.fullmatch(r"L998\s+.*", row) for row in rows):
        raise ValueError("missing CG370 L998 end marker")
    if not cs[0] < ends[0] or cs[0] > extern[0]:
        raise ValueError("unexpected CG370 source organization")
    rows[cs[0]] = "R0APP    CSECT"
    rows.insert(cs[0] + 1, "         ENTRY R0APP")
    rows[ends[0] + 1] = "         END   R0APP"
    # The separately assembled installed BLIB is never recompiled here.
    return checked_asm("\n".join(rows), "renamed CG370 application")


def asm_step(name: str, obj: str, rows: list[str]) -> list[str]:
    return [
        f"//{name:<8} EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSPUNCH DD  DUMMY",
        f"//SYSGO    DD  DSN=&&{obj},UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD  *", *rows, "/*",
    ]


def make_deck(jobcard: list[str], observer: str, generated: str,
              obj_dsn: str) -> str:
    if not jobcard or jobcard[0].split()[:2] != ["//R0TRAIL", "JOB"]:
        raise ValueError("R0TRAIL authenticated JOB card required")
    cards = [*jobcard,
             "//* R.0 READ-ONLY EXPORT EVIDENCE: NO PDS UPDATES",
             "//* R0APP AND INSTALLED BOOT_OBJ(BLIB) ARE NEVER EXECUTED"]
    cards += asm_step("ASMT", "R0TOBJ", checked_asm(observer, "observer"))
    cards += asm_step("ASMA", "R0AOBJ", application_source(generated))
    cards += [
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=((0,NE,ASMT),(0,NE,ASMA))",
        f"//OBJ      DD  DSN={obj_dsn},DISP=SHR",
        "//SYSLIN   DD  DSN=&&R0TOBJ,DISP=(OLD,DELETE)",
        "//         DD  DSN=&&R0AOBJ,DISP=(OLD,DELETE)",
        "//         DD  *",
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(BCPLIO)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY R0TRACE",
        " NAME R0TRAIL(R)",
        "/*",
        "//SYSLMOD  DD  DSN=&&R0LOAD(R0TRAIL),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE,LKED)",
        "//QOUT     DD  SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for i, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"JCL card {i} invalid ({len(row)}): {row!r}")
    if cards.count("/*") != 3:
        raise ValueError("expected two source and one IEWL stream")
    if "//SYSUT2   DD  DSN=" in "\n".join(cards):
        raise ValueError("unexpected permanent output dataset")
    return "\n".join(cards) + "\n"


def sample_generated() -> str:
    return "\n".join([
        "         CSECT", "         EXTRN BCPLMAIN",
        "L999     STM   14,12,12(13)",
        "         BCR   15,4", "         DC    AL2(L998-L999)",
        "         DC    A(BCPLMAIN)",
        "         DC    F'2796'", "         DC    F'0'",
        "         DC    F'4'", "         DC    A(L999)",
        "L998     EQU   *", "         END", "",
    ])


def run() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generated", type=Path,
                   help="saved assembler from tools/bootstrap/compile-mvs")
    p.add_argument("--check", action="store_true",
                   help="offline check, synthetic data if no --generated")
    a = p.parse_args()
    if not a.check and a.generated is None:
        p.error("--generated is required outside --check")
    if a.generated is not None:
        generated = a.generated.read_bytes().decode("latin-1")
    else:
        generated = sample_generated()
    observer = (HERE / "trailer-observer.asm").read_text("ascii")
    if a.check:
        jobcard = ["//R0TRAIL JOB (BCPL),'R0 TRAILER',CLASS=A,MSGCLASS=A"]
        obj_dsn = "HERC02.BCPL.BOOT.OBJ"  # validation only
    else:
        core = load_core()
        config = core.load_config()
        spec = config["datasets"]["BOOT_OBJ"]
        if not (spec.get("content_type") == "object" and
                spec.get("recfm") == "FB" and
                int(spec.get("lrecl", 0)) == 80 and
                spec.get("dsorg") == "PO"):
            raise ValueError("BOOT_OBJ must be a binary FB80 object PDS")
        obj_dsn = core.full_dsn(config, spec)
        jobcard = core.authenticated_job_card(
            config, JOB, "R0 TRAILER EVIDENCE", redact_password=False)
    deck = make_deck(jobcard, observer, generated, obj_dsn)
    digest = hashlib.sha256(generated.encode("latin-1")).hexdigest()
    if a.check:
        print(f"CHECK: R.0 trailer job {len(deck.splitlines())} cards; "
              f"input SHA256 {digest}; no JCL written")
        return
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / "r0-trailer.jcl"
    out.write_text(deck, encoding="ascii", newline="\n")
    out.chmod(0o600)
    (WORK / "generated-sha256.txt").write_text(digest + "\n", "ascii")
    print(f"Generated test-only JCL: {out}")
    print(f"CG370 assembler SHA256: {digest}")


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f"R.0 trailer generator failed: {exc}")
