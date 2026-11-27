#!/usr/bin/env python3
"""DR.5 read-only census of resident BLIB exports using the R.0 observer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "bootstrap-toolchain/probes/r0-export-trailer-probe"
SOURCE = ROOT / "tests/bootstrap/00-most-degenerate-bcpl-program/source.bcpl"
EXPECTED = [3, 4, 5, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68,
            69, 70, 74, 75, 76, 77, 78]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def assess(ledger):
    app = sorted(e["global"] for e in ledger["application"]["exports"])
    blib = sorted(e["global"] for e in ledger["installed_blib"]["exports"])
    require(app == [1], "unexpected application exports: " + repr(app))
    require(blib == EXPECTED, "unexpected BLIB exports: " + repr(blib))
    require(not ledger["app_blib_overlaps"], "application/BLIB overlap")
    return {"application_exports": app, "blib_exports": blib,
            "blib_max_global": ledger["installed_blib"]["max_global"]}


def deck_for(trailer, jobcard, observer, generated, dsn):
    deck = trailer["make_deck"](jobcard, observer, generated, dsn)
    # The historical R.0 deck predates the resident generic registrar.
    anchor = " INCLUDE OBJ(BLIB)\n"
    require(deck.count(anchor) == 1, "historical BLIB INCLUDE anchor changed")
    deck = deck.replace(anchor, anchor + " INCLUDE OBJ(BCPLRGS)\n"
                        " INCLUDE OBJ(BCPLREG)\n")
    includes = [row.strip() for row in deck.splitlines()
                if row.startswith(" INCLUDE ")]
    require(includes == ["INCLUDE OBJ(" + name + ")" for name in
                         ("BCPLMAIN", "BCPLIO", "BCPLMEM", "BCPLBYTE",
                          "BCPLAPT", "BLIB", "BCPLRGS", "BCPLREG")],
            "unexpected installed linkage")
    require(all(row.isascii() and len(row) <= 71 for row in deck.splitlines()),
            "invalid JCL card")
    return deck


def check(trailer, parser, observer):
    deck_for(trailer, ["//R0TRAIL JOB (BCPL),'TRAILER',CLASS=A,MSGCLASS=A"],
             observer, trailer["sample_generated"](), "TEST.BCPL.BOOT.OBJ")
    lines = []
    for name, slots in (("APP", [1]), ("BLIB", EXPECTED)):
        lines.append(f"R0TR {name} BEGIN")
        lines += [f"R0TR {name} OFF={4*n:08X} ADDR={4096+4*n:08X}"
                  for n in slots]
        lines += [f"R0TR {name} LIMIT={4*max(slots):08X}",
                  f"R0TR {name} END COUNT={len(slots):08X}"]
    lines.append("R0TR PASS APP AND INSTALLED BLIB")
    parsed = parser["parse_report"]("\n".join(lines))
    assess(parsed)
    # A structurally valid but different export census must not pass.
    parsed["installed_blib"]["exports"][0]["global"] = 71
    try:
        assess(parsed)
    except ValueError:
        pass
    else:
        raise ValueError("unexpected export accepted")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = p.parse_args()
    trailer = runpy.run_path(str(PROBE / "make-job.py"))
    parser = runpy.run_path(str(PROBE / "parse-report.py"))
    observer = (PROBE / "trailer-observer.asm").read_text("ascii")
    check(trailer, parser, observer)
    if args.check:
        print("DR.5 BLIB TRAILER CHECK PASS (no MVS)")
        return 0
    common = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
    run = common["run"]
    os.umask(0o077)
    base = ROOT / "workarea/dr5-blib-trailer"
    base.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=base))
    env = dict(os.environ)
    for key in ("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPL_TAPE_OBJECT_PDS",
                "R1_ACCEPTANCE", "CAMBRIDGE_IMAGE", "Q4_PUNCH_RESUME"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    result = {}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"],
                                 folder / "revision.log", env).strip()
        generated = folder / "app.asm"
        out = run(["tools/bootstrap/compile-mvs", SOURCE, "--job-name", "R0TRCMP",
                   "--compiler-image", "CAMBCOMP", "--cambridge-parm",
                   ROOT / "bootstrap-toolchain/bootstrap-cambridge/cambridge-options.txt",
                   "--output", generated], folder / "compile.log", env)
        comp = common["job_id"](out)
        result["compiler_job"] = comp
        report = common["receipt"](folder, comp, "R0TRCMP", common["CC_STEPS"], env)
        require([int(n) for n in common["CODE"].findall(report)] == [0],
                "Cambridge CODE not zero")
        result["generated_sha256"] = hashlib.sha256(generated.read_bytes()).hexdigest()
        core = trailer["load_core"]()
        config = core.load_config()
        spec = config["datasets"]["BOOT_OBJ"]
        require(spec["content_type"] == "object" and spec["dsorg"] == "PO"
                and spec["recfm"] == "FB" and int(spec["lrecl"]) == 80,
                "BOOT_OBJ must be binary FB80 object PDS")
        dsn = core.full_dsn(config, spec)
        cards = deck_for(trailer, core.authenticated_job_card(
            config, "R0TRAIL", "DR5 BLIB TRAILER", redact_password=False),
            observer, generated.read_bytes().decode("latin-1"), dsn)
        deck = folder / "native.jcl"
        deck.write_text(cards, encoding="ascii")
        cursor = folder / "native.cursor"
        out = run(["tools/mvs/submit-jcl", "--cursor-file", cursor, deck],
                  folder / "submit.log", env)
        job = common["job_id"](out)
        result["job"] = job
        steps = [("ASMT", "IFOX00"), ("ASMA", "IFOX00"), ("LKED", "IEWL"),
                 ("GO", "PGM=*.LKED.SYSLMOD")]
        report = common["receipt"](folder, job, "R0TRAIL", steps, env, cursor)
        require("AUTHORIZATION CODE IS" in report, "missing IEWL boundary")
        ledger = parser["parse_report"](report.rsplit("AUTHORIZATION CODE IS", 1)[1])
        (folder / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
        result.update(assess(ledger), status="PASS")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result.update(status="FAIL", reason=str(exc))
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 BLIB TRAILER " + result["status"])
    print("Evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
