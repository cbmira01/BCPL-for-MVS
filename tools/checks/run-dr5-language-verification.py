#!/usr/bin/env python3
"""DR.5 one shared BCPL source, two independent MVS execution paths."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "packaging/milestones/documentation-refactoring/candidates/language-verification"
SOURCE = FIX / "source.bcpl"
EXPECTED = FIX / "expected.txt"
DIAG_SOURCE = FIX / "native-shift-diagnostic.bcpl"
DIAG_EXPECTED = FIX / "native-shift-diagnostic.expected"
CODE = re.compile(r"EXECUTION CYCLES\s*=\s*\d+,\s*CODE\s*=\s*(-?\d+)")
JOB = re.compile(r"^JOB\s+(\d+)\s*$", re.M)
STEP = re.compile(r"^[ \t]*([A-Z0-9]+)[ \t]+(\S*?)[ \t]+RC=(\d{4})[ \t]*$", re.M)
MR_STEPS = [(name, "IEBGENER") for name in
            ("STGSYNI", "STGTRNI", "STGCGI", "STGBLIB", "STGICLIB")]
MR_STEPS += [(name, "ICINT19") for name in ("COMP", "CG", "RUN")]
CC_STEPS = [("COMP", "ICINT19"), ("SVCODE", "IEBGENER")]
GO_STEPS = [("ASMAP", "IFOX00"), ("LKED", "IEWL"), ("GO", "PGM=*.LKED.SYSLMOD")]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def records(report):
    return [line.strip() for line in report.replace("\f", "").splitlines()
            if line.strip().startswith("RP: DR5")]


def assess(report, expected, codes=None, boundary=None):
    if codes is not None:
        require([int(x) for x in CODE.findall(report)] == codes,
                "interpreted completion codes differ")
    if boundary:
        require(boundary in report, "missing execution boundary")
        report = report.rsplit(boundary, 1)[1]
    actual = records(report)
    require(actual == expected, "observed records differ: " + repr(actual))
    return actual


def check_candidate(source, oracle, labels):
    raw = source.read_bytes()
    rows = raw.decode("ascii").splitlines()
    require(rows and all(len(x) <= 80 and "\t" not in x and
                         not x.startswith(("//", "/*")) for x in rows),
            "invalid BCPL source card")
    expected = oracle.read_text("ascii").splitlines()
    require([x.split()[2] for x in expected] == list(labels),
            "oracle labels differ")
    require(all(x.startswith("RP: DR5 ") for x in expected),
            "invalid oracle record")
    require(assess("INTCODE SYSTEM ENTERED\n" + "\n".join(expected) +
                   "\nEXECUTION CYCLES = 1, CODE = 0", expected, [0],
                   "INTCODE SYSTEM ENTERED") == expected, "parser self-check")
    for wrong in (expected[:-1], expected + expected[-1:], expected[::-1]):
        try:
            assess("\n".join(wrong), expected)
        except ValueError:
            pass
        else:
            raise ValueError("oracle accepted missing, duplicate or unordered records")
    require(STEP.findall("ASMAP      IFOX00       RC=0000\n"
                         "LKED       IEWL         RC=0000\n"
                         "GO                      RC=0000\n") ==
            [("ASMAP", "IFOX00", "0000"), ("LKED", "IEWL", "0000"),
             ("GO", "", "0000")], "JES summary parser self-check")
    return expected


def check():
    return check_candidate(SOURCE, EXPECTED,
                           ("ASSIGN", "BOUND", "STEP", "BRANCH", "VALUE",
                            "OR", "SIGNED", "SHIFT", "END"))


def check_diagnostic():
    return check_candidate(DIAG_SOURCE, DIAG_EXPECTED,
                           ("ASSIGN", "BOUND", "STEP", "BRANCH", "VALUE",
                            "OR", "SIGNED", "ISO", "SHIFT", "SHIFT", "END"))


def command(args, log, env):
    with log.open("w", encoding="utf-8") as out:
        p = subprocess.run([str(x) for x in args], cwd=ROOT, env=env,
                           stdout=out, stderr=subprocess.STDOUT, timeout=600)
    return p.returncode, log.read_text("utf-8", errors="replace")


def run(args, log, env):
    rc, text = command(args, log, env)
    require(rc == 0, f"{log.name}: RC={rc}")
    return text


def job_id(text):
    ids = JOB.findall(text)
    require(len(ids) == 1, "expected one JES job number")
    return ids[0]


def receipt(folder, job, name, steps, env, cursor=None):
    cursor_args = ["--cursor-file", cursor] if cursor else []
    end = time.monotonic() + 240
    while True:
        rc, summary = command(["tools/mvs/job-summary", job, "--max-rc", "0",
                               *cursor_args], folder / (name + "-summary.log"), env)
        if rc != 2:
            break
        require(time.monotonic() < end, "JES completion timeout")
        time.sleep(2)
    require(re.search(rf"^JOB\s+{re.escape(job)}\s+{name}\s*$", summary, re.M),
            "JES job identity mismatch")
    report = run(["tools/mvs/dump-report-for-job", job, *cursor_args],
                 folder / (name + "-report.log"), env)
    require(rc == 0 and "JOB RESULT: SUCCESS" in summary and
            "HIGHEST RC: 0000" in summary,
            f"{name} JOB {job}: JES job not successful; " +
            repr(STEP.findall(summary)) + "; records=" +
            repr(records(report.rsplit("AUTHORIZATION CODE IS", 1)[-1])))
    # GO's displayed program field varies with the passed load module;
    # check exact ordered step identities and zero RC, plus fixed programs.
    actual = STEP.findall(summary)
    require(len(actual) == len(steps), "unexpected JES step count")
    for (step, pgm, code), (wanted, wanted_pgm) in zip(actual, steps):
        require(step == wanted and code == "0000" and
                (wanted == "GO" or pgm == wanted_pgm),
                "JES step mismatch: " + repr(actual))
    return report


def mr10(folder, expected, env):
    text = run(["tools/mr10/compile-and-run", "--installed-icint", "MR10_LOAD",
                "--results", "--job-name", "DR5MR10",
                "--jcl", folder / "mr10.jcl", SOURCE],
               folder / "mr10.log", env)
    job = job_id(text)
    report = receipt(folder, job, "DR5MR10", MR_STEPS, env)
    observed = assess(report, expected, [0, 0, 0], "INTCODE SYSTEM ENTERED")
    return {"job": job, "records": observed}


def native(folder, expected, env, diagnostic=False):
    source = DIAG_SOURCE if diagnostic else SOURCE
    compiler_name = "DR5CISO" if diagnostic else "DR5CAMB"
    number = "901" if diagnostic else "900"
    generated = folder / "native.asm"
    text = run(["tools/bootstrap/compile-mvs", source, "--job-name", compiler_name,
                "--compiler-image", "CAMBCOMP", "--cambridge-parm",
                ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                "--output", generated], folder / "native-compile.log", env)
    comp = job_id(text)
    report = receipt(folder, comp, compiler_name, CC_STEPS, env)
    require([int(x) for x in CODE.findall(report)] == [0], "Cambridge CODE not zero")
    require(generated.is_file() and generated.stat().st_size > 0, "missing CODE")
    deck = folder / "native.jcl"
    # Private helper naming arguments only, not suite case numbers.
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py",
         generated, deck, "--test-number", number], folder / "native-build.log", env)
    cursor = folder / "native.cursor"
    text = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
               folder / "native-submit.log", env)
    job = job_id(text)
    report = receipt(folder, job, "RG" + number + "R", GO_STEPS, env, cursor)
    observed = assess(report, expected, boundary="AUTHORIZATION CODE IS")
    return {"compiler_job": comp, "job": job, "records": observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--run-native-diagnostic", action="store_true",
                       help="execute only the isolated native follow-up")
    args = parser.parse_args()
    expected = check()
    diagnostic_expected = check_diagnostic()
    if args.check:
        print("DR.5 source/oracle and parser CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    base = ROOT / "workarea/dr5-language-verification"
    base.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    source = DIAG_SOURCE if args.run_native_diagnostic else SOURCE
    oracle = DIAG_EXPECTED if args.run_native_diagnostic else EXPECTED
    result = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "oracle_sha256": hashlib.sha256(oracle.read_bytes()).hexdigest(),
              "git_head": run(["git", "rev-parse", "HEAD"],
                              folder / "revision.log", env).strip(), "paths": {}}
    actions = (("native-diagnostic", lambda f, e, v: native(f, e, v, True)),) \
        if args.run_native_diagnostic else (("mr10", mr10), ("native", native))
    if args.run_native_diagnostic:
        expected = diagnostic_expected
    for name, action in actions:
        try:
            result["paths"][name] = {"status": "PASS", **action(folder, expected, env)}
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            result["paths"][name] = {"status": "FAIL", "reason": str(exc)}
        print("DR.5 " + name.upper() + " " + result["paths"][name]["status"])
    result["status"] = ("PASS" if all(x["status"] == "PASS"
                        for x in result["paths"].values()) else "FAIL")
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
