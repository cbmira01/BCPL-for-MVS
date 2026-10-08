#!/usr/bin/env python3
"""Submit a stored JCL job body through the JES internal reader.

Usage:
    tools/dspal submit JCL CAMBBLD
    tools/dspal submit JCL CAMBBLD --wait
    tools/dspal submit JCL CAMBBLD --show-jcl

The PDS member is never copied back to the host.  dspal submits a small
authenticated launcher job whose IEBGENER SYSUT1 concatenates:

  1. an authenticated payload JOB card generated from dspal.local.yaml; and
  2. the requested FB/80 JCL PDS member.

SYSUT2 is SYSOUT=(A,INTRDR), so JES receives the resulting complete job deck.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "tools" / "dspal-core.py"
LS_PATH = ROOT / "tools" / "dspal-ls.py"


def load_core():
    spec = importlib.util.spec_from_file_location("dspal_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_core()
DspalError = core.DspalError


def load_ls():
    spec = importlib.util.spec_from_file_location("dspal_ls", LS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {LS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lsmod = load_ls()


def validate_member(member: str) -> str:
    value = member.strip().upper()
    if not re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}", value):
        raise DspalError(f"invalid JCL member name: {member}")
    return value


def resolve_text_pds(
    config: dict[str, Any], operand: str
) -> tuple[str, str | None, dict[str, Any] | None]:
    dsn, logical = core.resolve_dsn(config, operand)
    spec = config["datasets"].get(logical) if logical else None
    if spec is None:
        raise DspalError(
            "submit requires a managed PDS logical name so its attributes "
            "can be validated"
        )
    if str(spec.get("dsorg", "")).upper() != "PO":
        raise DspalError(f"not a partitioned data set: {dsn}")
    if str(spec.get("content_type", "")).lower() == "object":
        raise DspalError(f"cannot submit binary object records as JCL: {dsn}")
    if str(spec.get("recfm", "")).upper() != "FB":
        raise DspalError(f"submit requires an FB text PDS: {dsn}")
    if int(spec.get("lrecl", 0) or 0) != 80:
        raise DspalError(f"submit requires LRECL=80: {dsn}")
    return dsn, logical, spec


def require_member_exists(
    config: dict[str, Any], dsn: str, member: str
) -> None:
    """Fail locally before launching if the requested PDS member is absent."""
    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(
        config,
        lsmod.list_members_deck(config, [dsn]),
        max_rc=8,
    )
    report = core.job_report(job)
    block = lsmod.require_members_block(report, dsn, job, [dsn])
    members = lsmod.parse_members(block)
    if member not in members:
        available = ", ".join(members) if members else "(none)"
        raise DspalError(
            f"member not found: {dsn}({member}); available members: {available}"
        )


def payload_job_card(
    config: dict[str, Any],
    jobname: str,
    description: str,
    redact_password: bool,
) -> list[str]:
    return core.authenticated_job_card(
        config,
        jobname,
        description,
        redact_password=redact_password,
    )


def launcher_deck(
    config: dict[str, Any],
    dsn: str,
    member: str,
    redact_password: bool = False,
) -> str:
    """Build a three-step internal-reader launcher.

    Do not concatenate an in-stream DD with a PDS member directly.  Classic
    JES/JCL handling is much more predictable if we first create a real FB/80
    sequential card deck, append the stored job body to it, and only then feed
    that data set to INTRDR.
    """
    lines = core.authenticated_job_card(
        config,
        "DSPALSUB",
        "DSPAL SUBMIT",
        redact_password=redact_password,
    )
    lines.extend(
        [
            "//* SUBMIT ONE STORED JCL JOB BODY THROUGH JES INTERNAL READER",
            f"//* PAYLOAD: {dsn}({member})",
            "//*",
            "//* STEP 1: CREATE FB/80 PAYLOAD WITH ONLY THE GENERATED JOB CARD.",
            "//MKJOB    EXEC PGM=IEBGENER",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            "//SYSUT2   DD  DSN=&&PAYLOAD,UNIT=SYSDA,SPACE=(80,(50,20)),",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800),",
            "//             DISP=(NEW,PASS)",
            "//SYSUT1   DD  DATA,DLM=ZZ",
        ]
    )
    lines.extend(
        payload_job_card(
            config,
            member,
            f"BCPL {member}",
            redact_password=redact_password,
        )
    )
    lines.extend(
        [
            "ZZ",
            "//*",
            "//* STEP 2: APPEND THE STORED JOB BODY TO THE SAME CARD DECK.",
            "//APPEND   EXEC PGM=IEBGENER",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            f"//SYSUT1   DD  DSN={dsn}({member}),DISP=SHR",
            "//SYSUT2   DD  DSN=&&PAYLOAD,DISP=(MOD,PASS)",
            "//*",
            "//* STEP 3: FEED THE COMPLETE FB/80 CARD DECK TO JES.",
            "//SUBMIT   EXEC PGM=IEBGENER",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            "//SYSUT1   DD  DSN=&&PAYLOAD,DISP=(OLD,DELETE)",
            "//SYSUT2   DD  SYSOUT=(A,INTRDR),",
            "//             DCB=(RECFM=F,LRECL=80,BLKSIZE=80)",
        ]
    )
    return "\n".join(lines) + "\n"


def printer_path(config: dict[str, Any]) -> Path:
    return ROOT / str(config["runtime"]["printer"])


def printer_offset(config: dict[str, Any]) -> int:
    path = printer_path(config)
    if not path.is_file():
        raise DspalError(f"printer log not found: {path}")
    return path.stat().st_size


def new_printer_text(config: dict[str, Any], offset: int) -> str:
    path = printer_path(config)
    with path.open("rb") as stream:
        stream.seek(offset)
        return stream.read().decode("latin-1", errors="replace")


def find_job_number(text: str, jobname: str) -> int | None:
    name = re.escape(jobname.upper())
    patterns = (
        re.compile(rf"\bJOB\s+([0-9]+)\b.*\b{name}\b", re.I),
        re.compile(rf"\b{name}\b.*\bJOB\s+([0-9]+)\b", re.I),
        re.compile(rf"\$HASP373\s+([0-9]+)\s+{name}\b", re.I),
        re.compile(rf"\$HASP373\s+{name}\s+([0-9]+)\b", re.I),
    )
    for line in text.splitlines():
        upper = line.upper()
        if jobname.upper() not in upper:
            continue
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                return int(match.group(1))
    return None


def wait_for_payload_start(
    config: dict[str, Any], offset: int, jobname: str
) -> int:
    timeout = int(config["runtime"].get("submit_timeout", 120))
    deadline = time.monotonic() + timeout
    while time.monotonic() <= deadline:
        number = find_job_number(new_printer_text(config, offset), jobname)
        if number is not None:
            return number
        time.sleep(0.5)
    raise DspalError(
        f"launcher completed but payload {jobname} was not observed "
        f"within {timeout} seconds"
    )


def wait_for_payload_completion(
    config: dict[str, Any], job: int
) -> tuple[int, str]:
    timeout = int(config["runtime"].get("completion_timeout", 120))
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() <= deadline:
        cp = subprocess.run(
            [str(core.JOB_SUMMARY), str(job)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        last = cp.stdout.strip() or cp.stderr.strip()
        if cp.returncode in (0, 1):
            return cp.returncode, cp.stdout
        time.sleep(0.5)
    raise DspalError(
        f"timed out waiting for payload JOB {job}; last status: {last}"
    )


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dspal submit",
        description=(
            "Submit a stored FB/80 JCL job body through JES INTRDR without "
            "copying the PDS member back to the host."
        ),
    )
    p.add_argument("dataset", help="managed JCL PDS logical name, normally JCL")
    p.add_argument("member", help="stored job-body member; also used as payload job name")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--show-jcl",
        action="store_true",
        help="show the generated launcher JCL with passwords redacted",
    )
    mode.add_argument(
        "--wait",
        action="store_true",
        help="wait for the payload job to complete and print its job summary",
    )
    return p


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        dsn, _logical, _spec = resolve_text_pds(config, args.dataset)
        member = validate_member(args.member)

        if args.show_jcl:
            sys.stdout.write(
                launcher_deck(config, dsn, member, redact_password=True)
            )
            return 0

        require_member_exists(config, dsn, member)
        offset = printer_offset(config)
        deck = launcher_deck(config, dsn, member, redact_password=False)

        launcher_job, _summary = core.submit_and_wait(config, deck, max_rc=0)
        payload_job = wait_for_payload_start(config, offset, member)

        print(f"Submitted {dsn}({member})")
        print(f"Launcher: JOB {launcher_job}")
        print(f"Payload:  JOB {payload_job}")

        if args.wait:
            rc, summary = wait_for_payload_completion(config, payload_job)
            if summary:
                print()
                sys.stdout.write(summary)
                if not summary.endswith("\n"):
                    print()
            return 0 if rc == 0 else 1

        return 0

    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
