#!/usr/bin/env python3
"""Prepare Q.0 read-only RDJFCB DD allocation inquiry (no unsafe OPEN)."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
JOBNAME = "QS0DDCHK"


def parent_module():
    spec = importlib.util.spec_from_file_location("q0_dasd_jcl", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing proven DASD probe harness: {PARENT}")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    return parent


def assembler_source() -> str:
    source = (HERE / "dd-inquiry.asm").read_text(encoding="ascii")
    for num, card in enumerate(source.splitlines(), 1):
        if not card.isascii() or len(card) > 71 or card.startswith("//") or card == "/*":
            raise ValueError(f"invalid IFOX source card {num}: {card!r}")
    if source.count("RDJFCB ((2))") != 2:
        raise ValueError("both non-opening DD inquiries are required")
    if "OPEN  (PDCB" in source or "OPEN  (MDCB" in source:
        raise ValueError("forbidden: probe must not OPEN the inquiry DCBs")
    if "Q0 DD RDJFCB PRESENT=0 MISSING=4 PASS" not in source:
        raise ValueError("missing expected success marker")
    return source.rstrip("\n")


def make_deck(jobcard: list[str]) -> str:
    parent = parent_module()
    if not jobcard or not jobcard[0].startswith("//" + JOBNAME):
        raise ValueError("wrong job name")
    cards = [
        *jobcard,
        "//* MILESTONE QSAM Q.0 - NON-OPENING DD ALLOCATION INQUIRY",
        "//* QPRES IS ALLOCATED; QMISS HAS NO DD STATEMENT",
        "//* TEST-ONLY, NO PDS WRITES OR NATIVE RUNTIME CHANGES",
        *parent.asm_step("ASM", "DDOBJ", assembler_source()),
        *parent.link_step("LKED", "DDOBJ", "DDMOD", "Q0DDMOD", "Q0DDCK", "ASM"),
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASM),(0,NE,LKED))",
        "//QPRES    DD  DSN=&&Q0PRES,DISP=(NEW,DELETE),",
        "//             UNIT=SYSDA,SPACE=(TRK,(1,1)),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//QOUT     DD  SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for num, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"invalid JCL card {num}: {card!r}")
    deck = "\n".join(cards) + "\n"
    if "//QMISS " in deck or "//QMISS\n" in deck:
        raise ValueError("QMISS must remain unallocated")
    if "//QPRES    DD  DSN=&&Q0PRES" not in deck:
        raise ValueError("positive-control DD is absent")
    if deck.count("RDJFCB ((2))") != 2:
        raise ValueError("missing two independent RDJFCB calls")
    return deck


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="source/JCL validation only; no credentials or file output")
    args = parser.parse_args()
    if args.check:
        jobcard = [f"//{JOBNAME} JOB (BCPL),'Q0 DD CHECK',CLASS=A,MSGCLASS=A"]
    else:
        parent = parent_module()
        core = parent.config_module()
        conf = core.load_config()
        jobcard = core.authenticated_job_card(conf, JOBNAME, "Q0 DD CHECK",
                                               redact_password=False)
    deck = make_deck(jobcard)
    if args.check:
        print(f"CHECK DDINQ: source/JCL OK; {len(deck.splitlines())} cards; no JCL written")
        return
    out = ROOT / "workarea/qsam-q0-error-path" / "q0-dd-inquiry.jcl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(deck, encoding="ascii", newline="\n")
    out.chmod(0o600)
    print(f"Q.0 DD inquiry JCL: {out}")


if __name__ == "__main__":
    main()
