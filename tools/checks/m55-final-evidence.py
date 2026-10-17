#!/usr/bin/env python3
"""M5.5 native final-panel freshness gate (no MVS submission).

'begin' snapshots the existing native logs, source revision and candidate
profile before the operator runs the normal 00..145 regression runner.
'verify' requires a full new panel, 145 freshly written per-case logs and
a successful existing M4.4 step/RC audit. It records a receipt but never
declares owner acceptance or changes PDS/JCL/runtime.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "native-compiler/regression"
WORK = ROOT / "workarea/native-regression"
LOGS = WORK / "logs"
BEGIN = WORK / "m55-begin.json"
TRANSCRIPT = WORK / "m55-full-panel.log"
RECEIPT = WORK / "m55-verification.json"
M44_MANIFEST = WORK / "m44-00-145-jobs.tsv"
PROFILE = {
    "BCPL_RUNTIME_PDS": "1",
    "BCPL_RUNTIME_LIBRARY": "DEVOBJ",
    "BCPL_RUNTIME_CANDIDATE": "1",
    "BCPL_RUNTIME_CANDIDATE_MEMBER": "BCPLM6",
}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True)
    return proc.stdout.strip()


def cases() -> dict[int, str]:
    path = ROOT / "tools/native/run-regression"
    found, end = runpy.run_path(str(path), run_name="m55_inspect")["discover"]()
    require(end == 145 and set(found) == set(range(146)),
            "regression case numbering drift (expected 00..145)")
    return found


def profile() -> None:
    for key, value in PROFILE.items():
        require(os.environ.get(key) == value,
                f"candidate profile {key} must equal {value}")


def check_clean_checkout() -> str:
    require(git("status", "--porcelain") == "",
            "Git working tree is not clean; preserve edits before M5.5")
    return git("rev-parse", "HEAD")


def file_stat(path: Path) -> dict | None:
    if not path.exists():
        return None
    stat = path.stat()
    return {"mtime_ns": stat.st_mtime_ns, "size": stat.st_size}


def observe_previous_logs(names: dict[int, str]) -> dict[str, dict | None]:
    return {name: file_stat(LOGS / (name + ".log"))
            for number, name in sorted(names.items()) if number != 83}


def check_fresh(names: dict[int, str],
                old: dict[str, dict | None], start_ns: int,
                logs_dir: Path) -> list[str]:
    problems = []
    for number, name in sorted(names.items()):
        if number == 83:
            continue
        path = logs_dir / (name + ".log")
        current = file_stat(path)
        if current is None:
            problems.append(f"{number:03d}: missing log")
            continue
        previous = old.get(name)
        if current["mtime_ns"] < start_ns or (
                previous and current["mtime_ns"] <= previous["mtime_ns"]):
            problems.append(f"{number:03d}: stale log timestamp")
        if current["size"] == 0:
            problems.append(f"{number:03d}: empty case log")
    return problems


def parse_runner(text: str, names: dict[int, str]) -> None:
    require(len(re.findall(
        r"(?m)^NATIVE REGRESSION\s+00\.\.145\s+\(146 tests\)\s*$", text)) == 1,
        "missing/duplicate 00..145 regression banner")
    require(len(re.findall(
        r"(?m)^NATIVE REGRESSION COMPLETE\s*$", text)) == 1,
        "missing/duplicate full-panel completion marker")
    lines = text.splitlines()
    summary = [
        "NATIVE REGRESSION COMPLETE",
        "PASS  145",
        "FAIL  0",
        "SKIP  1",
        "TOTAL 146",
    ]
    require(any(lines[i:i + 5] == summary
                for i in range(max(0, len(lines) - 4))),
            "full-panel summary is not 145 PASS / 0 FAIL / 1 SKIP")
    # Match only horizontal whitespace between fields. \s includes
    # newlines: on the final "PASS  145" summary line it consumed the
    # newline and mistook "FAIL  0" for a case name. Parse each line.
    runs = re.findall(r"(?m)^RUN[ \t]+(\d{2,3})[ \t]+([^\r\n]+)$", text)
    passes = re.findall(r"(?m)^PASS[ \t]+(\d{2,3})[ \t]+([^\r\n]+)$", text)
    skips = re.findall(r"(?m)^SKIP[ \t]+(\d{2,3})[ \t]+([^\r\n]+)$", text)
    expected = [(f"{n:02d}" if n <= 52 else f"{n:03d}", names[n])
                for n in sorted(names) if n != 83]
    require(runs == expected, "RUN lines do not identify all 145 cases in order")
    require(passes == expected, "PASS lines do not identify all 145 cases in order")
    require(len(skips) == 1 and skips[0] == (
        "083", names[83] + " (source-only instrumentation)"),
        "expected SKIP 083 missing or additional SKIPs observed")
    require(not re.search(r"(?m)^FAIL[ \t]+\d{2,3}[ \t]+", text),
            "one or more numbered cases failed")


def begin() -> None:
    profile()
    names = cases()
    rev = check_clean_checkout()
    require(not (BEGIN.exists() or TRANSCRIPT.exists() or RECEIPT.exists()),
            "M5.5 evidence files already exist: do not overwrite a run")
    # A failed gate self-test must prevent "begin" from declaring readiness,
    # even if the operator's shell does not use set -e.
    for cmd in (
        [sys.executable, "tools/checks/test-m55-final-evidence.py"],
        [sys.executable, "tools/checks/check-m44-compatibility.py", "--candidate"],
        [sys.executable, "tools/checks/check-bcplio-m43-account.py"],
        ["tools/native/run-regression", "--check-numbering"],
    ):
        result = subprocess.run(cmd, cwd=ROOT)
        require(result.returncode == 0, "preflight command failed: " + " ".join(cmd))
    started_ns = time.time_ns()
    state = {
        "schema": "bcpl-m55-fresh-panel-v1",
        "git_sha": rev,
        "started_ns": started_ns,
        "started_utc": datetime.fromtimestamp(
            started_ns / 1e9, timezone.utc).isoformat(),
        "candidate_profile": PROFILE,
        "expected_range": "00..145",
        "expected_pass": 145,
        "expected_skip": [83],
        "prior_logs": observe_previous_logs(names),
        "status": "BEGIN_ONLY_NOT_EXECUTED",
    }
    WORK.mkdir(parents=True, exist_ok=True)
    with BEGIN.open("x", encoding="utf-8") as out:
        json.dump(state, out, indent=2)
        out.write("\n")
    print("M5.5 PREPARED: strict candidate preflight PASS")
    print(f"  Git: {rev}")
    print(f"  Baseline snapshot: {BEGIN.relative_to(ROOT)}")
    print(f"  Runner transcript: {TRANSCRIPT.relative_to(ROOT)}")
    print("  MVS/JES: NOT YET EXECUTED BY THIS TOOL")


def verify() -> None:
    profile()
    names = cases()
    rev = check_clean_checkout()
    require(BEGIN.is_file(), "M5.5 begin checkpoint missing")
    require(not RECEIPT.exists(), "M5.5 receipt already exists; no overwrite")
    state = json.loads(BEGIN.read_text(encoding="utf-8"))
    require(state.get("schema") == "bcpl-m55-fresh-panel-v1",
            "invalid M5.5 checkpoint schema")
    require(rev == state.get("git_sha"), "Git revision changed during panel")
    require(state.get("candidate_profile") == PROFILE and
            state.get("expected_range") == "00..145" and
            state.get("expected_pass") == 145 and
            state.get("expected_skip") == [83] and
            state.get("status") == "BEGIN_ONLY_NOT_EXECUTED",
            "M5.5 checkpoint contract changed")
    start_ns = state.get("started_ns")
    require(type(start_ns) is int and start_ns > 0,
            "invalid checkpoint timestamp")
    require(TRANSCRIPT.is_file(), "M5.5 runner transcript missing")
    text = TRANSCRIPT.read_text(encoding="utf-8", errors="replace")
    parse_runner(text, names)
    old = state.get("prior_logs")
    require(isinstance(old, dict) and set(old) ==
            {name for n, name in names.items() if n != 83},
            "M5.5 original log snapshot incomplete")
    stale = check_fresh(names, old, start_ns, LOGS)
    require(not stale, "; ".join(stale[:15]))
    # The existing M4.4 audit still handles RC/step correctness, 048
    # compile-only and 052/093 BCPLM6 expected-RC reconciliation.
    cmd = [sys.executable, "tools/checks/check-m44-full-panel-logs.py"]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    require(result.returncode == 0 and
            "M4.4 detailed log audit: PASS" in result.stdout and
            "M4.4 existing regression logs: 145/145" in result.stdout,
            "saved per-case job/RC audit did not pass")
    require(M44_MANIFEST.is_file(), "M4.4 job/step manifest missing")
    ended_ns = time.time_ns()
    receipt = {
        "schema": "bcpl-m55-fresh-panel-receipt-v1",
        "status": "VERIFIED_AWAITING_OWNER_ACCEPTANCE",
        "git_sha": rev,
        "candidate_profile": PROFILE,
        "started_ns": start_ns,
        "verified_ns": ended_ns,
        "pass": 145,
        "fail": 0,
        "skip": [83],
        "per_case_fresh_logs": 145,
        "runner_transcript_sha256": digest(TRANSCRIPT.read_bytes()),
        "audit_manifest_sha256": digest(M44_MANIFEST.read_bytes()),
        "jobs_manifest": str(M44_MANIFEST.relative_to(ROOT)),
        "log_directory": str(LOGS.relative_to(ROOT)),
        "original_m5_qsam_evidence_jobs": [8184, 8185, 8186],
        "limitations": (
            "Previously accepted case-124 QSAM physical proof does not "
            "establish original raw JES2 spool bytes; no DEVOBJ->OBJ promotion."
        ),
    }
    with RECEIPT.open("x", encoding="utf-8") as out:
        json.dump(receipt, out, indent=2)
        out.write("\n")
    print("M5.5 fresh DEVOBJ native panel evidence: PASS")
    print("  145 fresh logs; 145 PASS, 0 FAIL, expected SKIP 083")
    print("  Per-case M4.4 job/step audit: PASS")
    print(f"  Receipt: {RECEIPT.relative_to(ROOT)}")
    print("  Final milestone owner acceptance: STILL REQUIRED")


def main(argv: list[str]) -> None:
    if argv == ["begin"]:
        begin()
    elif argv == ["verify"]:
        verify()
    else:
        raise ValueError("usage: m55-final-evidence.py begin|verify")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError,
            json.JSONDecodeError) as exc:
        sys.exit(f"M5.5 evidence: FAIL: {exc}")
