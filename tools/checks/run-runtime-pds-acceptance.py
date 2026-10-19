#!/usr/bin/env python3
"""Run the installed production-object PDS acceptance suite (exclude 083).

Test 083 requires private FREEMAIN counters unavailable in installed objects.
Do not conflate the separate instrumented two-object probe with this suite.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools/bootstrap/run-regression"
RANGES = ((0, 82, 83), (84, 119, 36))


def main() -> int:
    if os.environ.get("BCPL_RUNTIME_PDS") not in (None, "1"):
        print("Refusing conflicting BCPL_RUNTIME_PDS setting", file=sys.stderr)
        return 64
    env = os.environ.copy()
    env["BCPL_RUNTIME_PDS"] = "1"
    totals = {"PASS": 0, "FAIL": 0, "TOTAL": 0}
    for start, end, required in RANGES:
        print(f"=== Installed production PDS: {start:03d}..{end:03d} ===",
              flush=True)
        proc = subprocess.run(
            [sys.executable, str(RUNNER), str(start), str(end)],
            cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(proc.stdout, end="", flush=True)
        counts = {}
        for key in totals:
            match = re.findall(rf"(?m)^{key}\s+(\d+)\s*$", proc.stdout)
            if len(match) != 1:
                print(f"Acceptance blocked: missing/ambiguous {key} count",
                      file=sys.stderr)
                return 1
            counts[key] = int(match[0])
        if (counts["TOTAL"] != required or
            counts["PASS"] + counts["FAIL"] != required or
            (proc.returncode == 0) != (counts["FAIL"] == 0)):
            print("Acceptance blocked: inconsistent range results",
                  file=sys.stderr)
            return 1
        for key in totals:
            totals[key] += counts[key]
    print("\nINSTALLED PRODUCTION RUNTIME PDS ACCEPTANCE")
    for key in ("PASS", "FAIL", "TOTAL"):
        print(f"{key}  {totals[key]}")
    print("EXCLUDED 083 (test-only reclamation instrumentation)")
    if totals["TOTAL"] != 119 or totals["FAIL"] != 0:
        print("STATUS NOT ACCEPTED")
        return 1
    print("STATUS ACCEPTED: 119/119 production-object behavior tests")
    print("Independent 083 counter evidence: JOB 6295; not part of this run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
