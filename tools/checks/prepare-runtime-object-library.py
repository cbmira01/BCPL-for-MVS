#!/usr/bin/env python3
"""Stage four native runtime object decks for the dspal-managed MVS OBJ PDS.

Preparation only: emits JCL; NEVER submits it or changes MVS datasets.
BCPLMAIN is derived strictly from the frozen WIP baseline via the tested
externalizers. No instrumented regression-083 symbols are installed.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "tools/checks"


def run(*args: str) -> None:
    subprocess.run([sys.executable, *map(str, args)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path,
                    default=ROOT / "workarea/runtime-object-library")
    ap.add_argument("--only-main", action="store_true",
                    help="assemble/install only BCPLMAIN; preserve all other OBJ members")
    ap.add_argument("--main-and-mem", action="store_true",
                    help="install BCPLMAIN and BCPLMEM as a coordinated pair")
    args = ap.parse_args()
    if args.only_main and args.main_and_mem:
        ap.error("--only-main and --main-and-mem are mutually exclusive")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    deck = out / "build-runtime-objects.jcl"
    deck.unlink(missing_ok=True)

    # Exact source transformations fail if BCPLMAIN's contract has drifted.
    source = ROOT / "native-compiler/asm/history/bcplmain-wip.asm"
    for name, script in (
        ("byte", "externalize-bcplbyte.py"),
        ("apt", "externalize-bcplapt.py"),
        ("mem", "externalize-bcplmem.py"),
    ):
        dest = out / f"bcplmain-minus-{name}.asm"
        dest.unlink(missing_ok=True)
        run(CHECKS / script, source, dest)
        source = dest
    # The installed BCPLMAIN object registers BLIB's globals on startup.
    # Reuse the proven source transformation from regression 069.
    stage2 = ROOT / "native-compiler/regression/069-independent-blib-object/prepare-stage2.py"
    spec2 = importlib.util.spec_from_file_location("blib_stage2_obj", stage2)
    if spec2 is None or spec2.loader is None:
        raise RuntimeError("unable to load BLIB registration implementation")
    module2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(module2)
    registered = out / "bcplmain-object.asm"
    registered.unlink(missing_ok=True)
    registered.write_text(module2.inject_runtime(source.read_text(encoding="ascii")),
                          encoding="ascii", newline="\n")
    source = registered
    sources = [
        ("BCPLMAIN", source),
        ("BCPLBYTE", ROOT / "native-compiler/asm/bcplbyte.asm"),
        ("BCPLAPT", ROOT / "native-compiler/asm/bcplapt.asm"),
        ("BCPLMEM", ROOT / "native-compiler/asm/bcplmem.asm"),
    ]
    if args.only_main:
        sources = sources[:1]
    elif args.main_and_mem:
        sources = [sources[0], sources[3]]
    for _, file in sources:
        run(CHECKS / "check-asm-source.py", file)
    core_path = ROOT / "tools/datasets/dspal-core.py"
    spec = importlib.util.spec_from_file_location("dspal_core_obj", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load dspal core")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    conf = core.load_config()
    objdsn, _ = core.resolve_dsn(conf, "OBJ")
    if objdsn.upper() != "HERC02.BCPL.OBJ":
        raise ValueError(f"unexpected OBJ DSN {objdsn}; inspect installer")
    header = core.authenticated_job_card(conf, "BCOBJBLD", "BCPL RUNTIME OBJ",
                                         redact_password=False)
    lines = list(header)
    lines.extend([
        ("//* BCPLMAIN ONLY: PRESERVE ALL OTHER OBJ MEMBERS" if args.only_main
         else "//* BCPLMAIN+BCPLMEM: PRESERVE OTHER OBJ MEMBERS" if args.main_and_mem
         else "//* BCPL NATIVE RUNTIME: FOUR INDEPENDENT FB80 OBJECT MEMBERS"),
        "//* REVIEW BEFORE SUBMISSION: INSTALL STEPS REPLACE OBJ MEMBERS.",
        "//* NOT ATOMIC: FAILURE MAY LEAVE A PARTLY UPDATED OBJECT LIBRARY.",
        "//* PRESERVE EXISTING OBJ(BLIB); NO BLIB COMPILATION HERE.",
    ])
    install_steps = []
    for name, source_path in sources:
        step = "A" + name[4:] if name != "BCPLMAIN" else "AMAIN"
        # Step names: AMAIN, ABYTE, AAPT, AMEM.
        step = {"BCPLMAIN": "AMAIN", "BCPLBYTE": "ABYTE",
                "BCPLAPT": "AAPT", "BCPLMEM": "AMEM"}[name]
        tmp = {"BCPLMAIN": "RTMAIN", "BCPLBYTE": "RTBYTE",
               "BCPLAPT": "RTAPT", "BCPLMEM": "RTMEM"}[name]
        cards = source_path.read_text(encoding="ascii").splitlines()
        if any(line == "/*" or line.startswith("//") or len(line) > 71
               for line in cards):
            raise ValueError(f"unsafe inline assembler source: {source_path}")
        lines.extend([
            f"//{step:<8} EXEC PGM=IFOX00,REGION=256K,",
            "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
            "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
            "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSPUNCH DD DUMMY",
            f"//SYSGO    DD DSN=&&{tmp},UNIT=SYSDA,",
            "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSIN    DD *",
            *cards,
            "/*",
            "//*",
        ])
        install_steps.append((name, step, tmp))
    # Do not change the PDS until every selected assembly succeeded.
    # Installation is gated on assembler RC=0000.
    # An I/O failure during a subsequent install is still non-atomic.
    prior = [step for _, step, _ in install_steps]
    for name, step, tmp in install_steps:
        cond = "COND=(" + ",".join(f"(0,NE,{item})" for item in prior) + ")"
        # JCL continuation at whole tuple boundaries.
        tuples = [f"(0,NE,{item})" for item in prior]
        chunks = []
        line = "//             COND=("
        for i, item in enumerate(tuples):
            token = item + ("," if i != len(tuples) - 1 else ")")
            if len(line + token) > 71:
                chunks.append(line)
                line = "//             " + token
            else:
                line += token
        chunks.append(line)
        lines.extend([
            f"//I{step[1:]:<7} EXEC PGM=IEBGENER,",
            *chunks,
            "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY",
            f"//SYSUT1   DD DSN=&&{tmp},DISP=(OLD,DELETE)",
            f"//SYSUT2   DD DSN={objdsn}({name}),DISP=SHR",
            "//*",
        ])
        prior.append("I" + step[1:])
    lines.append("//")
    for i, line in enumerate(lines, 1):
        if len(line) > 71:
            raise ValueError(f"JCL card {i} exceeds column 71: {line!r}")
    deck.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"Staged: {deck}")
    print("Selected object members: " + " ".join(name for name, _ in sources))
    print("BCPLMAIN depends on resident OBJ(BLIB) at linkage.")
    print("NOT submitted. Inspect the deck before replacing any OBJ member.")
    print("Run 'tools/datasets/dspal stat OBJ' first; preserve the prior object library.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as err:
        raise SystemExit(f"prepare-runtime-object-library: {err}")
