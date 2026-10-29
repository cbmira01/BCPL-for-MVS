#!/usr/bin/env python3
"""Prepare Q2QUERY native IFOX/IEWL/GO using established Q.1 BCX linkage.

The test checks QUERY opcode mask 31, QS_CAP_FIXED=1 and ABI edges.
Only temporary MVS objects and load modules; never submits a JES job.
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
WORK = ROOT / "workarea/bcplqsam-q2/query-capabilities"


def q1_query():
    path = HERE / "prepare-q1-query.py"
    spec = importlib.util.spec_from_file_location("q2_query_base", path)
    if spec is None or spec.loader is None:
        raise ValueError("Q.1 BCX/IEWL template unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_once(cards: list[str], old: str, new: str) -> None:
    if cards.count(old) != 1:
        raise ValueError("expected one Q.1 template card: " + old)
    cards[cards.index(old)] = new


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r"^//Q2QUERY\s+JOB\b", jobcard[0]):
        raise ValueError("authenticated Q2QUERY job card required")
    q = q1_query()
    rows = q.make_deck(
        generated, ["//Q1QUERY JOB (BCPL),'Q2 TEMPLATE',CLASS=A"], obj_dsn
    ).splitlines()
    rows[:1] = jobcard
    replace_once(
        rows, "//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES",
        "//* Q.2 CAPABILITY QUERY: NO QSAM OPEN/CLOSE OR PDS WRITES")
    replace_once(rows, " NAME Q1QUERY(R)", " NAME Q2QUERY(R)")
    replace_once(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),",
                 "//SYSLMOD  DD  DSN=&&Q2QLD(Q2QUERY),")
    if rows.count("         BCXREQ BCPLQSAM") != 1:
        raise ValueError("BCPLQSAM selection absent/duplicated")
    if rows.count(" NAME Q2QUERY(R)") != 1 or rows.count("//") != 1:
        raise ValueError("native Q2QUERY deck malformed")
    if len([r for r in rows if re.match(r"^//\w+\s+EXEC\b", r)]) != 7:
        raise ValueError("expected five IFOX, one IEWL, one GO")
    for n, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"invalid fixed JCL/IFOX card {n}")
        if "DISP=MOD" in row or "CATLG" in row:
            raise ValueError("permanent dataset operation prohibited")
    return "\n".join(rows) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--generated", type=Path)
    args = ap.parse_args()
    q = q1_query()
    if args.check:
        if args.generated:
            ap.error("--check takes no generated input")
        sample = q.time_helper().trailer_helper().sample_generated()
        deck = make_deck(
            sample, ["//Q2QUERY JOB (BCPL),'Q2 CHECK',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")
        print(f"PASS: Q2QUERY {len(deck.splitlines())} JCL cards")
        print("NO JES submission")
        return
    if args.generated is None:
        ap.error("--generated required for the native compiler output")
    generated = args.generated.resolve()
    if (ROOT / "workarea").resolve() not in generated.parents:
        raise ValueError("generated BCPL code must be under workarea")
    if not generated.is_file():
        raise ValueError("missing Cambridge compiler output")
    core = q.time_helper().trailer_helper().load_core()
    config = core.load_config()
    obj = config["datasets"]["BOOT_OBJ"]
    if (obj.get("content_type") != "object" or obj.get("dsorg") != "PO"
        or obj.get("recfm") != "FB" or int(obj.get("lrecl", 0)) != 80):
        raise ValueError("BOOT_OBJ manifest geometry mismatch")
    jobcard = core.authenticated_job_card(
        config, "Q2QUERY", "Q2 QUERY FIXED", redact_password=False)
    deck = make_deck(
        generated.read_bytes().decode("latin-1"), jobcard,
        core.full_dsn(config, obj))
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / "q2query.jcl"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as out:
        out.write(deck)
    print(f"PREPARED Q2QUERY: {len(deck.splitlines())} cards")
    print("SHA-256: " + hashlib.sha256(deck.encode("ascii")).hexdigest())
    print("NO JES submission or permanent MVS dataset writes")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("Q2QUERY preparation failed: " + str(exc))
