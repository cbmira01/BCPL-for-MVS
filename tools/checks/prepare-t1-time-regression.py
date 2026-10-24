#!/usr/bin/env python3
"""BCPLTIME T.1 optional-extension native regression deck: source/installed."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "bootstrap-toolchain/regression"
R0 = ROOT / "bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py"
BCX = ROOT / "bootstrap-toolchain/extensions/bcx"
TIME = ROOT / "bootstrap-toolchain/extensions/bcpltime"
DEMO = ROOT / "bootstrap-toolchain/extensions/bcpldemo"

# Case-specific, exact native IFOX selection records. Never synthesize
# BCPLREG or IEWL INCLUDE controls on the host.
SELECTIONS = {
    159: ("BCXREQ BCPLTIME",),
    160: ("BCXREQ BCPLDEMO", "BCXREQ BCPLTIME"),
    161: ("BCXREQ BCPLTIME", "BCXREQ BCPLDEMO"),
    162: ("BCXSEL BCPLTIME", "BCXREQ BCPLTIME",
          "BCXREQ BCPLDEMO", "BCXREQ BCPLTIME"),
}


def load_r0():
    spec = importlib.util.spec_from_file_location("t1_r0", R0)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def selection(number: int) -> list[str]:
    if number not in SELECTIONS:
        raise ValueError("T.1 test number must be 159..162")
    found = list(REG.glob(f"{number:03d}-*"))
    if len(found) != 1:
        raise ValueError(f"expected one regression directory for {number}")
    rows = (found[0] / "time-selection.asm").read_text("ascii").splitlines()
    expected = ["         " + x for x in SELECTIONS[number]]
    if rows != expected:
        raise ValueError(f"case {number}: selection fixture changed")
    return rows


def asm(name: str, r0) -> list[str]:
    path = (TIME / "bcpltime.asm" if name == "time" else
            DEMO / "bcpldemo.asm" if name == "demo" else
            ROOT / f"bootstrap-toolchain/asm/{name}.asm")
    return r0.checked_asm(path.read_text("ascii"), str(path))


def make_deck(number: int, generated: str, jobcard: list[str],
              boot_obj: str, mode: str = "source", ext_obj: str | None = None,
              ext_mac: str | None = None) -> str:
    if not jobcard or not re.match(rf"^//RG{number:03d}R\s+JOB\s", jobcard[0]):
        raise ValueError("authenticated regression job card required")
    if mode not in ("source", "installed"):
        raise ValueError("mode must be source or installed")
    if mode == "installed" and (not ext_obj or not ext_mac):
        raise ValueError("installed mode requires approved object/macro PDS")
    t = load_r0()
    selected = selection(number)
    cards = [*jobcard,
             "//* T.1 OPTIONAL REGRESSION: NO PERMANENT WRITES",
             *t.asm_step("ASMA", "T1APOBJ", t.application_source(generated)),
             *t.asm_step("ASMN", "T1NMOBJ", asm("bcplmain", t)),
             *t.asm_step("ASMR", "T1RGOBJ", asm("bcplrgs", t))]
    if mode == "source":
        if number != 159:
            cards += t.asm_step("ASMD", "T1DEOBJ", asm("demo", t))
        cards += t.asm_step("ASMT", "T1TMOBJ", asm("time", t))
        macro_rows = []
        for path in (BCX / "BCXPRE.asm", TIME / "t1-catalog.asm"):
            macro_rows.extend(t.checked_asm(path.read_text("ascii"), str(path)))
        macro_rows.extend(selected)
        macro_rows.extend(t.checked_asm((BCX / "BCXPOST.asm").read_text("ascii"),
                                        "BCXPOST"))
        macro_input = ["//SYSIN    DD  *", *macro_rows, "/*"]
    else:
        # Future approved installed mode: consume resident macros, not
        # embedded source. The production BCXCAT must first be updated.
        macro_input = [f"//SYSIN    DD  DSN={ext_mac}(BCXPRE),DISP=SHR",
                       f"//         DD  DSN={ext_mac}(BCXCAT),DISP=SHR",
                       "//         DD  *", *selected, "/*",
                       f"//         DD  DSN={ext_mac}(BCXPOST),DISP=SHR"]
    cards += [
        "//ASMG     EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSPUNCH DD  DSN=&&T1REGD,UNIT=SYSDA,",
        "//             SPACE=(80,(100,20)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSGO    DD  DUMMY",
        *macro_input,
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        "//             COND=(0,NE)",
        f"//OBJ      DD  DSN={boot_obj},DISP=SHR",
    ]
    if mode == "source":
        if number != 159:
            cards += ["//DEMOOBJ  DD  DSN=&&T1DEOBJ,DISP=(OLD,PASS)"]
        cards += ["//TIMEOBJ  DD  DSN=&&T1TMOBJ,DISP=(OLD,PASS)"]
    else:
        cards += [f"//EXTLIB   DD  DSN={ext_obj},DISP=SHR"]
    cards += [
        "//SYSLIN   DD  DSN=&&T1APOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&T1NMOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&T1RGOBJ,DISP=(OLD,PASS)",
        "//         DD  DSN=&&T1REGD,DISP=(OLD,PASS)",
        "//         DD  *",
        " INCLUDE OBJ(BCPLIO)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY R0APP",
        f" NAME T1X{number:03d}(R)",
        "/*",
        f"//SYSLMOD  DD  DSN=&&T1LOAD(T1X{number:03d}),",
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
    for line_no, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or "\t" in row:
            raise ValueError(f"bad JCL/IFOX card {line_no}: {row!r}")
    expected_streams = (7 if number != 159 else 6) if mode == "source" else 5
    if cards.count("/*") != expected_streams:
        raise ValueError("incorrect in-stream source count")
    if any("DISP=MOD" in row or "CATLG" in row or "DISP=OLD" in row
           for row in cards):
        raise ValueError("unexpected permanent write")
    return "\n".join(cards) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("generated", nargs="?", type=Path)
    p.add_argument("output", nargs="?", type=Path)
    p.add_argument("--test-number", type=int)
    p.add_argument("--mode", choices=("source", "installed"), default="source")
    p.add_argument("--extension-dsn")
    p.add_argument("--macro-dsn")
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    t = load_r0()
    if a.check:
        for number in SELECTIONS:
            job = [f"//RG{number:03d}R JOB (BCPL),'T1 CHECK',CLASS=A"]
            deck = make_deck(number, t.sample_generated(), job,
                             "HERC02.BCPL.BOOT.OBJ")
            print(f"T.1 {number} source: {len(deck.splitlines())} cards OK")
        return
    if a.generated is None or a.output is None or a.test_number is None:
        p.error("generated, output and --test-number required")
    core = t.load_core()
    cfg = core.load_config()
    boot = cfg["datasets"]["BOOT_OBJ"]
    if not (boot.get("content_type") == "object" and
            boot.get("dsorg") == "PO" and boot.get("recfm") == "FB" and
            int(boot.get("lrecl", 0)) == 80):
        raise ValueError("BOOT_OBJ must be binary FB80 PDS")
    def dsn(alias: str, expected_type: str | None) -> str:
        spec = cfg["datasets"][alias]
        if not (spec.get("dsorg") == "PO" and spec.get("recfm") == "FB" and
                int(spec.get("lrecl", 0)) == 80 and
                (expected_type is None or spec.get("content_type") == expected_type)):
            raise ValueError(f"invalid {alias} PDS definition")
        return core.full_dsn(cfg, spec)
    obj = dsn("BOOT_OBJ", "object")
    if a.mode == "installed":
        obj_ext = dsn("EXT_OBJ", "object")
        mac_ext = dsn("EXT_MAC", None)
        if a.extension_dsn != obj_ext or a.macro_dsn != mac_ext:
            raise ValueError("installed object/macro DSNs must match manifest")
    job = core.authenticated_job_card(cfg, f"RG{a.test_number:03d}R",
                                       "T1 TIME REG", redact_password=False)
    deck = make_deck(a.test_number,
                     a.generated.read_bytes().decode("latin-1"), job, obj,
                     a.mode, a.extension_dsn, a.macro_dsn)
    if not a.output.resolve().is_relative_to((ROOT / "workarea").resolve()):
        raise ValueError("JCL output must reside under ignored workarea")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(deck, encoding="ascii", newline="\n")
    a.output.chmod(0o600)
    print(f"Prepared BCPLTIME T.1 {a.mode}-mode JCL: {a.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit("BCPLTIME T.1 job preparation failed: " + str(exc))
