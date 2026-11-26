#!/usr/bin/env python3
"""Permanent Bootstrap compatibility regressions 190–192, no resident writes."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
CODE = re.compile(r"EXECUTION CYCLES\s*=\s*\d+,\s*CODE\s*=\s*(-?\d+)")
JOB = re.compile(r"^JOB\s+(\d+)\s*$", re.M)
STEP = re.compile(r"^[ \t]*([A-Z0-9]+)[ \t]+(\S*?)[ \t]+RC=(\d{4})[ \t]*$", re.M)
CC_STEPS = [("COMP", "ICINT19"), ("SVCODE", "IEBGENER")]
GO_STEPS = [("ASMAP", "IFOX00"), ("LKED", "IEWL"), ("GO", None)]
RECORD_STEPS = GO_STEPS + [("VASM", "IFOX00"), ("VLINK", "IEWL"),
                          ("VCHK", None), ("SHOW", "IEBGENER")]
DEFAULT_PARM = ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt"
CASES = {190: "190-native-logical-newline", 191: "191-cambridge-option-replay",
         192: "192-cambridge-source-lookahead"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def output_records(report):
    return [line.strip() for line in report.replace("\f", "").splitlines()
            if line.strip().startswith("RP: RG")]


def compare(report, expected):
    require("AUTHORIZATION CODE IS" in report, "missing GO boundary")
    actual = output_records(report.rsplit("AUTHORIZATION CODE IS", 1)[1])
    require(actual == expected, "observed records differ: " + repr(actual))
    return actual


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
            repr(output_records(report.rsplit("AUTHORIZATION CODE IS", 1)[-1])))
    # GO's displayed program field varies with the passed load module;
    # check exact ordered step identities and zero RC, plus fixed programs.
    actual = STEP.findall(summary)
    require(len(actual) == len(steps), "unexpected JES step count")
    for (step, pgm, code), (wanted, wanted_pgm) in zip(actual, steps):
        require(step == wanted and code == "0000" and
                (wanted_pgm is None or wanted == "GO" or pgm == wanted_pgm),
                "JES step mismatch: " + repr(actual))
    return report



def verifier(expected):
    require(expected and len(expected) < 256, "invalid record count")
    require(all(len(x) <= 55 and "'" not in x for x in expected),
            "unsupported verifier literal")
    rows = ["RG190V   CSECT", "         STM   14,12,12(13)",
            "         LR    12,15", "         USING RG190V,12",
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
    rows += ["         END   RG190V"]
    require(all(len(x) <= 71 for x in rows), "verifier assembler card length")
    return rows


def transform(deck, expected, inputs):
    require(deck.endswith("\n//\n") and " INCLUDE OBJ(BLIB)" in deck,
            "unexpected native deck")
    before, go = deck.split("//GO       EXEC", 1)
    old = "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)"
    require(go.count(old) == 1, "missing GO SYSPRINT")
    go = go.replace(old, "\n".join([
        "//SYSPRINT DD DSN=&&RGREC,UNIT=SYSDA,",
        "//             SPACE=(TRK,(1,1)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//BCPIN    DD DATA,DLM=Z9", *inputs, "Z9"]))
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
            " ENTRY RG190V", " NAME RG190V(R)", "/*",
            "//SYSLMOD  DD DSN=&&VLD(RG190V),UNIT=SYSDA,",
            "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))", "//SYSPRINT DD SYSOUT=*",
            "//VCHK     EXEC PGM=*.VLINK.SYSLMOD,",
            "//             COND=((0,NE,GO),(0,NE,VASM),(0,NE,VLINK))",
            "//RECORDS  DD DSN=&&RGREC,DISP=(OLD,PASS)", "//SYSUDUMP DD SYSOUT=*",
            "//SHOW     EXEC PGM=IEBGENER,COND=(0,NE,VCHK)", "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY", "//SYSUT1   DD DSN=&&RGREC,DISP=(OLD,DELETE)",
            "//SYSUT2   DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)", "//"]
    result = before + "//GO       EXEC" + go[:-3] + "\n".join(tail) + "\n"
    require(all(len(x) <= 80 for x in result.splitlines()), "JCL card length")
    require(result.count("DSN=&&RGREC") == 3, "record dataset linkage")
    return result



def cards(path):
    lines = path.read_text("ascii").splitlines()
    require(lines and all(len(x) <= 80 and "\t" not in x and
                          not x.startswith(("Z9", "//", "/*")) for x in lines),
            "invalid cards: " + str(path))
    return lines


def check(number, fixture):
    require(fixture.resolve() == ROOT / "tests/bootstrap" / CASES[number],
            "fixture identity mismatch")
    source = cards(fixture / "source.bcpl")
    expected = cards(fixture / "expected.txt")
    require(all(x.startswith(f"RP: RG{number}") for x in expected), "bad oracle prefix")
    if number == 190:
        inputs = cards(fixture / "input.records")
        require(len(expected) == 6 and inputs == ["A", "B"], "newline fixture geometry")
        sample = " INCLUDE OBJ(BLIB)\n//GO       EXEC PGM=*.LKED.SYSLMOD\n"
        sample += "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)\n//\n"
        deck = transform(sample, expected, inputs)
        require(deck.count("CLC   BUF(132),EXP") == 6, "record verifier coverage")
    elif number == 191:
        for name, prefix in (("original-options.txt", "J12Q/N/"),
                             ("numeric-options.txt", "J12P3000R30Q/N/"),
                             ("naming-options.txt", "Q/H600N/")):
            require(cards(fixture / name) == [prefix.ljust(80, "/")],
                    "unexpected CAMBPARM record")
        require(len(expected) == 1, "option oracle count")
    else:
        require(sum(x.startswith(".") for x in source) == 1 and len(expected) == 2,
                "source lookahead fixture geometry")
    compare("AUTHORIZATION CODE IS\n" + "\n".join(expected), expected)
    wrong_cases = [expected[:-1], expected + expected[-1:],
                   [expected[0] + " EXTRA", *expected[1:]]]
    if expected[::-1] != expected:
        wrong_cases.append(expected[::-1])
    for wrong in wrong_cases:
        try:
            compare("AUTHORIZATION CODE IS\n" + "\n".join(wrong), expected)
        except ValueError:
            pass
        else:
            raise ValueError("incorrect oracle accepted")
    return expected


def compile_source(folder, fixture, name, parm, env, warning=False, quiet=False):
    generated = folder / (name + ".asm")
    rc, text = command(["tools/bootstrap/compile-mvs", fixture / "source.bcpl",
                        "--job-name", name, "--compiler-image", "CAMBCOMP",
                        "--cambridge-parm", parm, "--output", generated],
                       folder / (name + "-compile.log"), env)
    ids = JOB.findall(text)
    require(len(ids) == 1, f"{name}: compiler driver RC={rc}; no unique JES job number")
    job = ids[0]
    # Retain the complete MVS report even when the host rejects ICINT CODE.
    report = receipt(folder, job, name, CC_STEPS, env)
    codes = [int(x) for x in CODE.findall(report)]
    require(codes == [0], f"{name} JOB {job}: ICINT CODE={codes!r}")
    require(rc == 0, f"{name} JOB {job}: compiler driver RC={rc}")
    if warning:
        require("UNKNOWN COMPILATION OPTION J IGNORED" in report.upper(), "missing J warning")
        require(len(re.findall(r"Unknown compilation option", report, re.I)) == 1,
                "unexpected extra unknown-option warning")
        require("OPTION IS ONLY SUITABLE FOR CROSS COMPILATION" not in report.upper(),
                "unexpected cross-compilation option warning")
    if quiet:
        require(not any(x in report.upper() for x in
                        ("TREE SIZE", "OCODE SIZE =", "COMPILATION SUCCESSFUL")),
                "Q did not suppress ordinary phase diagnostics")
    require(generated.is_file() and generated.stat().st_size, "missing CODE")
    print(f"{name} JOB {job} compile PASS", flush=True)
    return generated


def split_units(generated, count):
    units = []
    part = []
    for row in generated.read_text("latin-1").splitlines(keepends=True):
        part.append(row)
        if re.fullmatch(r"\s*END(?:\s+.*?)?\s*", row):
            text = "".join(part)
            require(len(re.findall(r"(?m)^\s*CSECT\s*$", text)) == 1, "not one anonymous CSECT")
            require(len(re.findall(r"(?m)^\s*EXTRN\s+BCPLMAIN\s*$", text)) == 1,
                    "missing BCPLMAIN external")
            units.append(text)
            part = []
    require(len(units) == count and not "".join(part).strip(), "unexpected CODE unit count")
    return units


def execute_unit(folder, number, generated, jobname, expected, env, inputs=None):
    base = folder / (jobname + "-base.jcl")
    run(["python3", "tools/checks/prepare-runtime-pds-regression.py", generated,
         base, "--test-number", str(number)], folder / (jobname + "-prepare.log"), env)
    deck = base.read_text("ascii")
    old = f"//RG{number:03d}R "
    require(deck.count(old) == 1, "unexpected job card")
    deck = deck.replace(old, "//" + jobname + " ", 1)
    if inputs is not None:
        deck = transform(deck, expected, inputs)
    path = folder / (jobname + ".jcl")
    path.write_text(deck, encoding="ascii")
    cursor = folder / (jobname + ".cursor")
    text = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, path],
               folder / (jobname + "-submit.log"), env)
    job = job_id(text)
    report = receipt(folder, job, jobname,
                     RECORD_STEPS if inputs is not None else GO_STEPS, env, cursor)
    require(not CODE.findall(report), "unexpected interpreted completion in native job")
    # Only display the observed output, or the exact bytes independently
    # verified by VCHK; never claim a JES rendition is the FB132 oracle.
    observed = compare(report, expected) if inputs is None else expected
    print(f"{jobname} JOB {job} " + ("FB132 readback PASS" if inputs is not None else "GO PASS"),
          flush=True)
    print("=== BCPL output ===")
    for row in observed:
        print(row)
    print("=== End BCPL output ===")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", type=int, choices=CASES)
    parser.add_argument("fixture", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    expected = check(args.number, args.fixture)
    if args.check:
        print(f"Bootstrap {args.number} host CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    parent = ROOT / "workarea/bootstrap-compatibility"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix=f"case-{args.number}-", dir=parent))
    print("Evidence: " + str(folder), flush=True)
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {"case": args.number, "status": "FAIL"}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip()
        n = args.number
        f = args.fixture
        if n == 190:
            generated = compile_source(folder, f, "RG190C", DEFAULT_PARM, env)
            split_units(generated, 1)
            execute_unit(folder, n, generated, "RG190R", expected, env,
                         cards(f / "input.records"))
        elif n == 191:
            for suffix, option, go in (("C", "original-options.txt", "R"),
                                       ("D", "numeric-options.txt", "S"),
                                       ("H", "naming-options.txt", None)):
                generated = compile_source(folder, f, "RG191" + suffix, f / option,
                                           env, warning=suffix != "H", quiet=True)
                split_units(generated, 1)
                if go:
                    execute_unit(folder, n, generated, "RG191" + go, expected, env)
        else:
            generated = compile_source(folder, f, "RG192C", DEFAULT_PARM, env)
            for i, unit in enumerate(split_units(generated, 2)):
                output = folder / f"unit-{i+1}.asm"
                output.write_text(unit, encoding="latin-1")
                execute_unit(folder, n, output, "RG192" + ("R", "S")[i],
                             expected[i:i+1], env)
        result["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result["reason"] = str(exc)
        print("FAIL: " + str(exc))
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
