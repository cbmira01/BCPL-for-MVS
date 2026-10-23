#!/usr/bin/env python3
"""R.5 source/installed regressions; BCPL compiler and IFOX run on MVS."""
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "bootstrap-toolchain/regression"
PROBE = ROOT / "bootstrap-toolchain/probes/r4-bcx-macros"
TRAIL = ROOT / "bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py"


def trail_module():
    spec = importlib.util.spec_from_file_location("r5_trail", TRAIL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selection(n):
    dirs = list(REG.glob(f"{n:03d}-*"))
    if not 146 <= n <= 158 or len(dirs) != 1:
        raise ValueError("invalid R.5 test number or directory")
    rows = (dirs[0] / "extension-selection.asm").read_text("ascii").splitlines()
    actual = [x for x in rows if not x.startswith("*")]
    expected = ([] if n in (146, 158) else
                ["         BCXSEL BCPLDEMO"] if n == 156 else
                ["         BCXSEL BCPLDEMO", "         BCXREQ BCPLDEMO"]
                if n == 157 else ["         BCXREQ BCPLDEMO"])
    if actual != expected:
        raise ValueError(f"wrong selection fixture in case {n}")
    return rows, bool(actual)


def make_deck(n, generated, jobcard, obj, mode="source", extension_dsn=None, macro_dsn=None):
    t = trail_module()
    selects, included = selection(n)
    if mode not in ("source", "installed"):
        raise ValueError("mode must be source or installed")
    if mode == "installed":
        for value, meaning in ((extension_dsn, "object"),
                               (macro_dsn, "macro")):
            if (not value or len(value) > 44 or
                not re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}"
                                 r"(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+",
                                 value)):
                raise ValueError(f"installed mode needs approved {meaning} PDS DSN")
    app = t.application_source(generated)
    main = t.checked_asm((ROOT / "bootstrap-toolchain/asm/bcplmain.asm")
                         .read_text("ascii"), "BCPLMAIN")
    rgs = t.checked_asm((ROOT / "bootstrap-toolchain/asm/bcplrgs.asm")
                        .read_text("ascii"), "BCPLRGS")
    if mode == "source":
        # Preserve the accepted source-mode deck exactly.
        macro_source = []
        for name in ("BCXPRE.asm", "BCXCAT.asm"):
            macro_source += t.checked_asm((PROBE / name).read_text("ascii"), name)
        macro_source += selects
        macro_source += t.checked_asm((PROBE / "BCXPOST.asm")
                                      .read_text("ascii"), "post")
        macro_input = ["//SYSIN    DD  *", *macro_source, "/*"]
    else:
        # Native IFOX reads installed macro members; no embedded definitions.
        macro_input = [
            f"//SYSIN    DD  DSN={macro_dsn}(BCXPRE),DISP=SHR",
            f"//         DD  DSN={macro_dsn}(BCXCAT),DISP=SHR",
            "//         DD  *", *selects, "/*",
            f"//         DD  DSN={macro_dsn}(BCXPOST),DISP=SHR",
        ]
    cards = [*jobcard,
             "//* R.5 OPTIONAL REGRESSION; BOOT_OBJ READ ONLY",
             *t.asm_step("ASMA", "R5APOBJ", app),
             *t.asm_step("ASMN", "R5NMOBJ", main),
             *t.asm_step("ASMR", "R5RGOBJ", rgs)]
    if included and mode == "source":
        pkg = t.checked_asm(
            (ROOT / "bootstrap-toolchain/extensions/bcpldemo/bcpldemo.asm")
            .read_text("ascii"), "combined BCPLDEMO")
        cards += t.asm_step("ASMD", "R5DEOBJ", pkg)
    cards += [
        "//ASMG     EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD',",
        "//             COND=(0,NE)",
        "//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSPUNCH DD  DSN=&&R5REGD,UNIT=SYSDA,",
        "//             SPACE=(80,(100,20)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSGO    DD  DUMMY",
        *macro_input,
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        f"//OBJ      DD  DSN={obj},DISP=SHR",
    ]
    if included:
        cards += (["//PKGA     DD  DSN=&&R5DEOBJ,DISP=(OLD,PASS)"]
                  if mode == "source" else
                  [f"//EXTLIB   DD  DSN={extension_dsn},DISP=SHR"])
    cards += [
        "//SYSLIN   DD  DSN=&&R5APOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&R5NMOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&R5RGOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&R5REGD,DISP=(OLD,PASS)",
        "//         DD  *",
        " INCLUDE OBJ(BCPLIO)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY R0APP",
        f" NAME R5X{n:03d}(R)",
        "/*",
        f"//SYSLMOD  DD  DSN=&&R5LOAD(R5X{n:03d}),",
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
    for i, line in enumerate(cards, 1):
        if not line.isascii() or len(line) > 71 or "\t" in line:
            raise ValueError(f"bad JCL/IFOX card {i}: {line!r}")
    if cards.count("/*") != (6 if included and mode == "source" else 5):
        raise ValueError("wrong in-stream terminator count")
    if any("DISP=MOD" in line or "DISP=(NEW,CATLG)" in line
           for line in cards):
        raise ValueError("persistent MVS dataset write forbidden")
    return "\n".join(cards) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("generated", nargs="?", type=Path)
    p.add_argument("output", nargs="?", type=Path)
    p.add_argument("--test-number", type=int)
    p.add_argument("--mode", choices=("source", "installed"),
                   default="source")
    p.add_argument("--extension-dsn")
    p.add_argument("--macro-dsn")
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    t = trail_module()
    if a.check:
        for n in range(146, 159):
            job = [f"//RG{n:03d}R JOB (BCPL),'R5 CHECK',CLASS=A"]
            value = make_deck(n, t.sample_generated(), job,
                              "HERC02.BCPL.BOOT.OBJ")
            print(f"CHECK R5 {n}: {len(value.splitlines())} cards")
        installed = make_deck(147, t.sample_generated(),
            ["//RG147R JOB (BCPL),'R5 CHECK',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ", "installed",
            "HERC02.BCPL.EXT.OBJ", "HERC02.BCPL.EXT.MAC")
        if "//EXTLIB   DD  DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR" not in installed:
            raise ValueError("installed-mode DD not generated")
        for member in ("BCXPRE", "BCXCAT", "BCXPOST"):
            if f"DSN=HERC02.BCPL.EXT.MAC({member}),DISP=SHR" not in installed:
                raise ValueError(f"installed-mode macro member {member} missing")
        if "BCXADD &PKG" in installed or "BCXCAT &PKG" in installed:
            raise ValueError("installed mode must not embed BCX macro definitions")
        print("CHECK installed-mode synthetic JCL PASS (not executed)")
        return
    if a.generated is None or a.output is None or a.test_number is None:
        p.error("generated, output and --test-number required")
    core = t.load_core()
    cfg = core.load_config()
    spec = cfg["datasets"]["BOOT_OBJ"]
    if (spec.get("content_type") != "object" or
        spec.get("dsorg") != "PO" or spec.get("recfm") != "FB" or
        int(spec.get("lrecl", 0)) != 80):
        raise ValueError("BOOT_OBJ must be a binary FB80 object PDS")
    obj = core.full_dsn(cfg, spec)
    if a.mode == "installed":
        for alias, supplied in (("EXT_OBJ", a.extension_dsn),
                                ("EXT_MAC", a.macro_dsn)):
            ext = cfg["datasets"].get(alias)
            if ext is None or core.full_dsn(cfg, ext) != supplied:
                raise ValueError(f"{alias} must match the approved manifest DSN")
            if (ext.get("dsorg") != "PO" or ext.get("recfm") != "FB" or
                int(ext.get("lrecl", 0)) != 80):
                raise ValueError(f"{alias} must be an FB80 PDS")
        if cfg["datasets"]["EXT_OBJ"].get("content_type") != "object":
            raise ValueError("EXT_OBJ must be an object library")
    job = core.authenticated_job_card(cfg, f"RG{a.test_number:03d}R",
                                       "R5 NATIVE REG", redact_password=False)
    generated = a.generated.read_bytes().decode("latin-1")
    value = make_deck(a.test_number, generated, job, obj,
                      a.mode, a.extension_dsn, a.macro_dsn)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(value, encoding="ascii", newline="\n")
    a.output.chmod(0o600)
    print(f"Prepared R.5 MVS {a.mode}-mode regression:", a.output)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("R.5 regression preparation FAILED: " + str(exc))
