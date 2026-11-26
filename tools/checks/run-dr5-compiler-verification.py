#!/usr/bin/env python3
"""DR.5 focused GET and compiler-option probes; no resident writes."""
import argparse
import json
import os
from pathlib import Path
import re
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
COMMON = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
FIX = ROOT / "packaging/milestones/documentation-refactoring/candidates/compiler-verification"
require = COMMON["require"]
run = COMMON["run"]
receipt = COMMON["receipt"]


def check():
    cases = [("nested", "GET"), ("suppressed", "N"), ("cambridge", "HDR")]
    expected = {}
    for stem, label in cases:
        expected[stem] = COMMON["check_candidate"](
            FIX / (stem + ".bcpl"), FIX / (stem + ".expected"), (label,))
    for name in ("outer.h", "inner.h", "mr10-options.txt", "cambridge-options.txt"):
        lines = (FIX / name).read_text("ascii").splitlines()
        require(lines and all(len(x) <= 80 and "\t" not in x for x in lines),
                "invalid input cards: " + name)
    require((FIX / "mr10-options.txt").read_text("ascii") == "L6000N\n", "MR10 options")
    require((FIX / "cambridge-options.txt").read_text("ascii") ==
            "J12Q/N/".ljust(80, "/") + "\n", "Cambridge options")
    return expected


def mr10(folder, env, stem, jobname, bindings, expected):
    args = ["tools/mr10/compile-and-run", "--installed-icint", "MR10_LOAD",
            "--results", "--job-name", jobname, "--jcl", folder / (stem + ".jcl")]
    for dd, path in bindings:
        args += ["--dd", dd + "=" + str(FIX / path)]
    args.append(FIX / (stem + ".bcpl"))
    rc, output = COMMON["command"](args, folder / (stem + ".log"), env)
    job = COMMON["job_id"](output)
    report = receipt(folder, job, jobname, COMMON["MR_STEPS"], env)
    require(rc == 0, "MR10 driver returned nonzero")
    observed = COMMON["assess"](report, expected, [0, 0, 0], "INTCODE SYSTEM ENTERED")
    if stem == "suppressed":
        require(re.search(r"OPTIONS\s+L6000N\b", report), "missing numeric-option echo")
    return {"job": job, "records": observed}


def cambridge(folder, env, expected):
    generated = folder / "cambridge.asm"
    output = run(["tools/bootstrap/compile-mvs", FIX / "cambridge.bcpl",
                  "--job-name", "DR5CGET", "--compiler-image", "CAMBCOMP",
                  "--cambridge-parm", FIX / "cambridge-options.txt", "--output", generated],
                 folder / "cambridge-compile.log", env)
    comp = COMMON["job_id"](output)
    report = receipt(folder, comp, "DR5CGET", COMMON["CC_STEPS"], env)
    require([int(x) for x in COMMON["CODE"].findall(report)] == [0], "Cambridge CODE")
    require("UNKNOWN COMPILATION OPTION J IGNORED" in report.upper(), "missing first-phase warning")
    require(not any(x in report.upper() for x in ("TREE SIZE", "OCODE SIZE =", "COMPILATION SUCCESSFUL")),
            "Q did not suppress ordinary phase diagnostics")
    deck = folder / "cambridge.jcl"
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py", generated, deck,
         "--test-number", "904"], folder / "cambridge-build.log", env)
    cursor = folder / "cambridge.cursor"
    output = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                 folder / "cambridge-submit.log", env)
    job = COMMON["job_id"](output)
    report = receipt(folder, job, "RG904R", COMMON["GO_STEPS"], env, cursor)
    observed = COMMON["assess"](report, expected, boundary="AUTHORIZATION CODE IS")
    return {"compiler_job": comp, "job": job, "records": observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    expected = check()
    if args.check:
        print("DR.5 compiler inputs CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    base = ROOT / "workarea/dr5-compiler-verification"
    base.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {"git_head": run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip(),
              "paths": {}}
    actions = [("mr10-nested", lambda: mr10(folder, env, "nested", "DR5MGET",
                   [("DR5INC", "outer.h"), ("DR5NEST", "inner.h")], expected["nested"])),
               ("mr10-suppressed", lambda: mr10(folder, env, "suppressed", "DR5MNGET",
                   [("OPTIONS", "mr10-options.txt")], expected["suppressed"])),
               ("cambridge", lambda: cambridge(folder, env, expected["cambridge"]))]
    for name, action in actions:
        try:
            result["paths"][name] = {"status": "PASS", **action()}
        except (OSError, ValueError, COMMON["subprocess"].TimeoutExpired) as exc:
            result["paths"][name] = {"status": "FAIL", "reason": str(exc)}
            print("DR.5 " + name + " FAIL; stopping before further jobs")
            break
        print("DR.5 " + name + " PASS", flush=True)
    result["status"] = ("PASS" if len(result["paths"]) == len(actions) and
                        all(x["status"] == "PASS" for x in result["paths"].values()) else "FAIL")
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
