#!/usr/bin/env python3
"""Prepare Q.0 test-only post-OPEN DCB INFO probes (V and VB)."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / "q0-qsam-dasd-probes" / "make-jobs.py"
PROFILES = {
    "v": ("QS0INFV", "40", 104, 3, "V"),
    "vb": ("QS0INFVB", "50", 404, 4, "VB"),
}


def harness():
    spec = importlib.util.spec_from_file_location("qsam_q0_dasd", PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"existing Q.0 DASD harness missing: {PARENT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reader_with_open_info(base_reader: str, profile: str) -> str:
    _, recfm, blksize, enum_value, caption = PROFILES[profile]
    before = "         CLC   QDCB+82(2),=H'100'\n         BNE   FAILED\nRLOOP    GET"
    if base_reader.count(before) != 1:
        raise ValueError("unrecognized existing Q.0 V/VB reader baseline")
    # After OPEN, compare the effective DCB attributes (not just JCL).
    # The raw DCB field is translated to the proposed public enum here,
    # but neither QSAMSVC nor a BCPL INFO vector is implemented.
    insert = (
        "         CLC   QDCB+82(2),=H'100'\n"
        "         BNE   FAILED\n"
        f"         CLI   QDCB+36,X'{recfm}'\n"
        "         BNE   FAILED\n"
        f"         CLC   QDCB+62(2),=H'{blksize}'\n"
        "         BNE   FAILED\n"
        "* MAP THE EFFECTIVE DCB FORMAT BYTE TO PUBLIC FORMAT ENUM.\n"
        "         CLI   QDCB+36,X'40'\n"
        "         BE    INFOV\n"
        "         CLI   QDCB+36,X'50'\n"
        "         BE    INFOVB\n"
        "         B     FAILED\n"
        "INFOV    LA    4,3\n"
        "         B     INFOMAP\n"
        "INFOVB   LA    4,4\n"
        f"INFOMAP  C     4,=F'{enum_value}'\n"
        "         BNE   FAILED\n"
        "* V/VB DATA MAX = EFFECTIVE LRECL MINUS FOUR RDW BYTES.\n"
        "         LH    5,QDCB+82\n"
        "         SH    5,=H'4'\n"
        "         CH    5,=H'96'\n"
        "         BNE   FAILED\n"
        "RLOOP    GET"
    )
    result = base_reader.replace(before, insert)
    previous = "PASSREC  DC    CL80'Q0 VARIABLE 15 RECORDS PASS'"
    expected = f"Q0 INFO {caption} OPEN DCB ENUM{enum_value} DATA96 PASS"
    if result.count(previous) != 1:
        raise ValueError("unexpected Q.0 existing reader marker")
    result = result.replace(previous, f"PASSREC  DC    CL80'{expected}'")
    for lineno, card in enumerate(result.splitlines(), 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f"bad generated IFOX card {lineno}: {card!r}")
    return result


def deck(profile: str, jobcard: list[str]) -> str:
    if profile not in PROFILES:
        raise ValueError(f"unknown INFO profile: {profile}")
    job, _, block, _, _ = PROFILES[profile]
    if not jobcard or not jobcard[0].startswith("//" + job):
        raise ValueError("wrong INFO job name")
    base = harness()
    original_source = base.asm_source
    def modified(name: str) -> str:
        raw = original_source(name)
        if name == "v-read.asm":
            return reader_with_open_info(raw, profile)
        return raw
    base.asm_source = modified
    base.PROFILES[profile] = (job, "v-write.asm", "v-read.asm", "Q0VW", "Q0VR", profile.upper(), 100, block)
    output = base.make_deck(profile, jobcard)
    for needle in (
        "CLC   QDCB+82(2),=H'100'",
        f"CLC   QDCB+62(2),=H'{block}'",
        "CLI   QDCB+36,X'40'",
        "CLI   QDCB+36,X'50'",
        "SH    5,=H'4'",
        "CH    5,=H'96'",
        "RLOOP    GET   QDCB,AREA",
        "DSN=&&Q0DISK,DISP=(OLD,DELETE)",
    ):
        if needle not in output:
            raise ValueError("missing required INFO check: " + needle)
    if output.count("GET   QDCB,AREA") != 1:
        raise ValueError("unexpected GET sites")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("--check", action="store_true",
                        help="no credentials, no files, just source/JCL checks")
    args = parser.parse_args()
    job = PROFILES[args.profile][0]
    if args.check:
        jobcard = [f"//{job} JOB (BCPL),'Q0 INFO',CLASS=A,MSGCLASS=A"]
    else:
        core = harness().config_module()
        config = core.load_config()
        jobcard = core.authenticated_job_card(
            config, job, "Q0 INFO", redact_password=False)
    output = deck(args.profile, jobcard)
    if args.check:
        print(f"CHECK INFO {args.profile.upper()}: {len(output.splitlines())} cards; no JCL written")
        return
    path = ROOT / "workarea/qsam-q0-info" / f"q0-info-{args.profile}.jcl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="ascii", newline="\n")
    path.chmod(0o600)
    print(f"Q.0 {args.profile.upper()} INFO JCL: {path}")


if __name__ == "__main__":
    main()
