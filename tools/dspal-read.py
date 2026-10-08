#!/usr/bin/env python3
"""Direct PDS member read path for dspal cat/get.

This deliberately avoids concatenated SYSUT1 DDs.  One FB/80 member is copied
straight to a single SYSOUT data set with IEBGENER; the host then extracts that
sole data SYSOUT from the captured JES report.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "tools" / "dspal-core.py"


def load_core():
    spec = importlib.util.spec_from_file_location("dspal_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_core()
DspalError = core.DspalError


def validate_member(member: str) -> str:
    value = member.strip().upper()
    if not re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}", value):
        raise DspalError(f"invalid PDS member name: {member}")
    return value


def resolve_text_pds(config: dict[str, Any], operand: str):
    dsn, logical = core.resolve_dsn(config, operand)
    spec = config["datasets"].get(logical) if logical else None
    if spec is None:
        raise DspalError(
            "cat/get currently require a managed PDS logical name so record format can be validated"
        )
    if str(spec.get("dsorg", "")).upper() != "PO":
        raise DspalError(f"not a partitioned data set: {dsn}")
    if str(spec.get("content_type", "")).lower() == "object":
        raise DspalError(f"binary object library {dsn}: text cat/get prohibited")
    if str(spec.get("recfm", "")).upper() != "FB":
        raise DspalError(f"text transfer currently requires RECFM=FB: {dsn}")
    if int(spec.get("lrecl", 0) or 0) != 80:
        raise DspalError(f"text transfer currently requires LRECL=80: {dsn}")
    return dsn


def read_deck(
    config: dict[str, Any], dsn: str, member: str, redact_password: bool = False
) -> str:
    lines = core.authenticated_job_card(
        config, "DSPALGET", "DSPAL GET", redact_password=redact_password
    )
    lines.extend(
        [
            "//* COPY ONE FB/80 PDS MEMBER DIRECTLY TO A SINGLE SYSOUT DATA SET",
            "//COPY     EXEC PGM=IEBGENER",
            "//SYSPRINT DD  DUMMY",
            "//SYSIN    DD  DUMMY",
            f"//SYSUT1   DD  DSN={dsn}({member}),DISP=SHR",
            "//SYSUT2   DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        ]
    )
    return "\n".join(lines) + "\n"


def extract_data_sysout(report: str) -> str:
    """Extract the sole SYSUT2 stream following the JES accounting output.

    TK5 appends its large DSPALGET/JOB banner after the final SYSOUT stream.
    With SYSPRINT allocated DUMMY, SYSUT2 is the only application SYSOUT, so
    everything after the final IEF376 accounting line up to that banner is the
    member data.  FB padding is stripped on the right only.
    """
    lines = report.replace("\r", "").splitlines()
    stops = [
        index
        for index, line in enumerate(lines)
        if re.search(r"^IEF376I\s+JOB\s+/DSPALGET/\s+STOP\b", line)
    ]
    if not stops:
        raise DspalError(
            "member transfer completed but the final DSPALGET accounting marker was not found"
        )

    data = lines[stops[-1] + 1 :]
    while data and not data[0].strip():
        data.pop(0)

    records: list[str] = []
    banner = re.compile(r"^\s*([A-Z])\1{5,}")
    for line in data:
        if banner.match(line):
            break
        records.append(line.rstrip(" "))

    while records and records[-1] == "":
        records.pop()

    if not records and data:
        # An empty member is legitimate, but a non-empty tail that could not be
        # recognized should not silently become empty data.
        first = next((line for line in data if line.strip()), "")
        if first and not banner.match(first):
            raise DspalError("could not isolate the member SYSOUT in the JES report")

    return "\n".join(records) + ("\n" if records else "")


def read_member(
    config: dict[str, Any], dataset: str, member: str, show_jcl: bool = False
):
    dsn = resolve_text_pds(config, dataset)
    member = validate_member(member)
    deck = read_deck(config, dsn, member, redact_password=show_jcl)
    if show_jcl:
        return None, deck

    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, deck, max_rc=0)
    report = core.job_report(job)
    return job, extract_data_sysout(report)


def cmd_cat(config: dict[str, Any], dataset: str, member: str, show_jcl: bool) -> int:
    _, result = read_member(config, dataset, member, show_jcl=show_jcl)
    sys.stdout.write(result)
    return 0


def cmd_get(
    config: dict[str, Any],
    dataset: str,
    member: str,
    destination: str,
    show_jcl: bool,
) -> int:
    job, result = read_member(config, dataset, member, show_jcl=show_jcl)
    if show_jcl:
        sys.stdout.write(result)
        return 0

    if destination == "-":
        sys.stdout.write(result)
        return 0

    path = Path(destination)
    path.write_text(
        result,
        encoding=str(config["text"].get("host_encoding", "utf-8")),
        newline="\n",
    )
    print(
        f"get completed as JOB {job}: {dataset.upper()}({member.upper()}) -> {path}",
        file=sys.stderr,
    )
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read text PDS members for dspal.")
    sub = parser.add_subparsers(dest="command", required=True)

    cat = sub.add_parser("cat", help="write one text PDS member to stdout")
    cat.add_argument("dataset")
    cat.add_argument("member")
    cat.add_argument("--show-jcl", action="store_true")

    get = sub.add_parser("get", help="copy one text PDS member to a host file or -")
    get.add_argument("dataset")
    get.add_argument("member")
    get.add_argument("destination")
    get.add_argument("--show-jcl", action="store_true")
    return parser


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        if args.command == "cat":
            return cmd_cat(config, args.dataset, args.member, args.show_jcl)
        if args.command == "get":
            return cmd_get(
                config, args.dataset, args.member, args.destination, args.show_jcl
            )
        raise DspalError(f"unimplemented command: {args.command}")
    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
