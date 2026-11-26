#!/usr/bin/env python3
"""DR.5 rebuild only the Cambridge compiler host and run permanent compatibility tests."""
import argparse
import json
import os
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUILD = runpy.run_path(str(ROOT / "tools/checks/run-dr5-newline-fix.py"))
COMMON = BUILD["COMMON"]
run = COMMON["run"]
require = COMMON["require"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--rebuild-and-verify", action="store_true")
    args = p.parse_args()
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    runner = runpy.run_path(str(ROOT / "tools/checks/run-bootstrap-compatibility.py"))
    for n, name in runner["CASES"].items():
        runner["check"](n, ROOT / "tests/bootstrap" / name)
    if args.check:
        print("DR.5 bootstrap host compatibility CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-bootstrap-host-fix"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    result = {"status": "FAIL", "stage": "preflight", "cases": {}}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip()
        run(["tools/tests/run-suite", "--check"], folder / "manifest.log", env)
        run(["tools/bootstrap/prepare-bootstrap"], folder / "prepare.log", env)
        host = ROOT / "bootstrap-toolchain/bootstrap-cambridge/bootstrap-host.bcpl"
        import hashlib
        result["host_sha256"] = hashlib.sha256(host.read_bytes()).hexdigest()
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle.log", env)
        result["stage"] = "stage-host"
        (folder / "writes-started").write_text("BOOT_SOURCE(BOOTHOST), CAMBBLD\n")
        run(["tools/datasets/dspal", "put", "BOOT_SOURCE", "BOOTHOST", host],
            folder / "put-host.log", env)
        result["stage"] = "CAMBBLD"
        result["CAMBBLD"] = BUILD["build"](folder, env, "CAMBBLD", BUILD["CAMB_STEPS"], 22)
        for n in runner["CASES"]:
            result["stage"] = f"bootstrap-{n}"
            rc, output = COMMON["command"](["tools/tests/run-suite", "bootstrap", "--run",
                   "--profile", "production", "--case", str(n)],
                   folder / f"case-{n}.log", env)
            print(output, end="", flush=True)
            result["cases"][str(n)] = "PASS" if rc == 0 else "FAIL"
            require(rc == 0, f"Bootstrap {n} failed")
        result["stage"] = "complete"
        result["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, COMMON["subprocess"].TimeoutExpired) as exc:
        result["reason"] = str(exc)
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        print("STOP: do not replay a partial rebuild; retain evidence.")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
