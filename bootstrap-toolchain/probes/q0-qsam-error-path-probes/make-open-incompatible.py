#!/usr/bin/env python3
"""Prepare an opt-in, disposable Q.0 MVS OPEN geometry-abend probe.

The job uses a deliberately incompatible output DCB. Its GO step may
terminate with S013; this is intentional diagnostic evidence, not PASS.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
JOB = "QS0BADOP"


def harness():
    spec = importlib.util.spec_from_file_location("q0_dasd_harness", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load established JCL harness: {BASE}")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def source():
    s = (HERE / "open-incompatible.asm").read_text(encoding="ascii")
    for line_no, card in enumerate(s.splitlines(), 1):
        if not card.isascii() or len(card) > 71 or card.startswith("//") or card == "/*":
            raise ValueError(f"invalid IFOX card {line_no}: {card!r}")
    if s.count("OPEN  (QDCB,(OUTPUT))") != 1 or "PUT   QDCB" in s:
        raise ValueError("unsafe or missing OPEN experiment")
    if "CLOSE (QDCB)" in s or "DSN=" in s:
        raise ValueError("OPEN test must not close a failed DCB or name data sets")
    return s.rstrip("\n")


def make_deck(card, parent):
    if not card[0].startswith(f"//{JOB}"):
        raise ValueError("wrong JOB card")
    cards = [
        *card,
        "//* TEST-ONLY: AN INVALID FB DCB MAY ABEND THIS GO STEP",
        "//* NO PRODUCTION PDS WRITES; ONLY DISPOSABLE TEMPORARY DASD",
        *parent.asm_step("ASM", "BADOBJ", source()),
        *parent.link_step("LKED", "BADOBJ", "BADMOD", "Q0BADMD", "Q0BADOP", "ASM"),
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASM),(0,NE,LKED))",
        "//QBAD     DD  DSN=&&Q0BAD,DISP=(NEW,DELETE),",
        "//             UNIT=SYSDA,SPACE=(TRK,(1,1)),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSUDUMP DD  SYSOUT=*",
        "//",
    ]
    for line_no, line in enumerate(cards, 1):
        if not line.isascii() or len(line) > 71:
            raise ValueError(f"invalid JCL card {line_no}: {line!r}")
    deck = "\n".join(cards) + "\n"
    if deck.count("//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)") != 1 or "DSN=&&Q0BAD" not in deck:
        raise ValueError("missing deliberately invalid disposable DD")
    if "DISP=(OLD" in deck.split("//GO       EXEC")[1] or "DISP=SHR" in deck.split("//GO       EXEC")[1]:
        raise ValueError("experiment may not use an existing dataset")
    return deck


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify source/JCL without credentials or file writes")
    parser.add_argument("--allow-open-abend", action="store_true",
                        help="acknowledge deliberate possibility of MVS S013")
    args = parser.parse_args()
    parent = harness()
    if args.check:
        card = [f"//{JOB} JOB (BCPL),'Q0 BAD OPEN',CLASS=A,MSGCLASS=A"]
    else:
        if not args.allow_open_abend:
            parser.error("writing the negative-OPEN job requires --allow-open-abend")
        config_tools = parent.config_module()
        config = config_tools.load_config()
        card = config_tools.authenticated_job_card(
            config, JOB, "Q0 BAD OPEN", redact_password=False)
    deck = make_deck(card, parent)
    if args.check:
        print(f"CHECK BADOPEN: IFOX/JCL source OK; {len(deck.splitlines())} cards; not submitted")
        return
    output = ROOT / "workarea/qsam-q0-error-path" / "q0-open-incompatible.jcl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deck, encoding="ascii", newline="\n")
    output.chmod(0o600)
    print(f"Q.0 incompatible OPEN JCL: {output}")
    print("WARNING: GO may ABEND (e.g. S013). Review JCL before submitting.")


if __name__ == "__main__":
    main()
