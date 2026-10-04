#!/usr/bin/env python3
"""PDS maintenance commands for dspal."""

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


def resolve_managed_pds(config: dict[str, Any], operand: str) -> tuple[str, str | None]:
    dsn, logical = core.resolve_dsn(config, operand)
    spec = config["datasets"].get(logical) if logical else None
    if spec is not None and str(spec.get("dsorg", "")).upper() != "PO":
        raise DspalError(f"not a partitioned data set: {dsn}")
    return dsn, logical


def rm_deck(
    config: dict[str, Any], dsn: str, member: str, redact_password: bool = False
) -> str:
    lines = core.authenticated_job_card(
        config, "DSPALRM", "DSPAL RM", redact_password=redact_password
    )
    lines.extend(
        [
            "//* DELETE EXACTLY ONE PDS MEMBER WITH TSO DELETE",
            "//DELETE   EXEC PGM=IKJEFT01",
            "//SYSTSPRT DD  SYSOUT=*",
            "//SYSTSIN  DD  *",
            f" DELETE '{dsn}({member})'",
            "/*",
        ]
    )
    return "\n".join(lines) + "\n"


def compress_deck(
    config: dict[str, Any], dsn: str, redact_password: bool = False
) -> str:
    unit = str(config["mvs"].get("default_unit") or "SYSDA").upper()
    lines = core.authenticated_job_card(
        config, "DSPALCMP", "DSPAL COMPRESS", redact_password=redact_password
    )
    lines.extend(
        [
            "//* COMPRESS ONE PDS IN PLACE WITH IEBCOPY",
            "//* THE PDS IS HELD DISP=OLD FOR EXCLUSIVE ACCESS DURING THE STEP.",
            "//COMPRESS EXEC PGM=IEBCOPY",
            "//SYSPRINT DD  SYSOUT=*",
            f"//PDS      DD  DSN={dsn},DISP=OLD",
            f"//SYSUT3   DD  UNIT={unit},SPACE=(TRK,(5,5)),DISP=(NEW,DELETE)",
            f"//SYSUT4   DD  UNIT={unit},SPACE=(TRK,(5,5)),DISP=(NEW,DELETE)",
            "//SYSIN    DD  *",
            " COPY OUTDD=PDS,INDD=PDS",
            "/*",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_rm(
    config: dict[str, Any], dataset: str, member: str, show_jcl: bool
) -> int:
    dsn, _ = resolve_managed_pds(config, dataset)
    member = validate_member(member)
    deck = rm_deck(config, dsn, member, redact_password=show_jcl)
    if show_jcl:
        sys.stdout.write(deck)
        return 0

    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, deck, max_rc=0)
    print(f"rm completed as JOB {job}: {dsn}({member})")
    return 0


def cmd_compress(config: dict[str, Any], dataset: str, show_jcl: bool) -> int:
    dsn, _ = resolve_managed_pds(config, dataset)
    deck = compress_deck(config, dsn, redact_password=show_jcl)
    if show_jcl:
        sys.stdout.write(deck)
        return 0

    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, deck, max_rc=0)
    print(f"compress completed as JOB {job}: {dsn}")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain BCPL project PDS libraries on MVS/TK5.")
    sub = parser.add_subparsers(dest="command", required=True)

    rm = sub.add_parser("rm", help="delete exactly one PDS member")
    rm.add_argument("dataset", help="managed logical name or PDS DSN")
    rm.add_argument("member", help="member to delete")
    rm.add_argument(
        "--show-jcl", action="store_true", help="emit deletion JCL without submitting it"
    )

    compress = sub.add_parser("compress", help="compress one PDS in place with IEBCOPY")
    compress.add_argument("dataset", help="managed logical name or PDS DSN")
    compress.add_argument(
        "--show-jcl", action="store_true", help="emit compression JCL without submitting it"
    )
    return parser


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        if args.command == "rm":
            return cmd_rm(config, args.dataset, args.member, args.show_jcl)
        if args.command == "compress":
            return cmd_compress(config, args.dataset, args.show_jcl)
        raise DspalError(f"unimplemented command: {args.command}")
    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
