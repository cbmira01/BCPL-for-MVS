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
    args = ap.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    deck = out / "build-runtime-objects.jcl"
    deck.unlink(missing_ok=True)

    # Exact source transformations fail if BCPLMAIN's contract has drifted.
    source = ROOT / "asm/bcplmain-wip.asm"
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
        ("BCPLBYTE", ROOT / "asm/bcplbyte.asm"),
        ("BCPLAPT", ROOT / "asm/bcplapt.asm"),
        ("BCPLMEM", ROOT / "asm/bcplmem.asm"),
    ]
    for _, file in sources:
        run(CHECKS / "check-asm-source.py", file)
    core_path = ROOT / "tools/dspal-core.py"
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
        "//* BCPL NATIVE RUNTIME: FOUR INDEPENDENT FB80 OBJECT MEMBERS",
        "//* REVIEW BEFORE SUBMISSION: INSTALL STEPS REPLACE OBJ MEMBERS.",
        "//* NOT ATOMIC: FAILURE MAY LEAVE A PARTLY UPDATED OBJECT LIBRARY.",
        "//* PRESERVE EXISTING OBJ(BLIB); NO BLIB COMPILATION HERE.",
    ])
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
            f"//I{step[1:]:<7} EXEC PGM=IEBGENER,COND=(0,NE,{step})",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSIN    DD DUMMY",
            f"//SYSUT1   DD DSN=&&{tmp},DISP=(OLD,DELETE)",
            f"//SYSUT2   DD DSN={objdsn}({name}),DISP=SHR",
            "//*",
        ])
    lines.append("//")
    for i, line in enumerate(lines, 1):
        if len(line) > 71:
            raise ValueError(f"JCL card {i} exceeds column 71: {line!r}")
    deck.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"Staged: {deck}")
    print("Four object members: BCPLMAIN BCPLBYTE BCPLAPT BCPLMEM")
    print("BCPLMAIN depends on resident OBJ(BLIB) at linkage.")
    print("NOT submitted. Inspect and submit only after approving non-atomic PDS changes.")
    print("Run 'tools/dspal stat OBJ' first; preserve the prior object library.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as err:
        raise SystemExit(f"prepare-runtime-object-library: {err}")
