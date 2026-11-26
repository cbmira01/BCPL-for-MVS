#!/usr/bin/env python3
"""DR.5 targeted compiler/Base Library rebuild and native newline verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
COMMON = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
FIX = COMMON["FIX"]
SOURCE = FIX / "native-newline-fixed.bcpl"
EXPECTED = FIX / "native-newline-fixed.expected"
require = COMMON["require"]
run = COMMON["run"]
receipt = COMMON["receipt"]
CODE = COMMON["CODE"]
STEP = COMMON["STEP"]
CAMB_STEPS = [(f"C{i:02d}{stage}", "ICINT19")
              for i in range(1, 12) for stage in ("CMP", "CG")]
CAMB_STEPS.append(("PACKCOMP", "IEBGENER"))
BLIB_STEPS = [("COMP", "ICINT19"), ("PREPASM", "IFOX00"),
              ("PREPLK", "IEWL"), ("FIXASM", None),
              ("ASMBLIB", "IFOX00"), ("INSTALL", "IEBGENER")]


def build_gate(summary, report, name, steps, count):
    require("JOB RESULT: SUCCESS" in summary and "HIGHEST RC: 0000" in summary,
            name + " JES failure")
    actual = STEP.findall(summary)
    require(len(actual) == len(steps), name + " step count")
    for (step, pgm, rc), (wanted, program) in zip(actual, steps):
        require(step == wanted and rc == "0000" and
                (program is None or pgm == program), name + " step mismatch")
    require([int(x) for x in CODE.findall(report)] == [0] * count,
            name + " ICINT completion mismatch")


def build(folder, env, name, steps, count):
    log = folder / (name + "-submit.log")
    output = run(["tools/datasets/dspal", "submit", "BOOT_JCL", name], log, env)
    ids = re.findall(r"^Payload:\s+JOB\s+(\d+)\s*$", output, re.M)
    require(len(ids) == 1, name + " payload job identity")
    job = ids[0]
    summary = run(["tools/mvs/job-summary", job, "--max-rc", "0"],
                  folder / (name + "-summary.log"), env)
    require(re.search(rf"^JOB\s+{job}\s+{name}\s*$", summary, re.M),
            name + " summary identity")
    report = run(["tools/mvs/dump-report-for-job", job],
                 folder / (name + "-report.log"), env)
    build_gate(summary, report, name, steps, count)
    print(f"{name} JOB {job} PASS", flush=True)
    return job


def verifier(expected):
    require(expected and len(expected) < 256, "invalid record count")
    require(all(len(x) <= 55 and "'" not in x for x in expected),
            "unsupported verifier literal")
    rows = ["DR5VFY   CSECT", "         STM   14,12,12(13)",
            "         LR    12,15", "         USING DR5VFY,12",
            "         ST    13,OLDSAVE+4", "         LA    13,NEWSAVE",
            "         MVI   NREC,X'00'", "         OPEN  (OUTDCB,(INPUT))"]
    for i, line in enumerate(expected, 1):
        rows += ["         GET   OUTDCB,BUF", f"         CLC   BUF(132),EXP{i:02d}",
                 "         BNE   BAD", f"         MVI   NREC,X'{i:02X}'"]
    rows += ["         GET   OUTDCB,BUF", "         B     BAD",
             f"EOD      CLI   NREC,X'{len(expected):02X}'", "         BNE   BAD",
             "         CLOSE (OUTDCB)", "         L     13,OLDSAVE+4",
             "         LM    14,12,12(13)", "         SR    15,15", "         BR    14",
             "BAD      CLOSE (OUTDCB)", "         L     13,OLDSAVE+4",
             "         LM    14,12,12(13)", "         LA    15,12", "         BR    14",
             "         LTORG", "         DS    0F", "OLDSAVE  DS    18F",
             "NEWSAVE  DS    18F", "NREC     DC    X'00'", "         DS    0F",
             "BUF      DS    CL132", "OUTDCB   DCB   DDNAME=RECORDS,DSORG=PS,MACRF=GM,EODAD=EOD"]
    rows += [f"EXP{i:02d}    DC    CL132'{line}'" for i, line in enumerate(expected, 1)]
    rows += ["         END   DR5VFY"]
    require(all(len(x) <= 71 for x in rows), "verifier assembler card length")
    return rows


def transform(deck, expected):
    require(deck.endswith("\n//\n") and " INCLUDE OBJ(BLIB)" in deck,
            "unexpected native deck")
    before, go = deck.split("//GO       EXEC", 1)
    old = "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)"
    require(go.count(old) == 1, "missing GO SYSPRINT")
    go = go.replace(old, "\n".join([
        "//SYSPRINT DD DSN=&&DR5REC,UNIT=SYSDA,",
        "//             SPACE=(TRK,(1,1)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//BCPIN    DD DATA,DLM=Z9", "A", "B", "Z9"]))
    tail = ["//VASM     EXEC PGM=IFOX00,REGION=256K,COND=(0,NE,GO),",
            "//             PARM='OBJECT,NODECK,LIST'", "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSPRINT DD SYSOUT=*", "//SYSPUNCH DD DUMMY",
            "//SYSGO    DD DSN=&&VOBJ,UNIT=SYSDA,SPACE=(80,(100,20)),",
            "//             DISP=(NEW,PASS),DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSIN    DD *", *verifier(expected), "/*",
            "//VLINK    EXEC PGM=IEWL,PARM='LIST,XREF,MAP',COND=(0,NE,VASM)",
            "//SYSLIN   DD DSN=&&VOBJ,DISP=(OLD,DELETE)", "//         DD *",
            " ENTRY DR5VFY", " NAME DR5VFY(R)", "/*",
            "//SYSLMOD  DD DSN=&&VLD(DR5VFY),UNIT=SYSDA,",
            "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))", "//SYSPRINT DD SYSOUT=*",
            "//VCHK     EXEC PGM=*.VLINK.SYSLMOD,",
            "//             COND=((0,NE,GO),(0,NE,VASM),(0,NE,VLINK))",
            "//RECORDS  DD DSN=&&DR5REC,DISP=(OLD,PASS)", "//SYSUDUMP DD SYSOUT=*",
            "//SHOW     EXEC PGM=IEBGENER,COND=(0,NE,VCHK)", "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY", "//SYSUT1   DD DSN=&&DR5REC,DISP=(OLD,DELETE)",
            "//SYSUT2   DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)", "//"]
    result = before + "//GO       EXEC" + go[:-3] + "\n".join(tail) + "\n"
    require(all(len(x) <= 80 for x in result.splitlines()), "JCL card length")
    require(result.count("DSN=&&DR5REC") == 3, "record dataset linkage")
    return result


def check():
    expected = COMMON["check_candidate"](SOURCE, EXPECTED,
                         ("NEWLINE", "EBCDIC", "INPUT", "WRITES", "DIRECT", "END"))
    COMMON["check"]()
    sample = " INCLUDE OBJ(BLIB)\n//GO       EXEC PGM=*.LKED.SYSLMOD\n"
    sample += "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)\n//\n"
    result = transform(sample, expected)
    require(result.count("CLC   BUF(132),EXP") == len(expected), "verifier coverage")
    require("//BCPIN    DD DATA,DLM=Z9\nA\nB\nZ9" in result, "input fixture")
    summary = "JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n" + "\n".join(
        f"{a} {b} RC=0000" for a, b in CAMB_STEPS)
    report = "EXECUTION CYCLES = 1, CODE = 0\n" * 22
    build_gate(summary, report, "CAMBBLD", CAMB_STEPS, 22)
    for wrong in (report[:-35], report.replace("CODE = 0", "CODE = 8", 1)):
        try:
            build_gate(summary, wrong, "CAMBBLD", CAMB_STEPS, 22)
        except ValueError:
            pass
        else:
            raise ValueError("nonzero or missing ICINT completion accepted")
    return expected


def probe(folder, expected, env):
    generated = folder / "fixed.asm"
    output = run(["tools/bootstrap/compile-mvs", SOURCE, "--job-name", "DR5CFIX",
                  "--compiler-image", "CAMBCOMP", "--cambridge-parm",
                  ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                  "--output", generated], folder / "fixed-compile.log", env)
    comp = COMMON["job_id"](output)
    report = receipt(folder, comp, "DR5CFIX", COMMON["CC_STEPS"], env)
    require([int(x) for x in CODE.findall(report)] == [0], "compiler CODE")
    base = folder / "fixed-base.jcl"
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py", generated,
         base, "--test-number", "903"], folder / "fixed-build.log", env)
    deck = folder / "fixed-records.jcl"
    deck.write_text(transform(base.read_text("ascii"), expected), encoding="ascii")
    cursor = folder / "fixed.cursor"
    output = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                 folder / "fixed-submit.log", env)
    job = COMMON["job_id"](output)
    # Receipt helper exempts only the passed application GO program. VCHK's
    # displayed program is also site-dependent; validate its step/RC below.
    # Poll using the common receipt with a separate, exact VCHK identity gate.
    import time
    deadline = time.monotonic() + 240
    while True:
        rc, summary = COMMON["command"](["tools/mvs/job-summary", job, "--max-rc", "0",
                          "--cursor-file", cursor], folder / "RG903R-summary.log", env)
        if rc != 2:
            break
        require(time.monotonic() < deadline, "fixed GO timeout")
        time.sleep(2)
    report = run(["tools/mvs/dump-report-for-job", job, "--cursor-file", cursor],
                 folder / "RG903R-report.log", env)
    require(re.search(rf"^JOB\s+{job}\s+RG903R\s*$", summary, re.M), "fixed job identity")
    steps = [("ASMAP", "IFOX00"), ("LKED", "IEWL"), ("GO", None),
             ("VASM", "IFOX00"), ("VLINK", "IEWL"), ("VCHK", None), ("SHOW", "IEBGENER")]
    require(rc == 0, "fixed JES job failed: " + repr(STEP.findall(summary)))
    build_gate(summary, report, "RG903R", steps, 0)
    # VCHK is the authoritative exact FB132 record/EOF oracle; SHOW provides
    # a human-readable rendition. The linker list also contains expected data.
    return {"compiler_job": comp, "job": job, "fb132_readback": "PASS"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--rebuild-and-verify", action="store_true")
    args = parser.parse_args()
    expected = check()
    if args.check:
        print("DR.5 newline fix offline CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    base = ROOT / "workarea/dr5-newline-fix"
    base.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {"status": "FAIL", "jobs": {}, "stage": "preflight"}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip()
        run(["tools/bootstrap/prepare-bootstrap"], folder / "prepare.log", env)
        master = ROOT / "workarea/bootstrap-cambridge/demoted/bcpl"
        require(master.read_text("utf-8").count("IF CH=10 RESULTIS 10") == 1,
                "generated master does not contain the approved mapping")
        result["master_sha256"] = hashlib.sha256(master.read_bytes()).hexdigest()
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle.log", env)
        # Persistent changes start here. Never replay a failed partial build.
        result["stage"] = "stage-master"
        (folder / "writes-started").write_text("BOOT_SOURCE(BCPL), CAMBBLD, BLIBBLD\n")
        run(["tools/datasets/dspal", "put", "BOOT_SOURCE", "BCPL", master],
            folder / "put-master.log", env)
        result["stage"] = "CAMBBLD"
        result["jobs"]["CAMBBLD"] = build(folder, env, "CAMBBLD", CAMB_STEPS, 22)
        result["stage"] = "BLIBBLD"
        result["jobs"]["BLIBBLD"] = build(folder, env, "BLIBBLD", BLIB_STEPS, 1)
        result["stage"] = "original-native"
        result["jobs"]["original-native"] = COMMON["native"](folder, COMMON["check"](), env)
        print("DR.5 original native PASS", flush=True)
        result["stage"] = "newline-records"
        result["jobs"]["newline-records"] = probe(folder, expected, env)
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
