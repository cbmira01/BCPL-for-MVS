#!/usr/bin/env python3
"""Prepare Q.0 two-program MVS DASD QSAM experiments; do not install objects."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROFILES = {
    "fb": ("QS0FBD", "fb-write.asm", "fb-read.asm", "Q0FBW", "Q0FBR", "FB", 80, 800),
    "v": ("QS0VQD", "v-write.asm", "v-read.asm", "Q0VW", "Q0VR", "V", 100, 104),
    "vb": ("QS0VBD", "v-write.asm", "v-read.asm", "Q0VW", "Q0VR", "VB", 100, 404),
}


def config_module():
    path = ROOT / "tools/datasets/dspal-core.py"
    spec = importlib.util.spec_from_file_location("q0_dasd_dspal", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load project configuration: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def asm_source(name: str) -> str:
    path = HERE / name
    result = path.read_text(encoding="ascii")
    for n, line in enumerate(result.splitlines(), 1):
        if len(line) > 71 or line == "/*" or line.startswith("//"):
            raise ValueError(f"bad IFOX card {path}:{n}")
    if not result.strip():
        raise ValueError(f"empty IFOX source {path}")
    return result.rstrip("\n")


def asm_step(step: str, temporary_obj: str, source: str) -> list[str]:
    return [
        f"//{step:<8} EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD  SYSOUT=*",
        "//SYSPUNCH DD  DUMMY",
        f"//SYSGO    DD  DSN=&&{temporary_obj},UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD  *",
        *source.splitlines(),
        "/*",
    ]


def link_step(step: str, source_obj: str, temp_mod: str,
              member: str, entry: str, asm_step_name: str) -> list[str]:
    return [
        f"//{step:<8} EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',",
        f"//             COND=(0,NE,{asm_step_name})",
        f"//SYSLIN   DD  DSN=&&{source_obj},DISP=(OLD,DELETE)",
        "//         DD  *",
        f" ENTRY {entry}",
        f" NAME {member}(R)",
        "/*",
        f"//SYSLMOD  DD  DSN=&&{temp_mod}({member}),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD  SYSOUT=*",
    ]


def make_deck(profile: str, jobcard: list[str]) -> str:
    job, wfile, rfile, wentry, rentry, recfm, lrecl, block = PROFILES[profile]
    if not jobcard[0].startswith(f"//{job}"):
        raise ValueError("unexpected JOB card")
    cards = [*jobcard,
             f"//* Q.0 PROBE PROFILE {profile.upper()}; NO PDS WRITES",
             "//* PRIVATE TEMPORARY DASD; TWO SEPARATE LOAD MODULES",
             *asm_step("ASMWR", "WRROBJ", asm_source(wfile)),
             *asm_step("ASMRD", "RDROBJ", asm_source(rfile)),
             *link_step("LKWR", "WRROBJ", "WRMOD", "Q0WRMOD", wentry, "ASMWR"),
             *link_step("LKRD", "RDROBJ", "RDMOD", "Q0RDMOD", rentry, "ASMRD"),
             "//WGO      EXEC PGM=*.LKWR.SYSLMOD,TIME=(,1),",
             "//             COND=((0,NE,ASMWR),(0,NE,LKWR))",
             "//QDISK    DD  DSN=&&Q0DISK,DISP=(NEW,PASS),",
             "//             UNIT=SYSDA,SPACE=(TRK,(2,1)),",
             f"//             DCB=(RECFM={recfm},LRECL={lrecl},BLKSIZE={block})",
             "//SYSPRINT DD  SYSOUT=*",
             "//SYSUDUMP DD  SYSOUT=*",
             "//RGO      EXEC PGM=*.LKRD.SYSLMOD,TIME=(,1),",
             "//             COND=((0,NE,WGO),(0,NE,LKRD))",
             "//QDISK    DD  DSN=&&Q0DISK,DISP=(OLD,DELETE)",
             "//QOUT     DD  SYSOUT=*,",
             "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
             "//SYSPRINT DD  SYSOUT=*",
             "//SYSUDUMP DD  SYSOUT=*",
             "//"]
    for n, card in enumerate(cards, 1):
        if not card.isascii() or len(card)>71:
            raise ValueError(f"non-ASCII or >71-column JCL card {n}: {card!r}")
    if cards.count("//QDISK    DD  DSN=&&Q0DISK,DISP=(NEW,PASS),") != 1:
        raise ValueError("missing temp DASD allocation")
    if cards.count("//QDISK    DD  DSN=&&Q0DISK,DISP=(OLD,DELETE)") != 1:
        raise ValueError("missing temp DASD input")
    return "\n".join(cards) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("profile", choices=PROFILES)
    p.add_argument("--check", action="store_true", help="dry check; no JCL file written")
    args = p.parse_args()
    core = config_module()
    config = core.load_config()
    job = PROFILES[args.profile][0]
    jobcard = core.authenticated_job_card(config, job, "Q0 DASD QSAM", redact_password=False)
    deck = make_deck(args.profile, jobcard)
    if args.check:
        print(f"CHECK {args.profile.upper()}: JCL valid; no file written")
        return
    work = ROOT / "workarea/qsam-q0-dasd"
    work.mkdir(parents=True, exist_ok=True)
    path = work / f"q0-{args.profile}.jcl"
    path.write_text(deck, encoding="ascii", newline="\n")
    path.chmod(0o600)
    print(f"Q.0 {args.profile.upper()} JCL: {path}")


if __name__ == "__main__":
    main()
