#!/usr/bin/env python3
"""DR.5 registrar: private and installed IFOX/IEWL/GO contract checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIOR = runpy.run_path(str(ROOT / "tools/checks/run-dr5-bcplio-fix.py"))
TRAIL = runpy.run_path(str(ROOT / "bootstrap-toolchain/probes"
                         / "r0-export-trailer-probe/make-job.py"))
require, run, submit = (PRIOR[x] for x in ("require", "run", "submit"))
CORE = PRIOR["CORE"]
ASM = ROOT / "bootstrap-toolchain/asm/bcplrgs.asm"
PROBE = ROOT / "bootstrap-toolchain/probes/dr5-registrar/registrar-contract.asm"


def install_cards(config, redact=True):
    # Reuse the proven one-member IFOX/IEBGENER/readback/IEBCOMPR deck.
    cards = PRIOR["install_cards"](config, redact)
    require(cards.count("(BCPLIO)") == 3 and cards.count("BLDIOFIX") == 1,
            "one-member installation template changed")
    cards = cards.replace("BCPLIO", "BCPLRGS").replace("BLDIOFIX", "BLDRGFIX")
    require(all(len(x) <= 71 and x.isascii() for x in cards.splitlines()),
            "invalid registrar installation card")
    require(cards.count("(BCPLRGS),DISP=OLD") == 1 and
            "(BCPLIO)" not in cards, "unexpected installation write scope")
    return cards


def probe_cards(config, installed, redact=True):
    name = "DR5RGIN" if installed else "DR5RGPR"
    spec = config["datasets"]["BOOT_OBJ"]
    require(spec["content_type"] == "object" and spec["dsorg"] == "PO"
            and spec["recfm"] == "FB" and int(spec["lrecl"]) == 80,
            "BOOT_OBJ must be FB80 object PDS")
    dsn = CORE["full_dsn"](config, spec)
    cards = CORE["authenticated_job_card"](config, name, "RG CONTRACT", redact)
    cards += TRAIL["asm_step"]("ASMT", "RGTEST",
                              TRAIL["checked_asm"](PROBE.read_text("ascii"), "probe"))
    steps = [("ASMT", "IFOX00")]
    if not installed:
        cards += TRAIL["asm_step"]("ASMR", "RGPRIV",
                                  TRAIL["checked_asm"](ASM.read_text("ascii"), "registrar"))
        steps.append(("ASMR", "IFOX00"))
    cards += [
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE)",
    ]
    if installed:
        cards += [f"//OBJ      DD DSN={dsn},DISP=SHR"]
    cards += ["//SYSLIN   DD DSN=&&RGTEST,DISP=(OLD,DELETE)"]
    if not installed:
        cards += ["//         DD DSN=&&RGPRIV,DISP=(OLD,DELETE)"]
    cards += ["//         DD *"]
    if installed:
        cards += [" INCLUDE OBJ(BCPLRGS)"]
    cards += [
        " ENTRY RGTEST",
        " NAME RGTEST(R)",
        "/*",
        "//SYSLMOD  DD DSN=&&GOSET(RGTEST),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),COND=(0,NE)",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    require(all(len(x) <= 71 and x.isascii() for x in cards),
            "invalid probe card")
    require(sum(" INCLUDE OBJ(BCPLRGS)" == x for x in cards) == int(installed),
            "incorrect registrar source selection")
    require(not any("DISP=MOD" in x or "(BCPLRGS),DISP=OLD" in x for x in cards),
            "unexpected persistent probe write")
    return name, "\n".join(cards) + "\n", steps + [("LKED", "IEWL"), ("GO", None)]


def check():
    p = subprocess.run(["python3", "tools/checks/check-asm-source.py",
                        str(ASM), str(PROBE)], cwd=ROOT, capture_output=True, text=True)
    require(p.returncode == 0, p.stdout + p.stderr)
    cfg = {"mvs": {"hlq": "DR5", "batch_user": "TEST"},
           "datasets": {"BOOT_ASM": {"dsn": "BCPL.BOOT.ASM", "dsorg": "PO",
                                     "recfm": "FB", "lrecl": 80},
                        "BOOT_OBJ": {"dsn": "BCPL.BOOT.OBJ", "dsorg": "PO",
                                     "recfm": "FB", "lrecl": 80,
                                     "content_type": "object"}}}
    source = PROBE.read_text("ascii")
    require(source.count("         BAL   8,CHECK") == 18, "probe case count")
    for installed in (False, True):
        _, deck, steps = probe_cards(cfg, installed)
        require(deck.count(source.rstrip("\n")) == 1, "probe source missing")
        require(deck.count(ASM.read_text("ascii").rstrip("\n")) == int(not installed),
                "registrar source selection mismatch")
        require("PASSWORD=REDACTED" in deck and len(steps) == (3 if installed else 4),
                "invalid probe shape")
    deck = install_cards(cfg)
    require("DR5.BCPL.BOOT.ASM(BCPLRGS)" in deck and
            "DR5.BCPL.BOOT.OBJ(BCPLRGS)" in deck and
            "PASSWORD=REDACTED" in deck, "invalid install deck")


def probe(folder, config, installed, env):
    name, cards, steps = probe_cards(config, installed, redact=False)
    deck = folder / (name + ".jcl")
    deck.write_text(cards, encoding="ascii")
    job, _ = submit(folder, name, deck, steps, env)
    # GO returns zero only after all 18 exact status/publication assertions
    # and both reverse-order/once finalizer checks. Any failure returns 8+n.
    print(f"{name} JOB {job} PASS (18 registrar cases, finalization)", flush=True)
    return job


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--candidate-only", action="store_true")
    modes.add_argument("--installed-only", action="store_true")
    modes.add_argument("--rebuild-and-verify", action="store_true")
    args = p.parse_args()
    check()
    if args.check:
        print("DR.5 registrar CHECK PASS (no MVS)")
        return 0
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-registrar-fix"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    env = dict(os.environ)
    result = {"status": "FAIL", "stage": "preflight"}
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"],
                                 folder / "revision.log", env).strip()
        require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                        folder / "tracked-status.log", env).strip(), "tracked changes present")
        result["asm_sha256"] = hashlib.sha256(ASM.read_bytes()).hexdigest()
        result["probe_sha256"] = hashlib.sha256(PROBE.read_bytes()).hexdigest()
        config = CORE["load_config"]()
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-before.log", env)
        if not args.installed_only:
            result["stage"] = "private-candidate"
            result["private_job"] = probe(folder, config, False, env)
            result["private_cases"] = 18
        if args.rebuild_and_verify:
            require(hashlib.sha256(ASM.read_bytes()).hexdigest() == result["asm_sha256"]
                    and hashlib.sha256(PROBE.read_bytes()).hexdigest() == result["probe_sha256"],
                    "source changed after candidate test")
            require(run(["git", "rev-parse", "HEAD"], folder / "revision-before-write.log",
                        env).strip() == result["git_head"], "revision changed")
            require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                            folder / "status-before-write.log", env).strip(),
                    "tracked changes before write")
            run(["tools/reconstruction/jes-idle", "--live"], folder / "idle-write.log", env)
            cards = install_cards(config, redact=False)
            result["stage"] = "stage-source"
            (folder / "writes-started").write_text("BOOT_ASM(BCPLRGS), BOOT_OBJ(BCPLRGS)\n")
            run(["tools/datasets/dspal", "put", "BOOT_ASM", "BCPLRGS", ASM],
                folder / "put.log", env)
            readback = folder / "staged.asm"
            run(["tools/datasets/dspal", "get", "BOOT_ASM", "BCPLRGS", readback],
                folder / "get.log", env)
            def logical_cards(path):
                return [x.rstrip(" ") for x in path.read_text("ascii").splitlines()]
            require(logical_cards(readback) == logical_cards(ASM), "staged source mismatch")
            result["stage"] = "install-BCPLRGS"
            deck = folder / "install.jcl"
            deck.write_text(cards, encoding="ascii")
            result["install_job"], _ = submit(folder, "BLDRGFIX", deck,
                                               PRIOR["BUILD_STEPS"], env)
            print(f"BLDRGFIX JOB {result['install_job']} PASS (IFOX, IEBCOMPR)", flush=True)
        if args.rebuild_and_verify or args.installed_only:
            result["stage"] = "installed-probe"
            result["installed_job"] = probe(folder, config, True, env)
            result["installed_cases"] = 18
        result["stage"] = "complete"
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
