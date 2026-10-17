#!/usr/bin/env python3
"""M4.4 source-only compatibility preflight; DOES NOT submit MVS jobs."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "native-compiler" / "regression"
END = 145
ACCOUNTING = {
    139: "counters",
    140: "counters-terminal",
    141: "counters-terminal",
    142: "counters-fault-descriptor32",
    143: "counters-fault-buffer268",
    144: "counters-fault-handle16",
    145: "counters-fault-open-before-svc19",
}
CANDIDATE_ENV = {
    "BCPL_RUNTIME_PDS": "1",
    "BCPL_RUNTIME_LIBRARY": "DEVOBJ",
    "BCPL_RUNTIME_CANDIDATE": "1",
    "BCPL_RUNTIME_CANDIDATE_MEMBER": "BCPLM6",
}


def require(condition: bool, problem: str) -> None:
    if not condition:
        raise ValueError(problem)


def read(path: Path) -> str:
    require(path.is_file(), f"missing file {path}")
    return path.read_text(encoding="ascii")


def check(require_candidate: bool) -> None:
    # Consult the real runner's numbering and test discovery rules.
    runner_path = ROOT / "tools/native/run-regression"
    runner = runpy.run_path(str(runner_path), run_name="m44_preflight")
    cases, highest = runner["discover"]()
    require(highest == END, f"regression last test {highest}; expected {END}")
    require(set(cases) == set(range(END + 1)),
            f"missing or extra numbers in 00..{END}")
    for n, case in sorted(cases.items()):
        directory = REG / case
        require((directory / "source.bcpl").is_file(),
                f"test {n}: missing BCPL source")
        require((directory / "README.md").is_file(),
                f"test {n}: missing README")
        require((directory / "candidate-only.txt").is_file() == (n >= 124),
                f"test {n}: unexpected candidate-only marker")
        if n in ACCOUNTING:
            require(read(directory / "io-accounting.txt").strip()
                    == ACCOUNTING[n],
                    f"test {n}: M4.3 private accounting mode changed")
            source = read(directory / "source.bcpl")
            require(all(len(row) <= 80 for row in source.splitlines()),
                    f"test {n}: source record exceeds 80 columns")
        elif (directory / "io-accounting.txt").exists():
            raise ValueError(f"test {n}: unplanned private accounting marker")

    expected_faults = {
        135: "descriptor32", 136: "buffer268", 137: "handle16"
    }
    for n, mode in expected_faults.items():
        require(read(REG / cases[n] / "io-fault-mode.txt").strip() == mode,
                f"test {n}: allocation fault fixture changed")
    require(read(REG / cases[138] / "io-open-fault.txt").strip()
            == "before-svc19", "regression 138 fault changed")
    require(read(REG / cases[141] / "expected-go-rc.txt").strip()
            == "0008", "regression 141 expected STOP(8) changed")

    runner_source = read(runner_path)
    require("if installed_pds and test_no == 83:" in runner_source,
            "expected source-only SKIP 083 has changed")
    require('and os.environ.get("BCPL_RUNTIME_CANDIDATE_MEMBER") == "BCPLM6"'
            in runner_source, "DEVOBJ BCPLM6 candidate gate changed")
    harness = read(REG / "run-test.sh")
    for anchor in (
        'pds_args+=(--test-io-asm "$account_asm")',
        'account_args+=(--terminal-check)',
        'counters-fault-*',
    ):
        require(anchor in harness, f"M4.3 private harness changed: {anchor}")
    canonical = read(ROOT / "native-compiler/asm/bcplio.asm")
    require(not any(mark in canonical for mark in
                    ("M43G32", "M43TRAP", "IOACCT", "F43PH")),
            "private instrumentation leaked into canonical BCPLIO")
    require((ROOT / "tools/checks/check-bcplio-m43-account.py").is_file(),
            "M4.3 source checker missing")

    if require_candidate:
        for key, wanted in CANDIDATE_ENV.items():
            require(os.environ.get(key) == wanted,
                    f"{key}={os.environ.get(key)!r}, expected {wanted!r}")

    print("M4.4 source-only compatibility preflight: PASS")
    print("Corpus: 00..145, 146 numbered cases; no gaps")
    print("Expected full panel: 145 PASS / 0 FAIL / 1 SKIP (083)")
    print("Candidate-only cases: 124..145")
    print("Private test-only accounting: 139..145; canonical BCPLIO clean")
    print("Candidate environment: " +
          ("PASS" if require_candidate else "NOT CHECKED"))
    print("MVS/JES execution: NOT PERFORMED")
    print("Full-panel compatibility: NOT VERIFIED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="store_true",
                        help="verify the four DEVOBJ BCPLM6 env variables")
    args = parser.parse_args()
    try:
        check(args.candidate)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"M4.4 preflight: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
