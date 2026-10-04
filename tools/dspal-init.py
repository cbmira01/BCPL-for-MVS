#!/usr/bin/env python3
"""Create missing dspal-managed BCPL datasets after strict preflight."""

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


def report_says_missing(report: str, dsn: str) -> bool:
    """Recognize classic TSO LISTDS missing-catalog responses for one DSN."""
    upper = report.upper()
    name = re.escape(dsn.upper())
    patterns = (
        rf"IKJ58503I\s+DATA\s+SET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"DATA\s+SET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"DATASET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"['\"]?{name}['\"]?\s+NOT\s+FOUND",
    )
    return any(re.search(pattern, upper) for pattern in patterns)


def probe_one(config: dict[str, Any], logical: str, spec: dict[str, Any]):
    dsn = core.full_dsn(config, spec)
    job, _ = core.submit_and_wait(
        config, core.stat_deck(config, [dsn]), max_rc=8
    )
    report = core.job_report(job)

    if report_says_missing(report, dsn):
        return job, None

    block = core.extract_listds_block(report, dsn)
    attrs = core.parse_listds(block) if block else {}
    if not attrs:
        raise DspalError(
            f"JOB {job}: could not determine whether {dsn} exists or parse its "
            f"LISTDS attributes; run dspal stat {logical} --raw"
        )
    return job, attrs


def cmd_initbcpl(config: dict[str, Any], show_jcl: bool) -> int:
    if show_jcl:
        sys.stdout.write(core.initbcpl_deck(config, redact_password=True))
        return 0

    core.require_reader_ready(config)
    missing: list[str] = []
    existing: list[str] = []
    incompatible: list[str] = []
    probes: list[int] = []

    for logical, spec in config["datasets"].items():
        job, attrs = probe_one(config, logical, spec)
        probes.append(job)
        if attrs is None:
            missing.append(logical)
            continue

        problems = core.mismatches(spec, attrs)
        if problems:
            incompatible.append(
                f"{logical} {core.full_dsn(config, spec)}: " + "; ".join(problems)
            )
        else:
            existing.append(logical)

    if incompatible:
        detail = "\n  ".join(incompatible)
        raise DspalError(
            "initbcpl preflight found incompatible managed data sets:\n  "
            + detail
            + "\nNo allocations were attempted."
        )

    if not missing:
        print(
            "initbcpl preflight completed as JOB "
            + ",".join(str(job) for job in probes)
        )
        print("All managed datasets already exist with compatible attributes.")
        return 0

    job, _ = core.submit_and_wait(
        config,
        core.initbcpl_deck(config, logicals=missing, redact_password=False),
        max_rc=0,
    )
    print(
        "initbcpl preflight completed as JOB "
        + ",".join(str(number) for number in probes)
    )
    print(f"initbcpl allocation completed as JOB {job}")
    for logical in existing:
        print(f"  {logical:<9} existing, compatible")
    for logical in missing:
        print(
            f"  {logical:<9} created "
            f"{core.full_dsn(config, config['datasets'][logical])}"
        )
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dspal initbcpl",
        description="Create missing managed datasets after strict per-DSN attribute preflight.",
    )
    parser.add_argument(
        "--show-jcl",
        action="store_true",
        help="emit worst-case allocation JCL without submitting it; password is redacted",
    )
    return parser


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        return cmd_initbcpl(config, args.show_jcl)
    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
