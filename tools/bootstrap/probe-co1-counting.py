#!/usr/bin/env python3
"""CO.1: compile-only System/370 /CPN counting-site emission probe."""
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
SOURCE = ROOT / "tests/bootstrap/51-checked-recursion/source.bcpl"
PARM = ROOT / "packaging/milestones/coroutines/probes/co1-counting/cambridge-parm.txt"
COMPILER = ROOT / "tools/bootstrap/compile-mvs"
WORKAREA = ROOT / "workarea/co1-counting"

BRANCH80 = re.compile(r"^\s*BAL\s+14\s*,\s*80\s*\(\s*11\s*\)", re.M)
ENTRY80 = re.compile(
    r"^\s*BAL\s+14\s*,\s*80\s*\(\s*11\s*\)[^\n]*\n"
    r"\s*DC\s+F\s*'0'[^\n]*\n"
    r"\s*DC\s+A\s*\(\s*L(\d+)\s*\)\s+STACK FRAME SIZE[^\n]*$", re.M)
BRANCH20 = re.compile(r"^\s*BAL\s+14\s*,\s*20\s*\(\s*11\s*\)", re.M)
ENTRY20 = re.compile(
    r"^\s*BAL\s+14\s*,\s*20\s*\(\s*11\s*\)[^\n]*\n"
    r"\s*DC\s+F\s*'0'[^\n]*$", re.M)
FRAMES = re.compile(r"^L(\d+)\s+EQU\s+(\d+)\s+STACK FRAME SIZE\s*$", re.M)
BRANCH60 = re.compile(r"^\s*BAL\s+14\s*,\s*60\s*\(\s*11\s*\)", re.M)
CALL = re.compile(r"^\s*BALR\s+6\s*,\s*4\b", re.M)
JOB = re.compile(r"(?m)^JOB\s+(\d+)\s*$")


class ProbeError(ValueError):
    pass


def verify_assembler(source: str) -> dict[str, object]:
    entries80 = list(ENTRY80.finditer(source))
    entries20 = list(ENTRY20.finditer(source))
    raw80, raw20 = len(BRANCH80.findall(source)), len(BRANCH20.findall(source))
    if raw80 < 2 or len(entries80) != raw80:
        raise ProbeError(f"expected >=2 complete +80 entries; {len(entries80)}/{raw80} complete")
    if raw20 < 1 or len(entries20) != raw20:
        raise ProbeError(f"expected >=1 complete +20 counter site; {len(entries20)}/{raw20} complete")
    if BRANCH60.search(source):
        raise ProbeError("unexpected +60 checked-only entry")
    if CALL.search(source) is None:
        raise ProbeError("missing ordinary BALR 6,4 call")
    definitions: dict[str, list[int]] = {}
    for m in FRAMES.finditer(source):
        definitions.setdefault(m.group(1), []).append(int(m.group(2)))
    sizes = []
    for m in entries80:
        frames = definitions.get(m.group(1), [])
        if len(frames) != 1 or frames[0] <= 0 or frames[0] % 4:
            raise ProbeError(f"invalid or nonunique frame size L{m.group(1)}")
        sizes.append(frames[0])
    return {"checked_counted_entries": raw80, "additional_count_sites": raw20,
            "frame_sizes_bytes": sizes}


def run() -> int:
    os.umask(0o077)
    WORKAREA.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-", dir=WORKAREA))
    log, generated, summaryfile = (folder / x for x in
        ("compiler.log", "generated.s370.asm", "summary.json"))
    summary: dict[str, object] = {
        "probe": "CO.1 /CPN additional counting-site compile-only",
        "status": "FAIL", "assembled": False, "linked": False, "native_go": False,
    }
    try:
        options = PARM.read_text(encoding="ascii").splitlines()
        if options != ["/CPN" + "/" * 76]:
            raise ProbeError("expected one 80-column /CPN parameter record")
        if not SOURCE.is_file() or not COMPILER.is_file():
            raise ProbeError("missing BCPL source or installed compile driver")
        summary["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        summary["parameter_sha256"] = hashlib.sha256(PARM.read_bytes()).hexdigest()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              text=True, capture_output=True, check=False)
        summary["git_head"] = head.stdout.strip() if head.returncode == 0 else "unknown"
        command = [sys.executable, str(COMPILER), str(SOURCE),
                   "--compiler-image", "CAMBCOMP", "--job-name", "CO1CNP",
                   "--cambridge-parm", str(PARM), "--output", str(generated)]
        with log.open("w", encoding="utf-8") as handle:
            proc = subprocess.run(command, cwd=ROOT, stdout=handle,
                                  stderr=subprocess.STDOUT, check=False)
        summary["compiler_driver_rc"] = proc.returncode
        jobs = JOB.findall(log.read_text(encoding="utf-8", errors="replace"))
        if len(jobs) == 1:
            summary["jes_job_id"] = jobs[0]
        if proc.returncode:
            raise ProbeError(f"compiler driver RC={proc.returncode}")
        if len(jobs) != 1:
            raise ProbeError("expected exactly one reported JES job number")
        if not generated.is_file() or not generated.stat().st_size:
            raise ProbeError("empty or missing generated assembler")
        metrics = verify_assembler(generated.read_text(encoding="latin-1"))
        summary.update(metrics)
        summary["status"] = "PASS"
        print(f"CO.1 COUNT-P PASS: JOB {jobs[0]}, +80={metrics['checked_counted_entries']}, "
              f"+20={metrics['additional_count_sites']}; compile-only")
        return 0
    except (OSError, UnicodeError, ProbeError) as exc:
        summary["reason"] = str(exc)
        print(f"CO.1 COUNT-P FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        summaryfile.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"CO.1 COUNT-P evidence: {folder.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(run())
