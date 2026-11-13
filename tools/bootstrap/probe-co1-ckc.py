#!/usr/bin/env python3
"""CO.1 CK-C: compile-only Cambridge /CKN source probe on MVS.

Never assemble, link or run the resulting native assembler.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tests/bootstrap/51-checked-recursion/source.bcpl"
PARM = ROOT / "packaging/milestones/coroutines/probes/co1-ckc/cambridge-parm.txt"
COMPILE = ROOT / "tools/bootstrap/compile-mvs"
WORKAREA = ROOT / "workarea/co1-ckc"

ENTRY = re.compile(
    r"^\s*BAL\s+14\s*,\s*80\s*\(\s*11\s*\)[^\n]*\n"
    r"\s*DC\s+F\s*'0'[^\n]*\n"
    r"\s*DC\s+A\s*\(\s*L(\d+)\s*\)\s+STACK FRAME SIZE[^\n]*$",
    re.MULTILINE,
)
RAW_ENTRY = re.compile(r"^\s*BAL\s+14\s*,\s*80\s*\(\s*11\s*\)", re.MULTILINE)
FRAME = re.compile(
    r"^L(\d+)\s+EQU\s+(\d+)\s+STACK FRAME SIZE\s*$", re.MULTILINE
)
CHECKED_ONLY = re.compile(r"^\s*BAL\s+14\s*,\s*60\s*\(\s*11\s*\)", re.MULTILINE)
CALL = re.compile(r"^\s*BALR\s+6\s*,\s*4\b", re.MULTILINE)
JOB = re.compile(r"(?m)^JOB\s+(\d+)\s*$")


class VerificationError(ValueError):
    """Generated code does not meet the compiler-only ABI oracle."""


def verify_assembler(source: str) -> dict[str, object]:
    """Verify /CK inline metadata without interpreting or executing assembler."""
    matches = list(ENTRY.finditer(source))
    raw_count = len(RAW_ENTRY.findall(source))
    if raw_count < 2 or len(matches) != raw_count:
        raise VerificationError(
            f"expected at least two complete +80 checked-counted entries; "
            f"found {len(matches)} complete of {raw_count} branches"
        )
    if CHECKED_ONLY.search(source):
        raise VerificationError("unexpected +60 checked-only entry in /CK listing")
    if CALL.search(source) is None:
        raise VerificationError("missing generated BALR 6,4 call")

    definitions: dict[str, list[int]] = {}
    for match in FRAME.finditer(source):
        definitions.setdefault(match.group(1), []).append(int(match.group(2)))

    sizes: list[int] = []
    for match in matches:
        label = match.group(1)
        values = definitions.get(label, [])
        if len(values) != 1:
            raise VerificationError(f"L{label}: expected one frame-size EQU; found {len(values)}")
        size = values[0]
        if size <= 0 or size % 4:
            raise VerificationError(f"L{label}: invalid frame size {size}")
        sizes.append(size)
    return {"checked_counted_entries": raw_count, "frame_sizes_bytes": sizes}


def run() -> int:
    os.umask(0o077)
    WORKAREA.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-", dir=WORKAREA
    ))
    compiler_log = folder / "compiler.log"
    generated = folder / "generated.s370.asm"
    result = folder / "summary.json"
    summary: dict[str, object] = {
        "schema": 1,
        "status": "FAIL",
        "probe": "CO.1 CK-C /CKN compile-only",
        "source": str(SOURCE.relative_to(ROOT)),
        "parameter_file": str(PARM.relative_to(ROOT)),
        "compiler_job_name": "CO1CKC",
        "assembled": False,
        "linked": False,
        "native_go": False,
    }
    try:
        options = PARM.read_text(encoding="ascii").splitlines()
        if len(options) != 1 or len(options[0]) != 80 or options[0] != "/CKN" + "/" * 76:
            raise VerificationError("parameter fixture must be an 80-column /CKN record")
        if not SOURCE.is_file() or not COMPILE.is_file():
            raise VerificationError("missing canonical source or Cambridge compiler driver")
        summary["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        summary["parameter_sha256"] = hashlib.sha256(PARM.read_bytes()).hexdigest()
        git = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            text=True, capture_output=True, check=False
        )
        summary["git_head"] = git.stdout.strip() if git.returncode == 0 else "unknown"
        command = [sys.executable, str(COMPILE), str(SOURCE),
                   "--compiler-image", "CAMBCOMP", "--job-name", "CO1CKC",
                   "--cambridge-parm", str(PARM), "--output", str(generated)]
        # Preserve details for diagnosis, not on the WSL console.
        with compiler_log.open("w", encoding="utf-8") as output:
            proc = subprocess.run(command, cwd=ROOT, stdout=output,
                                  stderr=subprocess.STDOUT, check=False)
        summary["compiler_driver_rc"] = proc.returncode
        log_text = compiler_log.read_text(encoding="utf-8", errors="replace")
        ids = JOB.findall(log_text)
        if len(ids) == 1:
            summary["jes_job_id"] = ids[0]
        if proc.returncode:
            raise VerificationError(f"Cambridge compile driver RC={proc.returncode}")
        if len(ids) != 1:
            raise VerificationError("compiler output lacks one unambiguous JOB number")
        if not generated.is_file() or not generated.stat().st_size:
            raise VerificationError("compile driver returned without generated assembler")
        metrics = verify_assembler(generated.read_text(encoding="latin-1"))
        summary.update(metrics)
        summary["status"] = "PASS"
        print(f"CK-C PASS: JOB {ids[0]}, +80 entries {metrics['checked_counted_entries']}; compile-only")
        return 0
    except (OSError, UnicodeError, VerificationError) as exc:
        summary["reason"] = str(exc)
        print(f"CK-C FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        result.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"CK-C evidence: {folder.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(run())
