#!/usr/bin/env python3
"""DR.5: reproduce DEBUGINT defect, test private BCPLMAIN, then install only it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "packaging/milestones/documentation-refactoring/candidates/debugint-verification"
ASM = ROOT / "bootstrap-toolchain/asm/bcplmain.asm"
BASE = "0fde1b7c8c7ab1e2d1f6a07e77869030f6c06a24"
OLD = "         LA    10,C'-'\n         BAL   14,DBGAPND\nDBGCVT   CVD   7,DECPACK"
NEW = "         LR    8,7\n         LA    10,C'-'\n         BAL   14,DBGAPND\n         LR    7,8\nDBGCVT   CVD   7,DECPACK"
LABELS = ("DEBUGINT",) * 6
BUILD_STEPS = [("ASMMN", "IFOX00"), ("PUTMN", "IEBGENER"),
               ("RDMN", "IEBGENER"), ("VFMN", "IEBCOMPR")]
PRIVATE_STEPS = [("ASMAP", "IFOX00"), ("ASMNAT", "IFOX00"),
                 ("LKED", "IEWL"), ("GO", None)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replace_once(text, old, new):
    require(text.count(old) == 1, "missing or ambiguous anchor: " + old)
    return text.replace(old, new)


def private_cards(deck, source):
    require(deck.count(source.rstrip("\n")) == 1, "inline BCPLMAIN not unique")
    require(deck.count("//ASMNAT   EXEC") == 1 and
            deck.count("//         DD DSN=&&NATOBJ,DISP=(OLD,DELETE)") == 1,
            "private assembler/link concatenation missing")
    deck = replace_once(deck, " INCLUDE OBJ(BCPLMAIN)\n", "")
    deck = replace_once(deck, "//ASMNAT   EXEC PGM=IFOX00,REGION=256K,",
                        "//ASMNAT   EXEC PGM=IFOX00,REGION=512K,")
    require(" INCLUDE OBJ(BCPLMAIN)" not in deck and
            all(len(x) <= 71 and x.isascii() for x in deck.splitlines()),
            "private deck scope or card width")
    return deck


def baseline_result(actual, expected):
    require(len(actual) == len(expected) == 6, "baseline record count")
    require(actual[:3] == expected[:3], "baseline positive/zero controls failed")
    for got, wanted in zip(actual[3:], expected[3:]):
        prefix = wanted.rsplit(" ", 1)[0] + " "
        require(got.startswith(prefix) and
                re.fullmatch(r"-?[0-9]+", got[len(prefix):]),
                "unexpected baseline diagnostic shape")
    require(actual[3:] != expected[3:], "signed defect not reproduced; stop")
    return "FAIL (negative operand defect reproduced)"


def install_cards(helper, config, redact=True):
    original = helper["install_cards"](config, redact=True)
    anchor = "//* REPLACE ONLY BCPLIO; VERIFY OBJECT BY IEBCOMPR."
    require(original.count(anchor) == 1, "install template changed")
    body = original[original.index(anchor):]
    for old, new in (("BCPLIO", "BCPLMAIN"), ("ASMIO", "ASMMN"),
                     ("PUTIO", "PUTMN"), ("RDIO", "RDMN"), ("VFIO", "VFMN"),
                     ("&&IOOBJ", "&&MNOBJ"), ("&&IOREAD", "&&MNREAD")):
        body = body.replace(old, new)
    core = helper["CORE"]
    src = core["full_dsn"](config, config["datasets"]["BOOT_ASM"])
    dst = core["full_dsn"](config, config["datasets"]["BOOT_OBJ"])
    require(body.count(f"DSN={src}(BCPLMAIN),DISP=SHR") == 1 and
            body.count(f"DSN={dst}(BCPLMAIN),DISP=OLD") == 1 and
            body.count(f"DSN={dst}(BCPLMAIN),DISP=SHR") == 1,
            "unexpected install member scope")
    cards = core["authenticated_job_card"](config, "BLDMNFIX", "DEBUGINT FIX", redact)
    deck = "\n".join(cards) + "\n" + body
    require(all(len(x) <= 71 and x.isascii() for x in deck.splitlines()),
            "invalid install card")
    return deck


def check(common):
    expected = common["check_candidate"](FIX / "source.bcpl", FIX / "expected.txt", LABELS)
    old = subprocess.check_output(["git", "show", BASE + ":" + str(ASM.relative_to(ROOT))],
                                  cwd=ROOT).decode("ascii")
    require(ASM.read_text("ascii") == replace_once(old, OLD, NEW),
            "BCPLMAIN differs from approved two-card correction")
    subprocess.run(["python3", "tools/checks/check-asm-source.py", str(ASM)],
                   cwd=ROOT, check=True)
    bad = expected[:3] + [x.rsplit(" ", 1)[0] + " -123" for x in expected[3:]]
    baseline_result(bad, expected)
    for invalid in (expected, bad[:-1], ["BAD", *bad[1:]]):
        try:
            baseline_result(invalid, expected)
        except ValueError:
            pass
        else:
            raise ValueError("baseline gate accepted invalid evidence")
    return expected


def native(common, folder, generated, env, private=False):
    folder.mkdir()
    deck = folder / "native.jcl"
    args = ["python3", "tools/checks/prepare-runtime-pds-regression.py",
            generated, deck, "--test-number", "906", "--case-dir", FIX]
    if private:
        args += ["--native", ASM]
    common["run"](args, folder / "prepare.log", env)
    if private:
        deck.write_text(private_cards(deck.read_text("ascii"), ASM.read_text("ascii")),
                        encoding="ascii")
    cursor = folder / "native.cursor"
    output = common["run"](["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                           folder / "submit.log", env)
    job = common["job_id"](output)
    report = common["receipt"](folder, job, "RG906R",
                              PRIVATE_STEPS if private else common["GO_STEPS"], env, cursor)
    require("AUTHORIZATION CODE IS" in report and not common["CODE"].findall(report),
            "missing native execution boundary or unexpected interpreted execution")
    return {"job": job, "records": common["records"](report.rsplit("AUTHORIZATION CODE IS", 1)[1])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--candidate-only", action="store_true")
    modes.add_argument("--rebuild-and-verify", action="store_true")
    args = parser.parse_args()
    common = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
    expected = check(common)
    if args.check:
        print("DR.5 DEBUGINT CHECK PASS (no MVS)")
        return 0
    helper = runpy.run_path(str(ROOT / "tools/checks/run-dr5-bcplio-fix.py"))
    config = helper["CORE"]["load_config"]()
    cards = install_cards(helper, config, redact=False)
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-debugint"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "R1_REGRESSION_LOG_DIR", "R1_ACCEPTANCE_WORKDIR",
                "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    run = common["run"]
    result = {"status": "FAIL", "stage": "preflight", "expected": expected}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"], folder / "revision.log", env).strip()
        require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                        folder / "tracked-status.log", env).strip(), "tracked changes present")
        result["asm_sha256"] = hashlib.sha256(ASM.read_bytes()).hexdigest()
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-before.log", env)
        result["stage"] = "compile"
        generated = folder / "native.asm"
        output = run(["tools/bootstrap/compile-mvs", FIX / "source.bcpl",
                      "--job-name", "DR5DBG", "--compiler-image", "CAMBCOMP",
                      "--cambridge-parm", ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                      "--output", generated], folder / "compile.log", env)
        comp = common["job_id"](output)
        result["compiler_job"] = comp
        report = common["receipt"](folder, comp, "DR5DBG", common["CC_STEPS"], env)
        require(common["CODE"].findall(report) == ["0"] and generated.stat().st_size,
                "compiler completion or CODE missing")
        result["stage"] = "installed-baseline"
        result["baseline"] = native(common, folder / "baseline", generated, env)
        result["baseline"]["semantic_status"] = baseline_result(result["baseline"]["records"], expected)
        result["stage"] = "private-candidate"
        result["candidate"] = native(common, folder / "candidate", generated, env, private=True)
        require(result["candidate"]["records"] == expected, "private exact oracle mismatch")
        if args.rebuild_and_verify:
            require(hashlib.sha256(ASM.read_bytes()).hexdigest() == result["asm_sha256"] and
                    run(["git", "rev-parse", "HEAD"], folder / "revision-before-write.log", env).strip() == result["git_head"],
                    "revision or source changed after candidate")
            run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-write.log", env)
            result["stage"] = "stage-source"
            (folder / "writes-started").write_text("BOOT_ASM(BCPLMAIN), BOOT_OBJ(BCPLMAIN)\n")
            run(["tools/datasets/dspal", "put", "BOOT_ASM", "BCPLMAIN", ASM], folder / "put.log", env)
            staged = folder / "staged.asm"
            run(["tools/datasets/dspal", "get", "BOOT_ASM", "BCPLMAIN", staged], folder / "get.log", env)
            require([x.rstrip(" ") for x in staged.read_text("ascii").splitlines()] ==
                    ASM.read_text("ascii").splitlines(), "staged source mismatch")
            result["stage"] = "install-BCPLMAIN"
            deck = folder / "install.jcl"
            deck.write_text(cards, encoding="ascii")
            result["install_job"], _ = helper["submit"](folder, "BLDMNFIX", deck, BUILD_STEPS, env)
            result["stage"] = "installed-correction"
            result["installed"] = native(common, folder / "installed", generated, env)
            require(result["installed"]["records"] == expected, "installed exact oracle mismatch")
        result.update(status="PASS", stage="complete" if args.rebuild_and_verify else "candidate-only")
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result["reason"] = str(exc)
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        print("STOP: retain evidence; do not replay a partially completed write.")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
