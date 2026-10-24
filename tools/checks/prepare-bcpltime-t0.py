#!/usr/bin/env python3
"""Generate one temporary-only BCPLTIME T.0 IFOX/IEWL/GO job.

--check uses a synthetic CG370 source and dummy JOB card; no credentials,
MVS submission, or dataset updates. Normal mode uses the project's
local authenticated JOB-card mechanism and a saved real compiler output.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / "bootstrap-toolchain/extensions/bcpltime"
BCX = ROOT / "bootstrap-toolchain/extensions/bcx"
TRAIL = ROOT / "bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py"


def trailer_helper():
    spec = importlib.util.spec_from_file_location("bcpltime_trailer", TRAIL)
    if spec is None or spec.loader is None:
        raise ValueError("missing accepted R.0 native-code JCL helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_cards(helper, path):
    return helper.checked_asm(path.read_text(encoding="ascii"), path.name)


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    """Construct T.0 JCL using R.5's temporary object/BCX link sequence."""
    t = trailer_helper()
    if not jobcard or not re.match(r"^//T0TIME\s+JOB\b", jobcard[0]):
        raise ValueError("expected authenticated T0TIME JOB card")
    if not re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+", obj_dsn):
        raise ValueError("invalid BOOT_OBJ dataset name")

    app = t.application_source(generated)
    main = read_cards(t, ROOT / "bootstrap-toolchain/asm/bcplmain.asm")
    rgs = read_cards(t, ROOT / "bootstrap-toolchain/asm/bcplrgs.asm")
    ext = read_cards(t, EXT / "bcpltime.asm")
    macros = []
    for path in (BCX / "BCXPRE.asm", EXT / "t0-catalog.asm",
                 EXT / "t0-selection.asm", BCX / "BCXPOST.asm"):
        macros += read_cards(t, path)

    cards = [*jobcard,
             "//* BCPLTIME T.0 TEMPORARY ONLY. BOOT_OBJ READ ONLY.",
             *t.asm_step("ASMA", "T0APOBJ", app),
             *t.asm_step("ASMN", "T0NMOBJ", main),
             *t.asm_step("ASMR", "T0RGOBJ", rgs),
             *t.asm_step("ASMT", "T0TMOBJ", ext),
             "//ASMG     EXEC PGM=IFOX00,REGION=256K,",
             "//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD',",
             "//             COND=(0,NE)",
             "//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR",
             "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))",
             "//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
             "//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
             "//SYSPRINT DD  SYSOUT=*",
             "//SYSPUNCH DD  DSN=&&T0REGD,UNIT=SYSDA,",
             "//             SPACE=(80,(100,20)),DISP=(NEW,PASS),",
             "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
             "//SYSGO    DD  DUMMY",
             "//SYSIN    DD  *", *macros, "/*",
             "//LKED     EXEC PGM=IEWL,REGION=256K,",
             "//             PARM='NCAL,LIST,XREF,MAP',",
             "//             COND=(0,NE)",
             f"//OBJ      DD  DSN={obj_dsn},DISP=SHR",
             "//TIMEOBJ  DD  DSN=&&T0TMOBJ,DISP=(OLD,PASS)",
             "//SYSLIN   DD  DSN=&&T0APOBJ,DISP=(OLD,PASS)",
             "//         DD  DSN=&&T0NMOBJ,DISP=(OLD,PASS)",
             "//         DD  DSN=&&T0RGOBJ,DISP=(OLD,PASS)",
             "//         DD  DSN=&&T0REGD,DISP=(OLD,PASS)",
             "//         DD  *",
             " INCLUDE OBJ(BCPLIO)",
             " INCLUDE OBJ(BCPLMEM)",
             " INCLUDE OBJ(BCPLBYTE)",
             " INCLUDE OBJ(BCPLAPT)",
             " INCLUDE OBJ(BLIB)",
             " ENTRY R0APP",
             " NAME T0TIME(R)",
             "/*",
             "//SYSLMOD  DD  DSN=&&T0LOAD(T0TIME),",
             "//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),",
             "//             DISP=(NEW,PASS)",
             "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
             "//SYSPRINT DD  SYSOUT=*",
             "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
             "//             TIME=(,2),COND=(0,NE,LKED)",
             "//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,",
             "//             BLKSIZE=132)",
             "//SYSUDUMP DD  SYSOUT=*",
             "//",
             ]
    for n, line in enumerate(cards, 1):
        if not line.isascii() or len(line) > 71 or "\t" in line:
            raise ValueError(f"invalid JCL/IFOX card {n}: {line!r}")
    # 4 object assemblies, 1 BCX assembler, 1 IEWL SYSIN terminator.
    if cards.count("/*") != 6:
        raise ValueError("incorrect JCL in-stream termination count")
    if any("DISP=MOD" in row or "CATLG" in row for row in cards):
        raise ValueError("persistent output forbidden in T.0")
    if any("//EXTLIB" in row or "(BCPLDEMO)" in row for row in cards):
        raise ValueError("T.0 must not reference installed extensions")
    if cards.count(" ENTRY R0APP") != 1:
        raise ValueError("explicit application ENTRY required")
    return "\n".join(cards) + "\n"


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated", nargs="?", type=Path,
                        help="CG370 output from tools/bootstrap/compile-mvs")
    parser.add_argument("output", nargs="?", type=Path,
                        help="ignored workarea/ destination for authenticated JCL")
    parser.add_argument("--check", action="store_true",
                        help="offline only; no local credentials or MVS writes")
    args = parser.parse_args()
    t = trailer_helper()
    if args.check:
        if args.generated or args.output:
            parser.error("--check takes no positional paths")
        deck = make_deck(t.sample_generated(),
                         ["//T0TIME JOB (BCPL),'T0 OFFLINE',CLASS=A"],
                         "HERC02.BCPL.BOOT.OBJ")
        print(f"BCPLTIME T.0 JCL check: PASS ({len(deck.splitlines())} cards; "
              "synthetic; not MVS execution)")
        return
    if args.generated is None or args.output is None:
        parser.error("generated and output are required")
    output = args.output.resolve()
    workarea = (ROOT / "workarea").resolve()
    if workarea not in output.parents:
        raise ValueError("authenticated JCL must remain inside workarea/")
    generated = args.generated.read_bytes().decode("latin-1")
    core = t.load_core()
    config = core.load_config()
    obj_spec = config["datasets"]["BOOT_OBJ"]
    if (obj_spec.get("content_type") != "object" or
        obj_spec.get("dsorg") != "PO" or
        obj_spec.get("recfm") != "FB" or
        int(obj_spec.get("lrecl", 0)) != 80):
        raise ValueError("BOOT_OBJ is not an FB80 object PDS")
    obj_dsn = core.full_dsn(config, obj_spec)
    jobcard = core.authenticated_job_card(
        config, "T0TIME", "BCPLTIME T0", redact_password=False)
    deck = make_deck(generated, jobcard, obj_dsn)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deck, encoding="ascii", newline="\n")
    output.chmod(0o600)
    print(f"Prepared temporary-only BCPLTIME T.0 JCL: {output}")


if __name__ == "__main__":
    try:
        run()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f"BCPLTIME T.0 job preparation FAILED: {exc}")
