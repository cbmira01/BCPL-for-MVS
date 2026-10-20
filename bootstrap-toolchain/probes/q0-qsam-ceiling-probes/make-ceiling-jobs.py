#!/usr/bin/env python3
"""Build isolated Q.0 1024-byte candidate-stage MVS probe jobs."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
PROFILES = {
    "v": ("QS0C102V", "V", "40", 1028, "Q0 V1024 RDW4/16/1024 BINARY 15 PASS"),
    "vb": ("QS0C10VB", "VB", "50", 2052, "Q0 VB1024 RDW4/16/1024 BINARY 15 PASS"),
    "stage16": ("QS0S16", None, None, None,
                "Q0 16 STAGES 1024 GETMAIN FREEMAIN PASS"),
}


def harness():
    spec = importlib.util.spec_from_file_location("q0_ceiling_base", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"existing Q.0 JCL harness missing: {PARENT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source(name: str) -> str:
    data = (HERE / name).read_text(encoding="ascii")
    for i, card in enumerate(data.splitlines(), 1):
        if len(card) > 71 or not card.isascii() or card.startswith("//") or card == "/*":
            raise ValueError(f"bad IFOX source card {name}:{i}: {card!r}")
    return data.rstrip("\n")


def variable_reader(profile: str) -> str:
    _, _, fmt, blksize, pass_message = PROFILES[profile]
    data = source("variable-reader.asm")
    substitutions = {
        "CLI   QDCB+36,CINFMT": f"CLI   QDCB+36,X'{fmt}'",
        "CLC   QDCB+62(2),CINBLK": f"CLC   QDCB+62(2),=H'{blksize}'",
        "PASSREC  DC    CL80'CINPASS'": f"PASSREC  DC    CL80'{pass_message}'",
    }
    for old, new in substitutions.items():
        if data.count(old) != 1:
            raise ValueError(f"bad Q.0 template substitution {old!r}")
        data = data.replace(old, new)
    for i, card in enumerate(data.splitlines(), 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"bad generated IFOX card {i}: {card!r}")
    return data


def make_deck(profile: str, jobcard: list[str]) -> str:
    if profile not in PROFILES:
        raise ValueError(f"unknown Q.0 ceiling profile {profile!r}")
    job, recfm, _, blksize, marker = PROFILES[profile]
    if not jobcard or not jobcard[0].startswith(f"//{job} JOB "):
        raise ValueError("unexpected JOB card")
    base = harness()
    if profile == "stage16":
        cards = [
            *jobcard,
            "//* Q.0 TEST ONLY: 16 LIVE 1024-BYTE AREAS; NOT 16 DCBS",
            "//* NO PERMANENT DATA SETS OR ACCEPTED PDS OBJECTS",
            *base.asm_step("ASM", "S16OBJ", source("stage16.asm")),
            *base.link_step("LKED", "S16OBJ", "S16MOD", "Q0S16MOD", "Q0S16", "ASM"),
            "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
            "//             TIME=(,1),COND=((0,NE,ASM),(0,NE,LKED))",
            "//QOUT     DD  SYSOUT=*,",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSUDUMP DD  SYSOUT=*",
            "//",
        ]
    else:
        cards = [
            *jobcard,
            "//* Q.0 TEST ONLY: 1024-BYTE V/VB LOGICAL RECORD BOUNDARY",
            "//* 5 EMPTY RDW-ONLY, 5 SHORT, 5 FULL WITH BINARY BYTES",
            *base.asm_step("ASMWR", "CWR0OBJ", source("variable-writer.asm")),
            *base.asm_step("ASMRD", "CRD0OBJ", variable_reader(profile)),
            *base.link_step("LKWR", "CWR0OBJ", "CWRMOD", "Q0CWRMOD", "Q0CVW", "ASMWR"),
            *base.link_step("LKRD", "CRD0OBJ", "CRDMOD", "Q0CRDMOD", "Q0CVR", "ASMRD"),
            "//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,",
            "//             TIME=(,1),COND=((0,NE,ASMWR),(0,NE,LKWR))",
            "//QDISK    DD  DSN=&&Q0CEIL,DISP=(NEW,PASS),",
            "//             UNIT=SYSDA,SPACE=(TRK,(2,1)),",
            f"//             DCB=(RECFM={recfm},LRECL=1024,BLKSIZE={blksize})",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSUDUMP DD  SYSOUT=*",
            "//RGO      EXEC PGM=*.LKRD.SYSLMOD,REGION=256K,",
            "//             TIME=(,1),COND=((0,NE,WGO),(0,NE,LKRD))",
            "//QDISK    DD  DSN=&&Q0CEIL,DISP=(OLD,DELETE)",
            "//QOUT     DD  SYSOUT=*,",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSUDUMP DD  SYSOUT=*",
            "//",
        ]
    if not any(marker in card for card in cards):
        raise ValueError("missing expected probe marker")
    if profile != "stage16":
        required = [
            "GET   QDCB,AREA", "PUT   QDCB,AREA", "EODAD=ATEND",
            "AREA     DS    CL1024", "CH    2,=H'1024'",
            "CLC   AREA+512(255),BLANKS", "CLI   AREA+1023,X'00'",
            "DSN=&&Q0CEIL,DISP=(OLD,DELETE)",
        ]
        for needle in required:
            if needle not in "\n".join(cards):
                raise ValueError(f"missing V/VB size-boundary test: {needle}")
        if cards.count("//QDISK    DD  DSN=&&Q0CEIL,DISP=(OLD,DELETE)") != 1:
            raise ValueError("missing temporary QSAM input DELETE")
    else:
        if sum("GETMAIN RC,LV=1024" in card for card in cards) != 1:
            raise ValueError("expected one loop GETMAIN RC site")
        if any(card.startswith("//QDISK ") for card in cards):
            raise ValueError("stage16 must not have QSAM data sets")
    for i, card in enumerate(cards, 1):
        if len(card) > 71 or not card.isascii():
            raise ValueError(f"invalid JCL card {i}: {card!r}")
    return "\n".join(cards) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("--check", action="store_true", help="validate without credentials/files")
    args = parser.parse_args()
    jobname = PROFILES[args.profile][0]
    if args.check:
        card = [f"//{jobname} JOB (BCPL),'Q0 LIMIT',CLASS=A,MSGCLASS=A"]
    else:
        core = harness().config_module()
        settings = core.load_config()
        card = core.authenticated_job_card(settings, jobname, "Q0 LIMIT", redact_password=False)
    output = make_deck(args.profile, card)
    if args.check:
        print(f"CHECK Q0 {args.profile.upper()}: {len(output.splitlines())} cards; no file written")
        return
    path = ROOT / "workarea/qsam-q0-ceiling" / f"q0-ceiling-{args.profile}.jcl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="ascii", newline="\n")
    path.chmod(0o600)
    print(f"Q.0 candidate stage ceiling JCL: {path}")


if __name__ == "__main__":
    main()
