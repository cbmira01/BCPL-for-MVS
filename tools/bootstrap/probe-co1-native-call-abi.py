#!/usr/bin/env python3
"""CO.1 native CG370 checked-entry four-argument/nested-call compile-only probe.

Generates textual System/370 assembler through ICINT19. Does not assemble,
link-edit, GO, install native objects, or modify persistent MVS datasets.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "packaging/milestones/coroutines/probes/co1-abi"
SOURCE = PROBE / "source.bcpl"
PARM = PROBE / "cambridge-parm.txt"
COMPILER = ROOT / "tools/bootstrap/compile-mvs"
WORKAREA = ROOT / "workarea/co1-native-call-abi"

ENTRY = re.compile(
    r"^[ \t]*BAL[ \t]+14,[ \t]*60\(11\)[^\n]*\n"
    r"[ \t]*DC[ \t]+A\(L(\d+)\)[ \t]+STACK FRAME SIZE[ \t]*$", re.M
)
RAW_ENTRY = re.compile(r"^[ \t]*BAL[ \t]+14,[ \t]*60\(11\)", re.M)
FRAME = re.compile(r"^L(\d+)[ \t]+EQU[ \t]+(\d+)[ \t]+STACK FRAME SIZE[ \t]*$", re.M)
FOUR_FORMAL = re.compile(r"^[ \t]*STM[ \t]+4,10,0\(15\)", re.M)
CALL = re.compile(r"^[ \t]*BALR[ \t]+6,4\b", re.M)
RETURN = re.compile(r"^[ \t]*BCR[ \t]+15,11\b", re.M)
WORKSPACE = re.compile(r"^[ \t]*LA[ \t]+15,[0-9]+\(5\)", re.M)
WRONG_ENTRY = re.compile(r"^[ \t]*BAL[ \t]+14,(?:20|80)\(11\)", re.M)
JOB = re.compile(r"(?m)^JOB[ \t]+(\d+)[ \t]*$")


class ProbeError(ValueError):
    """Compiler output does not match this isolated checked native ABI oracle."""


def verify_assembler(source: str) -> dict[str, object]:
    """Inspect only emitted code shape; does not prove runtime register liveness."""
    entries = list(ENTRY.finditer(source))
    raw_count = len(RAW_ENTRY.findall(source))
    if raw_count < 3 or len(entries) != raw_count:
        raise ProbeError(f"expected 3 complete +60 entries; {len(entries)}/{raw_count} complete")
    if WRONG_ENTRY.search(source):
        raise ProbeError("unexpected +20/+80 counting service in /CN code")
    if len(FOUR_FORMAL.findall(source)) != 1:
        raise ProbeError("expected exactly one STM 4,10,0(15) four-argument callee")
    call_count = len(CALL.findall(source))
    if call_count < 3:
        raise ProbeError(f"expected at least three BALR 6,4 calls, found {call_count}")
    if not RETURN.search(source):
        raise ProbeError("missing BCR 15,11 system-vector return")
    if not WORKSPACE.search(source):
        raise ProbeError("missing LA 15,n(5) checked-call workspace formation")
    definitions: dict[str, list[int]] = {}
    for match in FRAME.finditer(source):
        definitions.setdefault(match.group(1), []).append(int(match.group(2)))
    frames: list[int] = []
    for match in entries:
        sizes = definitions.get(match.group(1), [])
        if len(sizes) != 1 or sizes[0] <= 0 or sizes[0] % 4:
            raise ProbeError(f"invalid, missing or duplicate frame EQU L{match.group(1)}")
        frames.append(sizes[0])
    return {"checked_entries": raw_count, "four_argument_entry": 1,
            "ordinary_calls": call_count, "frame_sizes_bytes": frames}


def run() -> int:
    os.umask(0o077)
    WORKAREA.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-", dir=WORKAREA
    ))
    log, generated, evidence = (folder / item for item in
                                ("compiler.log", "generated.s370.asm", "summary.json"))
    result: dict[str, object] = {
        "probe": "CO.1 checked native four-argument and nested-call ABI",
        "status": "FAIL", "assembled": False, "linked": False, "native_go": False,
    }
    try:
        if PARM.read_text(encoding="ascii").splitlines() != ["/CN" + "/" * 77]:
            raise ProbeError("parameter file must contain one 80-column /CN record")
        if not SOURCE.is_file() or not COMPILER.is_file():
            raise ProbeError("source or resident Cambridge compiler driver is missing")
        source = SOURCE.read_text(encoding="ascii")
        if "LET SUM4(A,B,C,D)" not in source or "LET WRAP(X,Y)" not in source:
            raise ProbeError("four-argument/nested-call fixture has changed")
        result["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        result["parm_sha256"] = hashlib.sha256(PARM.read_bytes()).hexdigest()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              text=True, capture_output=True, check=False)
        result["git_head"] = head.stdout.strip() if head.returncode == 0 else "unknown"
        cmd = [sys.executable, str(COMPILER), str(SOURCE),
               "--compiler-image", "CAMBCOMP", "--job-name", "CO1ABI",
               "--cambridge-parm", str(PARM), "--output", str(generated)]
        with log.open("w", encoding="utf-8") as handle:
            proc = subprocess.run(cmd, cwd=ROOT, stdout=handle,
                                  stderr=subprocess.STDOUT, check=False)
        result["compiler_driver_rc"] = proc.returncode
        jobs = JOB.findall(log.read_text(encoding="utf-8", errors="replace"))
        if len(jobs) == 1:
            result["jes_job_id"] = jobs[0]
        if proc.returncode:
            raise ProbeError(f"resident compiler RC={proc.returncode}")
        if len(jobs) != 1:
            raise ProbeError("expected exactly one reported JES job number")
        if not generated.is_file() or not generated.stat().st_size:
            raise ProbeError("generated assembler missing or empty")
        checked = verify_assembler(generated.read_text(encoding="latin-1"))
        result.update(checked)
        result["status"] = "PASS"
        print(f"CO.1 ABI PASS: JOB {jobs[0]}, four-arg entry 1, "
              f"checked entries {checked['checked_entries']}, "
              f"calls {checked['ordinary_calls']}; compile-only")
        return 0
    except (OSError, UnicodeError, ProbeError) as exc:
        result["reason"] = str(exc)
        print(f"CO.1 ABI FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        evidence.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"CO.1 ABI evidence: {folder.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(run())
