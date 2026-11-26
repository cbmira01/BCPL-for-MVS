#!/usr/bin/env python3
"""DR.5: verify canonical BCPLIO privately before any production writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
COMMON = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
require, run, receipt = COMMON["require"], COMMON["run"], COMMON["receipt"]
ASM = ROOT / "bootstrap-toolchain/asm/bcplio.asm"
CASE = ROOT / "tests/bootstrap/193-bcplio-stream-guards"
CORE = runpy.run_path(str(ROOT / "tools/datasets/dspal-core.py"))
BUILD_STEPS = [("ASMIO", "IFOX00"), ("PUTIO", "IEBGENER"),
               ("RDIO", "IEBGENER"), ("VFIO", "IEBCOMPR")]
PRIVATE_STEPS = [("ASMAP", "IFOX00"), ("ASMFIO", "IFOX00"),
                 ("LKED", "IEWL"), ("GO", None)]


def install_cards(config, redact=True):
    asm = config["datasets"]["BOOT_ASM"]
    obj = config["datasets"]["BOOT_OBJ"]
    for spec in (asm, obj):
        require(spec["dsorg"] == "PO" and spec["recfm"] == "FB"
                and int(spec["lrecl"]) == 80, "expected FB80 PDS")
    require(obj["content_type"] == "object", "expected object PDS")
    src = CORE["full_dsn"](config, asm)
    dst = CORE["full_dsn"](config, obj)
    require(src != dst, "source/object PDS collision")
    cards = [
        *CORE["authenticated_job_card"](config, "BLDIOFIX", "BCPLIO FIX", redact),
        "//* REPLACE ONLY BCPLIO; VERIFY OBJECT BY IEBCOMPR.",
        "//ASMIO    EXEC PGM=IFOX00,REGION=512K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        "//SYSGO    DD DSN=&&IOOBJ,UNIT=SYSDA,",
        "//             SPACE=(80,(500,200)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        f"//SYSIN    DD DSN={src}(BCPLIO),DISP=SHR",
        "//PUTIO    EXEC PGM=IEBGENER,COND=(0,NE)",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSIN    DD DUMMY",
        "//SYSUT1   DD DSN=&&IOOBJ,DISP=(OLD,PASS)",
        f"//SYSUT2   DD DSN={dst}(BCPLIO),DISP=OLD",
        "//RDIO     EXEC PGM=IEBGENER,COND=(0,NE)",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSIN    DD DUMMY",
        f"//SYSUT1   DD DSN={dst}(BCPLIO),DISP=SHR",
        "//SYSUT2   DD DSN=&&IOREAD,UNIT=SYSDA,",
        "//             SPACE=(80,(500,200)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//VFIO     EXEC PGM=IEBCOMPR,COND=(0,NE)",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSUT1   DD DSN=&&IOOBJ,DISP=(OLD,DELETE)",
        "//SYSUT2   DD DSN=&&IOREAD,DISP=(OLD,DELETE)",
        "//SYSIN    DD *",
        " COMPARE TYPORG=PS",
        "/*",
        "//",
    ]
    require(all(len(x) <= 71 and x.isascii() for x in cards), "invalid JCL card")
    require(sum("(BCPLIO),DISP=OLD" in x for x in cards) == 1,
            "unexpected persistent write scope")
    return "\n".join(cards) + "\n"


def check():
    for cmd in (["python3", "tools/checks/check-asm-source.py", str(ASM)],
                ["tools/tests/run-suite", "--check"]):
        p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        require(p.returncode == 0, p.stdout + p.stderr)
    for name in ("source.bcpl", "input.records", "input-b.records",
                 "input-dd01.records", "expected.txt", "expected-alt.txt",
                 "expected-report.txt"):
        rows = (CASE / name).read_text("ascii").splitlines()
        require(rows and all(len(x) <= 80 and not x.startswith(("//", "/*"))
                             for x in rows), "invalid fixture " + name)
    config = {"mvs": {"hlq": "DR5", "batch_user": "TEST"},
              "datasets": {"BOOT_ASM": {"dsn": "BCPL.BOOT.ASM",
                                          "dsorg": "PO", "recfm": "FB", "lrecl": 80},
                           "BOOT_OBJ": {"dsn": "BCPL.BOOT.OBJ", "content_type": "object",
                                          "dsorg": "PO", "recfm": "FB", "lrecl": 80}}}
    deck = install_cards(config)
    require("DR5.BCPL.BOOT.ASM(BCPLIO)" in deck
            and "DR5.BCPL.BOOT.OBJ(BCPLIO)" in deck
            and "PASSWORD=REDACTED" in deck, "install deck self-check")


def submit(folder, name, deck, steps, env):
    cursor = folder / (name + ".cursor")
    output = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                 folder / (name + "-submit.log"), env)
    job = COMMON["job_id"](output)
    report = receipt(folder, job, name, steps, env, cursor)
    return job, report


def candidate(folder, env, result):
    generated = folder / "guards.asm"
    output = run(["tools/bootstrap/compile-mvs", CASE / "source.bcpl",
                  "--job-name", "DR5IOC", "--compiler-image", "CAMBCOMP",
                  "--cambridge-parm",
                  ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                  "--output", generated], folder / "compile.log", env)
    job = COMMON["job_id"](output)
    report = receipt(folder, job, "DR5IOC", COMMON["CC_STEPS"], env)
    require(COMMON["CODE"].findall(report) == ["0"], "compiler completion")
    require(generated.is_file() and generated.stat().st_size, "missing CODE")
    result["candidate_compile"] = job
    deck = folder / "private.jcl"
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py",
         generated, deck, "--test-number", "193", "--case-dir", CASE,
         "--test-io-asm", ASM], folder / "private-prepare.log", env)
    cards = deck.read_text("ascii")
    require(" INCLUDE OBJ(BCPLIO)" not in cards and
            cards.count("//ASMFIO") == 1 and
            cards.count(ASM.read_text("ascii").rstrip("\n")) == 1,
            "private canonical source/linkage not established")
    job, report = submit(folder, "RG193R", deck, PRIVATE_STEPS, env)
    require(not COMMON["CODE"].findall(report), "unexpected interpreted GO")
    path = folder / "RG193R-report.log"
    for dd, name in (("SYSPRINT", "expected.txt"),
                     ("BCPALT", "expected-alt.txt"), ("REPORT", "expected-report.txt")):
        run(["python3", "tools/checks/check-combined-jes-records.py", CASE / name,
             path, "--destination", dd], folder / (dd + "-check.log"), env)
    result["candidate_go"] = job
    print(f"BCPLIO private IFOX/IEWL/GO JOB {job} PASS", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--candidate-only", action="store_true")
    modes.add_argument("--rebuild-and-verify", action="store_true")
    args = p.parse_args()
    check()
    if args.check:
        print("DR.5 BCPLIO guard CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-bcplio-fix"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "R1_REGRESSION_LOG_DIR",
                "R1_ACCEPTANCE_WORKDIR", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {"status": "FAIL", "stage": "preflight"}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip()
        require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                        folder / "tracked-status.log", env).strip(), "tracked changes present")
        result["asm_sha256"] = hashlib.sha256(ASM.read_bytes()).hexdigest()
        config = CORE["load_config"]()
        cards = install_cards(config, redact=False)
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-before.log", env)
        result["stage"] = "private-candidate"
        candidate(folder, env, result)
        if args.rebuild_and_verify:
            require(hashlib.sha256(ASM.read_bytes()).hexdigest() == result["asm_sha256"],
                    "source changed after private test")
            require(run(["git", "rev-parse", "HEAD"],
                        folder / "revision-before-write.log", env).strip() == result["git_head"],
                    "revision changed after private test")
            run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-write.log", env)
            result["stage"] = "stage-source"
            (folder / "writes-started").write_text("BOOT_ASM(BCPLIO), BOOT_OBJ(BCPLIO)\n")
            run(["tools/datasets/dspal", "put", "BOOT_ASM", "BCPLIO", ASM],
                folder / "put.log", env)
            readback = folder / "staged.asm"
            run(["tools/datasets/dspal", "get", "BOOT_ASM", "BCPLIO", readback],
                folder / "get.log", env)
            def logical_cards(path):
                return [x.rstrip(" ") for x in path.read_text("ascii").splitlines()]
            require(logical_cards(readback) == logical_cards(ASM), "staged source mismatch")
            result["stage"] = "install-BCPLIO"
            deck = folder / "install.jcl"
            deck.write_text(cards, encoding="ascii")
            job, _ = submit(folder, "BLDIOFIX", deck, BUILD_STEPS, env)
            result["install_job"] = job
            print(f"BLDIOFIX JOB {job} PASS (IFOX, install, readback, IEBCOMPR)", flush=True)
            result["stage"] = "installed-193"
            rc, output = COMMON["command"](
                ["tools/tests/run-suite", "bootstrap", "--run", "--profile",
                 "production", "--case", "193"], folder / "installed.log", env)
            print(output, end="", flush=True)
            require(rc == 0, "installed case 193 failed")
            result["installed_193"] = "PASS"
        result["stage"] = "complete" if args.rebuild_and_verify else "candidate-only"
        result["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result["reason"] = str(exc)
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        print("STOP: retain evidence; do not replay a partially completed write.")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
