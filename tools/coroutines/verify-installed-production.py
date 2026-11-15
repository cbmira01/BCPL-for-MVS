#!/usr/bin/env python3
"""Check production coroutine objects through installed-only IEWL/GO.

Independent application compile; BOOT_OBJ(BCPLMAIN), BCPLCO and COROUTIN
are selected as binary installed objects, not rebuilt from candidate sources.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "tools/coroutines/run-co3-first-lifecycle.py"
ADAPTER = ROOT / "tools/coroutines/run-co3-delete-reuse.py"
FIXTURE = ROOT / "packaging/milestones/coroutines/candidates/co3-delete-reuse"
EVIDENCE = ROOT / "workarea/co5-installed-coroutines"
PREP = ROOT / "tools/coroutines/prepare-production-library.py"
STEPS = ("ASMA", "LKED", "GO")
JOB = "COPRVER"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_deck(driver, listing: str, jobcard: list[str], dsn: str) -> str:
    if not jobcard or not jobcard[0].startswith("//COPRVER "):
        raise ValueError("unrecognized authenticated COPRVER jobcard")
    cards = [*jobcard,
             "//* CO.5 INSTALLED OBJECTS ONLY; NO PERSISTENT WRITE."]
    cards += driver.co2.asm_step(
        "ASMA", "COPROBJ", driver.generated_application(listing))
    cards += [
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE)",
        f"//OBJ      DD DSN={dsn},DISP=SHR",
        "//SYSLIN   DD DSN=&&COPROBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(COROUTIN)",
        " INCLUDE OBJ(BCPLCO)",
        " INCLUDE OBJ(BCPLIO)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BCPLRGS)",
        " INCLUDE OBJ(BCPLREG)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY CO3APP",
        " NAME COPRVER(R)",
        "/*",
        "//SYSLMOD  DD DSN=&&COLMOD(COPRVER),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE,LKED)",
        "//SYSPRINT DD SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    for n, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"invalid JCL/IFOX card {n}: {row!r}")
    if cards.count("/*") != 2 or "DISP=(NEW,CATLG)" in "\n".join(cards):
        raise ValueError("unsafe JCL output or delimiters")
    return "\n".join(cards) + "\n"


def assess(summary: str, report: str, job_id: str, expected) -> dict:
    if not re.search(rf"^JOB\s+{re.escape(job_id)}\s+{JOB}\s*$",
                     summary, re.M):
        raise ValueError("wrong installed-link native JES identity")
    if "JOB RESULT: SUCCESS" not in summary or "HIGHEST RC: 0000" not in summary:
        raise ValueError("JES completion unsuccessful")
    found = {}
    for row in summary.splitlines():
        m = re.fullmatch(r"\s*(ASMA|LKED|GO)\s+.*?RC=(\d{4})\s*", row)
        if m:
            if m.group(1) in found:
                raise ValueError("duplicate JES step")
            found[m.group(1)] = int(m.group(2))
    if set(found) != set(STEPS) or any(found.values()):
        raise ValueError(f"missing/nonzero installed-link steps: {found}")
    actual = [row.strip() for row in report.replace("\f", "").splitlines()
              if row.strip().startswith("CO3BCPL")]
    required = ["CO3BCPL " + marker for marker in expected]
    if actual != required:
        raise ValueError(f"wrong installed 21-record oracle: {actual}")
    return {"steps": found, "bcpl_records": actual}


def preflight() -> None:
    ck = subprocess.run([sys.executable, "-B", str(PREP), "--check"],
                        cwd=ROOT, capture_output=True, text=True, timeout=45)
    if ck.returncode:
        raise ValueError(f"production source preflight failed: {ck.stderr}")
    main = (ROOT / "bootstrap-toolchain/asm/bcplmain.asm").read_text("ascii")
    bridge = (ROOT / "bootstrap-toolchain/asm/bcplco-production.asm").read_text("ascii")
    if "         ENTRY STKOVFL,STKLIM\n" not in main:
        raise ValueError("canonical BCPLMAIN missing STKLIM export")
    if bridge.count("         ENTRY CO3DROP\n") != 1:
        raise ValueError("production BCPLCO missing CO3DROP export")


def run() -> int:
    os.umask(0o077)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-",
        dir=EVIDENCE))
    result = {"status": "FAIL", "installed_objects_modified": False,
              "linkage": "installed BOOT_OBJ(BCPLMAIN/BCPLCO/COROUTIN)"}
    try:
        preflight()
        driver = load("co5_installed_base", BASE)
        adapter = load("co5_installed_adapter", ADAPTER)
        adapter.configure(driver)
        driver.require_mvs_tools()
        parm = FIXTURE / "cambridge-parm.txt"
        if parm.read_text("ascii").splitlines() != ["/CN" + "/" * 77]:
            raise ValueError("expected checked Cambridge /CN frames")
        source = FIXTURE / "source.bcpl"
        result["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        result["git_head"] = driver.co2.shell(
            ["git", "rev-parse", "HEAD"], timeout=15).stdout.strip()
        listing = folder / "application-generated.asm"
        compiler = driver.co2.shell([
            sys.executable, "-B", str(driver.COMPILER), str(source),
            "--job-name", "COPRCMP", "--cambridge-parm", str(parm),
            "--output", str(listing)], timeout=240)
        (folder / "compiler.log").write_text(compiler.stdout + compiler.stderr)
        jobs = driver.JOB_RE.findall(compiler.stdout)
        if compiler.returncode or len(jobs) != 1 or not listing.is_file():
            raise ValueError("native installed-test application compile failed")
        result["compiler_job"] = jobs[0]
        jobcard, dsn = driver.config_and_object()
        if not jobcard[0].startswith("//CO3BGO "):
            raise ValueError("unexpected authenticated jobcard")
        jobcard[0] = jobcard[0].replace("//CO3BGO ", "//COPRVER ", 1)
        deck = build_deck(driver, listing.read_text("latin-1"),
                          jobcard, dsn)
        (folder / "installed.jcl").write_text(deck, encoding="ascii")
        launch = driver.co2.shell([
            str(driver.SUBMIT), "--cursor-file",
            str(folder / "printer.cursor"), str(folder / "installed.jcl")],
            timeout=140)
        (folder / "submission.log").write_text(launch.stdout + launch.stderr)
        jobs = driver.JOB_RE.findall(launch.stdout)
        if launch.returncode or len(jobs) != 1:
            raise ValueError("installed-link GO submission failed")
        job_id = jobs[0]
        result["native_job"] = job_id
        deadline = time.monotonic() + 200
        summary = ""
        while time.monotonic() < deadline:
            check = driver.co2.shell([
                str(driver.SUMMARY), job_id, "--cursor-file",
                str(folder / "printer.cursor"), "--max-rc", "0"],
                timeout=25)
            summary = check.stdout + check.stderr
            (folder / "job-summary.log").write_text(summary)
            if check.returncode in (0, 1):
                break
            time.sleep(2)
        else:
            raise ValueError("no complete JES summary from installed job")
        report = driver.co2.shell([
            str(driver.REPORT), job_id, "--cursor-file",
            str(folder / "printer.cursor")], timeout=45)
        (folder / "report.log").write_text(report.stdout + report.stderr)
        if report.returncode:
            raise ValueError("installed native report not available")
        result.update(assess(summary, report.stdout, job_id, driver.EXPECTED))
        result["status"] = "PASS"
        print(f"INSTALLED COROUTINES PASS: compiler JOB "
              f"{result['compiler_job']}, native JOB {job_id}; "
              f"IFOX/IEWL/GO all RC=0000")
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result["reason"] = str(exc)
        print(f"INSTALLED COROUTINES FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"Installed coroutine evidence: {folder.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="source preflight")
    parser.add_argument("--run", action="store_true", help="submit MVS jobs")
    args = parser.parse_args()
    if args.check and not args.run:
        preflight()
        print("Installed coroutine verification source checks PASS")
        return 0
    if not args.run:
        parser.error("MVS execution requires explicit --run")
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
