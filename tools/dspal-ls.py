#!/usr/bin/env python3
"""PDS member listing for dspal.

A specific DATASET lists only member names.  With no operand, one TSO job
queries every managed PDS and prints a labelled inventory, including empty
libraries.  A LISTDS result that lacks a MEMBERS block is treated as an error,
not as an empty PDS.
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


def resolve_pds(config: dict[str, Any], operand: str) -> tuple[str, str | None]:
    dsn, logical = core.resolve_dsn(config, operand)
    spec = config["datasets"].get(logical) if logical else None
    if spec is not None and str(spec.get("dsorg", "")).upper() != "PO":
        raise DspalError(f"not a partitioned data set: {dsn}")
    return dsn, logical


def list_members_deck(
    config: dict[str, Any], dsns: list[str], redact_password: bool = False
) -> str:
    lines = core.authenticated_job_card(
        config, "DSPALLS", "DSPAL LS", redact_password=redact_password
    )
    lines.extend(
        [
            "//* LIST PDS MEMBERS WITH TSO LISTDS MEMBERS",
            "//LIST     EXEC PGM=IKJEFT01",
            "//SYSTSPRT DD  SYSOUT=*",
            "//SYSTSIN  DD  *",
        ]
    )
    for dsn in dsns:
        lines.append(f" LISTDS '{dsn}' MEMBERS")
    lines.append("/*")
    return "\n".join(lines) + "\n"


def member_block(report: str, dsn: str) -> list[str] | None:
    """Return lines following this data set's --MEMBERS-- header through END."""
    lines = report.replace("\r", "").splitlines()
    target = dsn.upper()
    headers: list[int] = []

    for index, line in enumerate(lines):
        if "--MEMBERS--" not in line.upper():
            continue
        prefix = "\n".join(lines[max(0, index - 20) : index]).upper()
        if target in prefix:
            headers.append(index)

    if not headers:
        return None

    result: list[str] = []
    for line in lines[headers[-1] + 1 :]:
        text = line.strip()
        if text.upper() == "END":
            break
        if re.search(r"\bLISTDS\s+'", text.upper()):
            break
        if text.startswith("IEF") or text.startswith("$HASP"):
            break
        result.append(line)
    return result


def parse_members(block: list[str]) -> list[str]:
    members: list[str] = []
    for line in block:
        text = line.strip().upper()
        if not text or text.startswith("--"):
            continue
        token = text.split()[0]
        if re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}", token):
            members.append(token)
    return members


def require_members_block(report: str, dsn: str, job: int) -> list[str]:
    block = member_block(report, dsn)
    if block is not None:
        return block

    if core.dataset_missing(report, dsn):
        raise DspalError(f"data set not found: {dsn}")

    # An empty PDS still produces --MEMBERS-- followed by END.  Therefore a
    # missing MEMBERS block is never silently interpreted as an empty library.
    raise DspalError(
        f"JOB {job}: LISTDS MEMBERS did not return a member directory for {dsn}; "
        "retry with --raw to inspect the TSO response"
    )


def managed_pds(config: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for logical, spec in config["datasets"].items():
        if str(spec.get("dsorg", "")).upper() == "PO":
            result.append((logical, core.full_dsn(config, spec)))
    return result


def cmd_ls(
    config: dict[str, Any], dataset: str | None, show_jcl: bool, raw: bool
) -> int:
    if dataset is None:
        selected = managed_pds(config)
        dsns = [dsn for _, dsn in selected]
        if show_jcl:
            sys.stdout.write(list_members_deck(config, dsns, redact_password=True))
            return 0

        core.require_reader_ready(config)
        job, _ = core.submit_and_wait(
            config, list_members_deck(config, dsns), max_rc=8
        )
        report = core.job_report(job)
        if raw:
            sys.stdout.write(report)
            if not report.endswith("\n"):
                print()
            return 0

        for logical, dsn in selected:
            block = require_members_block(report, dsn, job)
            members = parse_members(block)
            print(f"{logical} ({dsn})")
            if members:
                for member in members:
                    print(f"    {member}")
            else:
                print("    (empty)")
        return 0

    dsn, _ = resolve_pds(config, dataset)
    if show_jcl:
        sys.stdout.write(list_members_deck(config, [dsn], redact_password=True))
        return 0

    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(
        config, list_members_deck(config, [dsn]), max_rc=8
    )
    report = core.job_report(job)
    if raw:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            print()
        return 0

    block = require_members_block(report, dsn, job)
    for member in parse_members(block):
        print(member)
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dspal ls",
        description=(
            "List PDS members. With no DATASET, inventory all managed PDSes in "
            "one TSO job."
        ),
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        help="managed logical name or PDS DSN; omit for all managed PDSes",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--show-jcl",
        action="store_true",
        help="emit LISTDS MEMBERS JCL without submitting it",
    )
    mode.add_argument(
        "--raw", action="store_true", help="print the complete JES report"
    )
    return parser


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        return cmd_ls(config, args.dataset, args.show_jcl, args.raw)
    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
