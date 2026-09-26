#!/usr/bin/env python3
"""Summarize an MVS/TK5 job from a Hercules printer output stream."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


START_JOB_RE = re.compile(
    r"\*+A\s+START\s+JOB\s+(\d+)\s+(\S+)(.*?)"
    r"\s+ROOM\s+.*?\s+(\d{1,2}\.\d{2}\.\d{2})\s+"
    r"(AM|PM)\s+(\d{1,2}\s+[A-Z]{3}\s+\d{2})\s+"
)

END_JOB_RE = re.compile(
    r"\*+A\s+END\s+JOB\s+(\d+)\s+"
)

IEFACTRT_RE = re.compile(
    r"^\s*\d+\.\d+\.\d+\s+JOB\s+\d+\s+"
    r"(\S+)\s+(\S+)\s+(?:(\S+)\s+)?RC=\s*(\d+)\s*$"
)

IEF142I_RE = re.compile(
    r"IEF142I\s+(\S+)\s+(\S+)"
    r"(?:\s+(\S+))?\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE\s+(\d+)"
)

IEF403I_RE = re.compile(
    r"IEF403I\s+\S+\s+-\s+STARTED\s+-\s+TIME=(\d{2}\.\d{2}\.\d{2})"
)

IEF404I_RE = re.compile(
    r"IEF404I\s+\S+\s+-\s+ENDED\s+-\s+TIME=(\d{2}\.\d{2}\.\d{2})"
)

IEF376I_RE = re.compile(
    r"IEF376I\s+JOB\s+/\S+/\s+STOP\s+\S+\s+"
    r"CPU\s+(\d+)MIN\s+([\d.]+)SEC\s+"
    r"SRB\s+(\d+)MIN\s+([\d.]+)SEC"
)

CARDS_RE = re.compile(r"^\s*(\d+)\s+CARDS READ\s*$")
SYSOUT_RE = re.compile(r"^\s*(\d+)\s+SYSOUT PRINT RECORDS\s*$")

ASM_FLAGGED_RE = re.compile(
    r"NO STATEMENTS FLAGGED IN THIS ASSEMBLY"
)

ASM_SEVERITY_RE = re.compile(
    r"HIGHEST SEVERITY WAS\s+(\d+)"
)

ABEND_RE = re.compile(
    r"\b(?:ABEND|ABENDED|SYSTEM COMPLETION CODE|USER COMPLETION CODE)\b",
    re.IGNORECASE,
)

JCL_ERROR_RE = re.compile(
    r"\b(?:JCL ERROR|JCLERR|JCL ERROR WAS DETECTED)\b",
    re.IGNORECASE,
)

BYPASSED_RE = re.compile(
    r"\b(?:STEP WAS NOT EXECUTED|STEP WAS BYPASSED)\b",
    re.IGNORECASE,
)


@dataclass
class Step:
    name: str
    program: str
    rc: int


@dataclass
class Job:
    number: int
    name: str
    description: str
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    steps: list[Step] | None = None
    cards: int | None = None
    sysout_records: int | None = None
    cpu_seconds: float | None = None
    srb_seconds: float | None = None
    assembler_flagged: int | None = None
    assembler_severity: int | None = None
    abend: bool = False
    jcl_error: bool = False
    bypassed: bool = False

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize an MVS/TK5 job from prt00e output."
    )

    parser.add_argument(
        "job",
        type=int,
        help="JES job number to summarize, for example: 6",
    )

    parser.add_argument(
        "--file",
        type=Path,
        help=(
            "Printer output file. If omitted, use "
            "mvs-state/prt/prt00e.txt relative to the repository root."
        ),
    )

    parser.add_argument(
        "--max-rc",
        type=int,
        default=4,
        metavar="RC",
        help="Highest return code considered successful (default: 4).",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show noteworthy raw diagnostic messages.",
    )

    return parser.parse_args()


def find_repo_root(start: Path) -> Path:
    """Find the repository root by walking upward looking for .git."""
    current = start.resolve()

    for directory in (current, *current.parents):
        if (directory / ".git").exists():
            return directory

    raise RuntimeError(
        "Unable to locate repository root; use --file explicitly."
    )


def default_printer_file() -> Path:
    root = find_repo_root(Path.cwd())
    return root / "mvs-state" / "prt" / "prt00e.txt"


def extract_job(lines: list[str], job_number: int) -> list[str]:
    """Extract one complete job using TK5 START JOB / END JOB banners."""
    result: list[str] = []
    inside = False

    for line in lines:
        start_match = START_JOB_RE.search(line)

        if not inside and start_match:
            if int(start_match.group(1)) == job_number:
                inside = True
                result.append(line)
            continue

        if inside:
            result.append(line)

            end_match = END_JOB_RE.search(line)
            if end_match and int(end_match.group(1)) == job_number:
                return result

    if inside:
        raise RuntimeError(
            f"JOB {job_number} starts in the printer file but has no END JOB banner."
        )

    raise RuntimeError(f"JOB {job_number} was not found in the printer file.")


def parse_job(job_number: int, lines: list[str]) -> tuple[Job, list[str]]:
    first = next(
        (START_JOB_RE.search(line) for line in lines if START_JOB_RE.search(line)),
        None,
    )

    if first is None:
        raise RuntimeError("Unable to parse START JOB banner.")

    name = first.group(2)
    description = first.group(3).strip()
    banner_time = first.group(4)
    am_pm = first.group(5)
    date = first.group(6)

    job = Job(
        number=job_number,
        name=name,
        description=description,
        date=date,
    )

    diagnostics: list[str] = []
    steps_seen: set[str] = set()

    for line in lines:
        match = IEF403I_RE.search(line)
        if match:
            job.start_time = match.group(1)

        match = IEF404I_RE.search(line)
        if match:
            job.end_time = match.group(1)

        # IEFACTRT is the preferred compact step summary.
        match = IEFACTRT_RE.match(line)
        if match:
            step_name = match.group(2)
            program = match.group(3) or ""
            rc = int(match.group(4))

            if step_name not in steps_seen:
                job.steps.append(
                    Step(
                        name=step_name,
                        program=program,
                        rc=rc,
                    )
                )
                steps_seen.add(step_name)

        match = CARDS_RE.match(line)
        if match:
            job.cards = int(match.group(1))

        match = SYSOUT_RE.match(line)
        if match:
            job.sysout_records = int(match.group(1))

        match = IEF376I_RE.search(line)
        if match:
            job.cpu_seconds = (
                int(match.group(1)) * 60 + float(match.group(2))
            )
            job.srb_seconds = (
                int(match.group(3)) * 60 + float(match.group(4))
            )

        if ASM_FLAGGED_RE.search(line):
            job.assembler_flagged = 0

        match = ASM_SEVERITY_RE.search(line)
        if match:
            job.assembler_severity = int(match.group(1))

        if ABEND_RE.search(line):
            job.abend = True
            diagnostics.append(line.rstrip())

        if JCL_ERROR_RE.search(line):
            job.jcl_error = True
            diagnostics.append(line.rstrip())

        if BYPASSED_RE.search(line):
            job.bypassed = True
            diagnostics.append(line.rstrip())

    # Fall back to IEF142I if IEFACTRT wasn't available.
    if not job.steps:
        for line in lines:
            match = IEF142I_RE.search(line)
            if not match:
                continue

            step_name = match.group(2)
            rc = int(match.group(4))

            if step_name not in steps_seen:
                job.steps.append(
                    Step(
                        name=step_name,
                        program="",
                        rc=rc,
                    )
                )
                steps_seen.add(step_name)

    return job, diagnostics


def format_seconds(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2f} sec"


def print_summary(
    job: Job,
    diagnostics: list[str],
    max_rc: int,
    verbose: bool,
) -> bool:
    highest_rc = max((step.rc for step in job.steps), default=None)

    success = (
        not job.abend
        and not job.jcl_error
        and not job.bypassed
        and highest_rc is not None
        and highest_rc <= max_rc
    )

    print(f"JOB {job.number}  {job.name}")

    if job.description:
        print(job.description)

    if job.date:
        times = ""
        if job.start_time or job.end_time:
            times = (
                f"  {job.start_time or '?'}"
                f" - {job.end_time or '?'}"
            )
        print(f"{job.date}{times}")

    print()

    if job.steps:
        print(f"{'STEP':<10} {'PROGRAM':<12} RESULT")

        for step in job.steps:
            print(
                f"{step.name:<10} "
                f"{step.program:<12} "
                f"RC={step.rc:04d}"
            )
    else:
        print("No executed steps found.")

    print()

    print(f"JOB RESULT: {'SUCCESS' if success else 'FAILURE'}")

    if highest_rc is not None:
        print(f"HIGHEST RC: {highest_rc:04d}")
    else:
        print("HIGHEST RC: -")

    if job.abend:
        print("ABEND:      detected")

    if job.jcl_error:
        print("JCL ERROR:  detected")

    if job.bypassed:
        print("BYPASSED:   one or more steps")

    if (
        job.assembler_flagged is not None
        or job.assembler_severity is not None
    ):
        print()
        print("Assembler:")

        if job.assembler_flagged is not None:
            print(
                f"  Statements flagged: {job.assembler_flagged}"
            )

        if job.assembler_severity is not None:
            print(
                f"  Highest severity:   {job.assembler_severity}"
            )

    if (
        job.cpu_seconds is not None
        or job.srb_seconds is not None
        or job.cards is not None
        or job.sysout_records is not None
    ):
        print()
        print("Resources:")

        if job.cpu_seconds is not None:
            print(f"  CPU:       {format_seconds(job.cpu_seconds)}")

        if job.srb_seconds is not None:
            print(f"  SRB:       {format_seconds(job.srb_seconds)}")

        if job.cards is not None:
            print(f"  Cards:     {job.cards}")

        if job.sysout_records is not None:
            print(f"  SYSOUT:    {job.sysout_records} records")

    if verbose and diagnostics:
        print()
        print("Diagnostics:")

        for diagnostic in diagnostics:
            print(f"  {diagnostic.strip()}")

    return success


def main() -> int:
    args = parse_args()

    try:
        printer_file = args.file or default_printer_file()

        if not printer_file.is_file():
            raise RuntimeError(
                f"Printer output file does not exist: {printer_file}"
            )

        lines = printer_file.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        job_lines = extract_job(lines, args.job)
        job, diagnostics = parse_job(args.job, job_lines)

        success = print_summary(
            job,
            diagnostics,
            args.max_rc,
            args.verbose,
        )

        return 0 if success else 1

    except (OSError, RuntimeError) as exc:
        print(f"job-summary: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

