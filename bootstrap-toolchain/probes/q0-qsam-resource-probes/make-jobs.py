#!/usr/bin/env python3
"""Generate an isolated Q.0 checked-storage and rollback experiment."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
JOB = "QS0RES"


def base_harness():
    spec = importlib.util.spec_from_file_location("q0_dasd_harness", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing Q.0 DASD harness: {PARENT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assembler_source() -> str:
    s = (HERE / "resource.asm").read_text(encoding="ascii")
    for n, card in enumerate(s.splitlines(), 1):
        if len(card) > 71 or not card.isascii() or card.startswith("//") or card == "/*":
            raise ValueError(f"invalid IFOX card {n}: {card!r}")
    if s.count("GETMAIN RC,LV=") != 3:
        raise ValueError("expected three real, conditional GETMAIN sites")
    if s.count("FREEMAIN R,LV=") != 6:
        raise ValueError("expected success and failure cleanup paths")
    if "LA    15,8" not in s or "NOT A REAL MVS SHORTAGE" not in s:
        raise ValueError("missing explicit deterministic injection")
    return s.rstrip("\n")


def make_deck(jobcard: list[str]) -> str:
    if not jobcard or not jobcard[0].startswith("//" + JOB):
        raise ValueError("unexpected job card")
    base = base_harness()
    cards = [
        *jobcard,
        "//* Q.0 TEST-ONLY CHECKED GETMAIN RC, INJECTED ROLLBACK",
        "//* NO MVS STORAGE EXHAUSTION; NO PRODUCTION PDS WRITES",
        *base.asm_step("ASM", "RESOBJ", assembler_source()),
        *base.link_step("LKED", "RESOBJ", "RESMOD", "Q0RESMOD",
                        "Q0RES", "ASM"),
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASM),(0,NE,LKED))",
        "//QOUT     DD  SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for n, c in enumerate(cards, 1):
        if not c.isascii() or len(c) > 71:
            raise ValueError(f"invalid JCL card {n}: {c!r}")
    deck = "\n".join(cards) + "\n"
    if deck.count("//SYSIN    DD  *") != 1 or cards.count("/*") != 2:
        raise ValueError("unexpected in-stream assembler/link editor sections")
    if "DSN=HERC" in deck or "DISP=OLD" in deck:
        raise ValueError("permanent dataset in test deck")
    if "Q0 GETMAIN RC ROLLBACK 3 ALLOC 3 FREE PASS" not in deck:
        raise ValueError("missing success marker")
    return deck


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate syntax and structure, do not write JCL")
    args = parser.parse_args()
    if args.check:
        jobcard = [f"//{JOB} JOB (BCPL),'Q0 RESOURCE',CLASS=A,MSGCLASS=A"]
    else:
        base = base_harness()
        config = base.config_module()
        settings = config.load_config()
        jobcard = config.authenticated_job_card(
            settings, JOB, "Q0 RESOURCE", redact_password=False)
    deck = make_deck(jobcard)
    if args.check:
        print(f"CHECK RESOURCE: {len(deck.splitlines())} cards; no JCL written")
        return
    out = ROOT / "workarea/qsam-q0-resource" / "q0-resource.jcl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(deck, encoding="ascii", newline="\n")
    out.chmod(0o600)
    print(f"Q.0 resource JCL: {out}")


if __name__ == "__main__":
    main()
