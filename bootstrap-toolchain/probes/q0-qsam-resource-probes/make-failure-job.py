#!/usr/bin/env python3
"""Build the isolated Q.0 rollback-handler (not real shortage) MVS job."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
JOB = "QS0FAIL"


def harness():
    spec = importlib.util.spec_from_file_location("q0_dasd_base", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing established MVS JCL harness: {PARENT}")
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    return base


def assembler_source():
    source = (HERE / "failure-path.asm").read_text(encoding="ascii")
    for lineno, card in enumerate(source.splitlines(), 1):
        if len(card) > 71 or not card.isascii() or card.startswith("//") or card == "/*":
            raise ValueError(f"invalid IFOX card {lineno}: {card!r}")
    required = {
        "GETMAIN RC,LV=": 4,
        "FREEMAIN R,LV=": 8,
        "BNZ   ROLLBACK": 3,
        "BAL   7,ACQUIRE": 4,
        "BAL   7,RELEASE": 8,
        "MVI   INJECT,X'01'": 1,
        "ROLLBACK L": 1,
        "Q0 RESOURCE FAILED PATH 4 ALLOC 4 FREE PASS": 1,
    }
    for needle, expected_count in required.items():
        actual = source.count(needle)
        if actual != expected_count:
            raise ValueError(f"{needle!r}: expected {expected_count}, found {actual}")
    if "QDCB" in source or "GET   " in source or "PUT   QDCB" in source:
        raise ValueError("test must not touch a QSAM input/output dataset")
    return source.rstrip("\n")


def make_deck(jobcard):
    if not jobcard or not jobcard[0].startswith("//" + JOB):
        raise ValueError("unexpected JOB card")
    base = harness()
    cards = [
        *jobcard,
        "//* Q.0 TEST ONLY: ACTUAL ROLLBACK HANDLER; INJECTED FAILURE",
        "//* FOUR SMALL GETMAIN CALLS, NO OOM, NO PRODUCTION PDS",
        *base.asm_step("ASM", "FALOBJ", assembler_source()),
        *base.link_step("LKED", "FALOBJ", "FALMOD", "Q0FALMOD",
                        "Q0FAIL", "ASM"),
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASM),(0,NE,LKED))",
        "//QOUT     DD  SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for lineno, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"invalid JCL card {lineno}: {card!r}")
    deck = "\n".join(cards) + "\n"
    if cards.count("/*") != 2 or deck.count("//SYSIN    DD  *") != 1:
        raise ValueError("invalid in-stream assembler/link-editor data")
    if "DISP=SHR" in deck.split("//GO       EXEC")[1] or "DSN=" in deck.split("//GO       EXEC")[1]:
        raise ValueError("GO step must not have physical data sets")
    return deck


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate locally; no credentials or deck written")
    args = parser.parse_args()
    if args.check:
        jobcard = [f"//{JOB} JOB (BCPL),'Q0 FAILED PATH',CLASS=A,MSGCLASS=A"]
    else:
        parent = harness()
        config = parent.config_module()
        settings = config.load_config()
        jobcard = config.authenticated_job_card(
            settings, JOB, "Q0 FAILED PATH", redact_password=False)
    deck = make_deck(jobcard)
    if args.check:
        print(f"CHECK FAILED PATH: {len(deck.splitlines())} cards; source/JCL OK; no deck written")
        return
    path = ROOT / "workarea/qsam-q0-resource" / "q0-failure-path.jcl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(deck, encoding="ascii", newline="\n")
    path.chmod(0o600)
    print(f"Q.0 failure-handler JCL: {path}")


if __name__ == "__main__":
    main()
