#!/usr/bin/env python3
"""Private BLIBBLD positive/negative native build-integrity verification."""
import argparse
import json
import os
from pathlib import Path
import re
import runpy
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
JCL = ROOT / "bootstrap-toolchain/jcl/blibbld.jcl"
PARAM = "P2000/N" + "/" * 73
BAD_PARAM = "P30000/N" + "/" * 72
TARGET = "//SYSUT2   DD DSN=HERC02.BCPL.BOOT.OBJ(BLIB),DISP=SHR"
PRIVATE = ("//SYSUT2   DD DSN=&&PRIVOBJ,UNIT=SYSDA,SPACE=(80,(300,100)),\n"
           "//             DISP=(NEW,DELETE),\n"
           "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)")
STEPS = [("COMP", "ICINT19"), ("COMPRPT", "IEBGENER"),
         ("PREPASM", "IFOX00"), ("PREPLK", "IEWL"),
         ("FIXASM", None), ("ASMBLIB", "IFOX00"), ("INSTALL", "IEBGENER")]
NAMES = ("DR5BLPOS", "DR5BLNEG")
ROW = re.compile(r"(?m)^([A-Z0-9]+)[ \t]+(\S*?)[ \t]+RC=(\d{4})[ \t]*$")
COMPLETION = re.compile(r"(?m)^[ \t]*EXECUTION CYCLES[^\n]*")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def deck_for(body, jobcard, negative=False):
    require(body.count(TARGET) == 1 and body.count(PARAM) == 1,
            "unexpected production JCL anchors")
    require(body.count("COND=(0,NE)") == 6,
            "unexpected all-prior-step guard inventory")
    require("         OPEN  (RPTDCB,(INPUT))" in body and
            body.index("         OPEN  (RPTDCB,(INPUT))") <
            body.index("         OPEN  (INDCB,(INPUT))"),
            "compiler report must precede RAW input")
    body = body.replace(TARGET, PRIVATE)
    if negative:
        body = body.replace(PARAM, BAD_PARAM)
    require("BOOT.OBJ" not in "\n".join(
        row for row in body.splitlines() if not row.startswith("//*")),
        "persistent BOOT_OBJ destination")
    deck = "\n".join(jobcard) + "\n" + body
    require(all(x.isascii() and len(x) <= 80 for x in deck.splitlines()),
            "invalid job card")
    return deck


def assess(job, name, summary, report, rc, negative=False):
    require(re.findall(r"(?m)^JOB\s+(\d+)\s+([A-Z0-9]+)\s*$", summary)
            == [(job, name)], "wrong job identity")
    require(not re.search(r"(?m)^(?:ABEND:|JCL ERROR:)", summary),
            "ABEND or JCL error")
    records = COMPLETION.findall(report)
    expected_code = 8 if negative else 0
    require(len(records) == 1 and re.fullmatch(
        rf"[ \t]*EXECUTION CYCLES = [0-9]+, CODE = {expected_code}[ \t\r]*",
        records[0]), "unexpected compiler completion")
    want = STEPS[:5] if negative else STEPS
    rows = ROW.findall(summary)
    require(len(rows) == len(want), "unexpected executed step inventory")
    for (step, program, code), (wanted, pgm) in zip(rows, want):
        require(step == wanted and (pgm is None or pgm == program) and
                int(code) == (8 if negative and wanted == "FIXASM" else 0),
                "unexpected step/program/RC: " + repr(rows))
    severities = re.findall(r"\bHIGHEST SEVERITY WAS\s+(\d+)\b", report, re.I)
    require(severities == (["0"] if negative else ["0", "0"]),
            "unexpected IFOX severity evidence")
    if negative:
        require(rc == 1 and "JOB RESULT: FAILURE" in summary and
                "HIGHEST RC: 0008" in summary, "negative job not rejected")
        for step, pgm in STEPS[5:]:
            require(re.search(
                rf"(?m)^\s*\d+\.\d+\.\d+\s+JOB\s+{job}\s+{name}\s+"
                rf"{step}\s+{pgm}\s+\*FLUSH\*\s*$", report),
                f"{step} flush not established")
    else:
        require(rc == 0 and "JOB RESULT: SUCCESS" in summary and
                "HIGHEST RC: 0000" in summary and "BYPASSED:" not in summary,
                "positive job not accepted")
    return {"job": job, "compiler_code": expected_code,
            "steps": {step: int(code) for step, _, code in rows},
            "installation_flushed": negative}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = p.parse_args()
    body = JCL.read_text("ascii")
    for negative in (False, True):
        deck_for(body, ["//DR5BLPOS JOB (BCPL),'BLIB TEST',CLASS=A"], negative)
    if args.check:
        print("DR.5 BLIB BUILD CHECK PASS (no MVS)")
        return 0
    common = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
    helper = runpy.run_path(str(ROOT / "tools/checks/run-dr5-bcplio-fix.py"))
    core = helper["CORE"]
    config = core["load_config"]()
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-blib-build"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    env = dict(os.environ)
    result = {"status": "FAIL", "stage": "preflight"}
    try:
        run, command = common["run"], common["command"]
        result["git_head"] = run(["git", "rev-parse", "HEAD"],
                                  folder / "revision.log", env).strip()
        require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                        folder / "tracked-status.log", env).strip(),
                "tracked changes present")
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle.log", env)
        for negative, name in zip((False, True), NAMES):
            result["stage"] = name
            cards = core["authenticated_job_card"](config, name, "BLIB PRIVATE",
                                                    redact_password=False)
            deck = folder / (name + ".jcl")
            deck.write_text(deck_for(body, cards, negative), encoding="ascii")
            cursor = folder / (name + ".cursor")
            output = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                         folder / (name + "-submit.log"), env)
            job = common["job_id"](output)
            deadline = time.monotonic() + 240
            while True:
                rc, summary = command(["tools/mvs/job-summary", job, "--max-rc", "0",
                                       "--cursor-file", cursor],
                                      folder / (name + "-summary.log"), env)
                if rc != 2:
                    break
                require(time.monotonic() < deadline, "JES completion timeout")
                time.sleep(2)
            report = run(["tools/mvs/dump-report-for-job", job, "--cursor-file", cursor],
                         folder / (name + "-report.log"), env)
            result[name] = assess(job, name, summary, report, rc, negative)
        result.update(status="PASS", stage="complete")
    except (OSError, ValueError, RuntimeError) as exc:
        result["reason"] = str(exc)
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 BLIB BUILD EVIDENCE: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
