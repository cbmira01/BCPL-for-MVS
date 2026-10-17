#!/usr/bin/env python3
"""Audit existing full 00..145 native regression logs without running MVS."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "native-compiler/regression"
LOGS = ROOT / "workarea/native-regression/logs"
MANIFEST = ROOT / "workarea/native-regression/m44-00-145-jobs.tsv"
SKIP = 83
END = 145


def expected_go(number: int, case_dir: Path) -> str:
    # D6 is used by both the accepted historical DEVOBJ(BCPLM6) panel
    # and the new all-OBJ production profile. D7 retains RC0012.
    profile = case_dir / "expected-go-rc-bcplm6.txt"
    fixture = profile if profile.is_file() else case_dir / "expected-go-rc.txt"
    if fixture.exists():
        value = fixture.read_text(encoding="ascii").strip()
        if not re.fullmatch(r"\d{4}", value):
            raise ValueError(f"bad expected GO RC: {fixture}")
        return value
    return {87: "0100", 89: "0008"}.get(number, "0000")


def audit() -> int:
    discover = runpy.run_path(
        str(ROOT / "tools/native/run-regression"), run_name="m44_log_audit"
    )["discover"]
    cases, highest = discover()
    if highest != END or set(cases) != set(range(END + 1)):
        raise ValueError("corpus drift: expected exactly 00..145")

    # Fail closed if either historical stack-overflow profile drifts.
    for number in (52, 93):
        case = REG / cases[number]
        if ((case / "expected-go-rc.txt").read_text(
                encoding="ascii").strip() != "0012"
            or (case / "expected-go-rc-bcplm6.txt").read_text(
                encoding="ascii").strip() != "0000"):
            raise ValueError(
                f"{number:03d}: D7 default / D6 BCPLM6 RC fixtures drifted"
            )
    rows = ["test\tcase\tcompiler_jobs\tgo_job\tasmap\tasmbio\tasmnat\tlked\tgo\texpected_go\tresult"]
    problems: list[str] = []
    go_counts: Counter[str] = Counter()
    first_time = None
    last_time = None
    found = 0

    for number, name in sorted(cases.items()):
        if number == SKIP:
            continue
        path = LOGS / (name + ".log")
        if not path.is_file():
            problems.append(f"{number:03d}: missing log {path}")
            continue
        found += 1
        stamp = path.stat().st_mtime
        first_time = stamp if first_time is None else min(first_time, stamp)
        last_time = stamp if last_time is None else max(last_time, stamp)
        log = path.read_text(encoding="utf-8", errors="replace")
        results = re.findall(r"^RESULT:\s*(.*?)\s*$", log, flags=re.M)
        if results != ["PASS"]:
            problems.append(f"{number:03d}: result {results!r}; expected exactly PASS")
        if "PASS WITH KNOWN RUNTIME DEFECT" in log or re.search(
            r"\bABEND S[0-9A-F]{3}\b", log
        ):
            problems.append(f"{number:03d}: known-defect/ABEND signature in log")
        if not re.search(r"^TEST:\s*" + re.escape(name) + r"\s*$", log, flags=re.M):
            problems.append(f"{number:03d}: TEST identity missing/mismatched")
        jobs = re.findall(r"^JOB\s+(\d+)\s*$", log, flags=re.M)
        case_dir = REG / name
        compile_only = (case_dir / "compile-only.txt").is_file()
        if len(jobs) < (1 if compile_only else 2):
            problems.append(
                f"{number:03d}: too few job IDs for "
                + ("compile-only" if compile_only else "compiler/GO")
            )
        step = {}
        for match in re.finditer(
            r"^\s*(ASMAP|ASMBCPL|ASM|ASMFIO|ASMNAT|LKED|GO)\s+.*?\bRC=(\d{4})\b",
            log, flags=re.M
        ):
            step[match.group(1)] = match.group(2)
        if compile_only:
            # Regression 048 intentionally performs Cambridge codegen only.
            if not re.search(r"^TERMINATION:\s*COMPILE-ONLY\s*$",
                             log, flags=re.M):
                problems.append(
                    f"{number:03d}: missing COMPILE-ONLY termination"
                )
            if "GO" in step or "LKED" in step:
                problems.append(
                    f"{number:03d}: unexpected GO/LKED in compile-only test"
                )
            rows.append("\t".join((
                f"{number:03d}", name, ",".join(jobs),
                "", step.get("ASMAP", ""), step.get("ASMFIO", ""),
                step.get("ASMNAT", ""), "", "NOT RUN", "NOT RUN",
                "|".join(results) if results else "MISSING",
            )))
            continue

        wanted = expected_go(number, case_dir)
        actual = step.get("GO", "MISSING")
        go_counts[actual] += 1
        if actual != wanted:
            problems.append(
                f"{number:03d}: GO RC={actual}; fixture requires {wanted}; "
                "D6 stack-overflow GO contract unresolved"
            )
        if step.get("LKED") != "0000":
            problems.append(f"{number:03d}: LKED RC={step.get('LKED', 'MISSING')}")
        for asm in ("ASMAP", "ASMFIO", "ASMNAT"):
            if asm in step and step[asm] != "0000":
                problems.append(f"{number:03d}: {asm} RC={step[asm]}")
        rows.append("\t".join((
            f"{number:03d}", name, ",".join(jobs[:-1]),
            jobs[-1] if jobs else "", step.get("ASMAP", ""),
            step.get("ASMFIO", ""), step.get("ASMNAT", ""),
            step.get("LKED", ""), actual, wanted,
            "|".join(results) if results else "MISSING",
        )))

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"M4.4 existing regression logs: {found}/145")
    print("Expected runner skip: 083 (source-only)")
    print("Compile-only: 048 (no GO or LKED)")
    print("GO-RC profile: D6 (all-OBJ or historical DEVOBJ BCPLM6);"
          " 052 and 093 expect RC0000")
    print("GO RC distribution: " +
          ", ".join(f"{code}={count}" for code, count in sorted(go_counts.items())))
    if first_time is not None:
        fmt = lambda t: datetime.fromtimestamp(t, timezone.utc).isoformat()
        print("Log mtime UTC: " + fmt(first_time) + " .. " + fmt(last_time))
    print("Saved JES job/step manifest: " + str(MANIFEST.relative_to(ROOT)))
    if problems:
        print(f"M4.4 detailed log audit: ATTENTION ({len(problems)} findings)")
        for item in problems:
            print("  " + item)
        return 1
    print("M4.4 detailed log audit: PASS (no detected known-defect/abend exceptions)")
    print("This checks saved harness reports, not physical per-DD MVS records.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(audit())
    except (OSError, ValueError, RuntimeError) as exc:
        sys.exit(f"M4.4 log audit: {exc}")
