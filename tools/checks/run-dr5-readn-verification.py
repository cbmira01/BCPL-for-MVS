#!/usr/bin/env python3
"""DR.5 focused native BLIB READN contract verification; no installed writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "packaging/milestones/documentation-refactoring/candidates/readn-verification"


def execute(common, folder, expected, env):
    require, run = common["require"], common["run"]
    generated = folder / "native.asm"
    text = run(["tools/bootstrap/compile-mvs", FIX / "source.bcpl",
                "--job-name", "DR5READN", "--compiler-image", "CAMBCOMP",
                "--cambridge-parm",
                ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                "--output", generated], folder / "compile.log", env)
    comp = common["job_id"](text)
    report = common["receipt"](folder, comp, "DR5READN", common["CC_STEPS"], env)
    require([int(x) for x in common["CODE"].findall(report)] == [0],
            "Cambridge CODE not zero")
    require(generated.is_file() and generated.stat().st_size > 0, "missing CODE")
    deck = folder / "native.jcl"
    # 905 is a private JCL naming parameter, not a numbered suite identity.
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py",
         generated, deck, "--test-number", "905", "--case-dir", FIX],
        folder / "build.log", env)
    cursor = folder / "native.cursor"
    text = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
               folder / "submit.log", env)
    job = common["job_id"](text)
    report = common["receipt"](folder, job, "RG905R", common["GO_STEPS"], env, cursor)
    observed = common["assess"](report, expected, boundary="AUTHORIZATION CODE IS")
    return {"compiler_job": comp, "job": job, "records": observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = parser.parse_args()
    common = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
    expected = common["check_candidate"](FIX / "source.bcpl", FIX / "expected.txt",
                                         ("READN",) * 12)
    rows = (FIX / "input.records").read_text("ascii").splitlines()
    common["require"](len(rows) == 4 and all(row and len(row) <= 80 and
                      not row.startswith(("//", "/*", "ZZ")) for row in rows),
                      "unsafe BCPIN fixture")
    if args.check:
        print("DR.5 READN source/oracle CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    base = ROOT / "workarea/dr5-readn-verification"
    base.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {"inputs": {name: hashlib.sha256((FIX / name).read_bytes()).hexdigest()
                         for name in ("source.bcpl", "expected.txt", "input.records")}}
    try:
        result["git_head"] = common["run"](["git", "rev-parse", "HEAD"],
                                            folder / "revision.log", env).strip()
        result.update(execute(common, folder, expected, env), status="PASS")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result.update(status="FAIL", reason=str(exc))
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 READN " + result["status"])
    print("Evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
