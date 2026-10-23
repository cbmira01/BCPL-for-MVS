#!/usr/bin/env python3
"""Generate native regressions with accepted and development runtime PDS objects.

Non-submitting. Does not assemble or overwrite BCPLMAIN or service modules.
Only the simple single-BCPL-source strategy is supported by this first gate.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--test-number", type=int, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--test-io-asm", type=Path)
    parser.add_argument("--library-generated", type=Path)
    parser.add_argument("--case-dir", type=Path)
    args = parser.parse_args()
    args.output.unlink(missing_ok=True)
    n = args.test_number
    if not 0 <= n <= 999:
        raise ValueError("invalid regression number")
    original = args.generated.read_bytes().decode("latin-1")
    original = "".join(c if ord(c) < 128 else "?" for c in original)
    lines = original.splitlines()
    if args.native and args.library_generated:
        raise ValueError("native and separately compiled BCPL library conflict")
    if args.native or args.library_generated:
        # Transform only the application.  The historical combiners append
        # WIP runtime text for source-mode jobs; installed-object linkage
        # must not read or manufacture that runtime text at all.
        if args.native:
            helper = load(
                ROOT / "bootstrap-toolchain/regression/prepare-native-global.py",
                "runtime_pds_native_global")
            csect = helper.one_index(lines, helper.CSECT, "generated CSECT")
            extrn = helper.one_index(
                lines, helper.EXTRN_MAIN, "EXTRN BCPLMAIN")
            end_stmt = helper.one_index(
                lines, helper.END_STMT, "generated END statement")
            lines[csect] = f"BCRG{n:04d} CSECT"
            lines.insert(csect + 1, "         EXTRN NATIVEAD")
            for index in sorted((extrn + 1, end_stmt + 1), reverse=True):
                del lines[index]
            start, maximum, pairs = helper.find_trailer(lines)
            offset = 151 * 4
            if any(slot == offset for slot, _ in pairs):
                raise ValueError("generated module already exports G!151")
            last = helper.one_index(lines, helper.L998, "L998")
            values = [
                f"         DC F'{max(maximum, offset)}'",
                "         DC F'0'",
            ]
            for slot, address in pairs:
                values.extend((f"         DC F'{slot}'",
                               f"         DC A({address})"))
            values.extend((f"         DC F'{offset}'",
                           "         DC A(NATIVEAD)"))
            lines[start:last] = values
        else:
            helper = load(
                ROOT / "bootstrap-toolchain/regression/combine-separate-bcpl.py",
                "runtime_pds_separate_bcpl")
            app = helper.prepare_main(lines, f"BCRG{n:04d}")
            library = helper.read_generated(args.library_generated)
            lines = helper.merge_units(app, library)

        if any(re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", row)
               for row in lines):
            raise ValueError("unexpected BCPLMAIN external declaration")
        section = [i for i, row in enumerate(lines)
                   if row == f"BCRG{n:04d} CSECT"]
        if len(section) != 1:
            raise ValueError("invalid transformed application CSECT")
        lines.insert(section[0] + 1, "         EXTRN BCPLMAIN")
        lines.append(f"         END   BCRG{n:04d}")
        original = "\n".join(lines) + "\n"
    csects = [i for i, row in enumerate(lines)
              if re.fullmatch(r"\s*CSECT\s*", row)]
    externs = [row for row in lines
               if re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", row)]
    ends = [i for i, row in enumerate(lines)
            if re.fullmatch(r"\s*END(?:\s+.*)?", row)]
    if (len(csects) != (0 if (args.native or args.library_generated) else 1)
            or len(externs) != 1 or len(ends) != 1):
        raise ValueError("application requires one CSECT, EXTRN BCPLMAIN, END")
    entry = f"BCRG{n:04d}"
    if csects:
        lines[csects[0]] = f"{entry} CSECT"
    # Match the proven BLIB consumer's handling of malformed signed-minimum
    # constants emitted by this historical CG370 printer transport.
    bad = [i for i, row in enumerate(lines)
           if row.strip() == "DC F'-./,),(-*,('"]
    if len(bad) > 1:
        raise ValueError("multiple malformed minimum-integer constants")
    for index in bad:
        lines[index] = "         DC X'80000000'"
    if any(len(row) > 71 or row == "/*" or row.startswith("//")
           for row in lines):
        raise ValueError("invalid application assembler card")
    core = load(ROOT / "tools/datasets/dspal-core.py", "runtime_pds_dspal")
    config = core.load_config()
    import os
    candidate = os.environ.get("BCPL_RUNTIME_CANDIDATE", "0")
    if candidate not in ("0", "1"):
        raise ValueError("BCPL_RUNTIME_CANDIDATE must be 0 or 1")
    library = os.environ.get("BCPL_RUNTIME_LIBRARY", "MIXED").upper()
    candidate_member = os.environ.get("BCPL_RUNTIME_CANDIDATE_MEMBER", "BCPLM3").upper()
    if candidate_member not in ("BCPLM3", "BCPLM4", "BCPLM5", "BCPLM6", "BCPLM7"):
        raise ValueError("invalid BCPLMAIN candidate member")
    if candidate != "1" and "BCPL_RUNTIME_CANDIDATE_MEMBER" in os.environ:
        raise ValueError("candidate member selection requires candidate mode")
    if candidate == "1" and library != "DEVOBJ":
        raise ValueError("candidate BCPLMAIN requires BCPL_RUNTIME_LIBRARY=DEVOBJ")
    if library not in ("MIXED", "OBJ", "DEVOBJ"):
        raise ValueError("BCPL_RUNTIME_LIBRARY must be MIXED, OBJ or DEVOBJ")
    if args.test_io_asm:
        if not (candidate == "1" and library == "DEVOBJ"
                or candidate == "0" and library == "OBJ"):
            raise ValueError("test-only BCPLIO needs accepted DEVOBJ or OBJ profile")
        if args.library_generated or (
            args.native and not (
                args.case_dir and
                (args.case_dir / "io-accounting.txt").is_file()
            )
        ):
            raise ValueError(
                "only M4.3 may combine native and private BCPLIO"
            )
        if not args.case_dir:
            raise ValueError("test-only BCPLIO requires regression case")
        markers = (
            (args.case_dir / "io-fault-mode.txt").is_file(),
            (args.case_dir / "io-open-fault.txt").is_file(),
            (args.case_dir / "io-accounting.txt").is_file(),
        )
        if sum(markers) != 1:
            raise ValueError("test-only BCPLIO requires exactly one marker")

    # OBJ is the explicit clean-room production profile: all six runtime
    # objects (five assembler CSECTs plus BLIB) reside in BOOT_OBJ.
    # MIXED and DEVOBJ remain for historical regression reproducibility.
    # Generating JCL cannot promote or modify an object library.
    chosen = ("BOOT_DEVOBJ" if library == "DEVOBJ" else "BOOT_OBJ")
    devchosen = ("BOOT_OBJ" if library == "OBJ" else "BOOT_DEVOBJ")
    def object_dsn(logical):
        spec = config["datasets"][logical]
        if (spec.get("content_type") != "object" or spec.get("recfm") != "FB"
                or int(spec.get("lrecl", 0)) != 80 or spec.get("dsorg") != "PO"):
            raise ValueError(f"{logical} must be a binary FB80 object PDS")
        return core.full_dsn(config, spec)
    main_dsn = object_dsn(chosen)
    service_dsn = object_dsn("BOOT_DEVOBJ" if candidate == "1"
                             else devchosen)
    core_dsn = object_dsn("BOOT_OBJ")
    job = f"RG{n:03d}R"
    cards = [
        *core.authenticated_job_card(config, job, "BCPL PDS REG",
                                    redact_password=False),
        f"//* RUNTIME LIBRARY: {library}; APP ASSEMBLY ONLY",
        f"//* EXPLICIT BCPLMAIN CANDIDATE: {candidate}",
        "//ASMAP    EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        "//SYSGO    DD DSN=&&APOBJ,UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD *", *lines, "/*",
        "//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
        "//             COND=(0,NE,ASMAP)",
        f"//OBJ      DD DSN={main_dsn},DISP=SHR",
        *([f"//DEVOBJ   DD DSN={service_dsn},DISP=SHR"]
          if library != "OBJ" else []),
        *([f"//COREOBJ  DD DSN={core_dsn},DISP=SHR"] if candidate == "1" else []),
        "//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        f" INCLUDE OBJ({candidate_member})" if candidate == "1" else " INCLUDE OBJ(BCPLMAIN)",
        *([" INCLUDE OBJ(BCPLIO)"]
          if (candidate == "1" or library == "OBJ")
          and not args.test_io_asm else []),
        " INCLUDE OBJ(BCPLBYTE)" if library == "OBJ"
            else " INCLUDE DEVOBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)" if library == "OBJ"
            else " INCLUDE DEVOBJ(BCPLAPT)",
        " INCLUDE COREOBJ(BCPLMEM)" if candidate == "1" else " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE COREOBJ(BLIB)" if candidate == "1" else " INCLUDE OBJ(BLIB)",
        # Production applications link the installed generic registrar
        # and exactly one default empty table; the historical R.1
        # temporary overlay supplies its own copies instead.
        *([" INCLUDE OBJ(BCPLRGS)", " INCLUDE OBJ(BCPLREG)"]
          if library == "OBJ" and os.environ.get("R1_ACCEPTANCE") != "1"
          else []),
        f" ENTRY {entry}",
        f" NAME RG{n:03d}OBJ(R)",
        "/*",
        f"//SYSLMOD  DD DSN=&&GOSET(RG{n:03d}OBJ),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASMAP),(0,NE,LKED))",
        "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    if args.test_io_asm:
        io = args.test_io_asm.read_text(encoding="ascii")
        if not io or any(
            len(row) > 71 or row.startswith("//") or row == "/*"
            for row in io.splitlines()
        ):
            raise ValueError("invalid test-only BCPLIO assembler cards")
        insertion = [
            "//* M4.1 TEST-ONLY BCPLIO FROM INLINE ASSEMBLER",
            "//ASMFIO   EXEC PGM=IFOX00,REGION=512K,COND=(0,NE,ASMAP),",
            "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
            "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
            "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSPUNCH DD DUMMY",
            "//SYSGO    DD DSN=&&IOOBJ,UNIT=SYSDA,",
            "//             SPACE=(80,(500,200)),DISP=(NEW,PASS),",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSIN    DD *", *io.rstrip("\n").splitlines(), "/*",
        ]
        at = cards.index("//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',")
        cards[at:at] = insertion
        link_cond = cards.index("//             COND=(0,NE,ASMAP)", at + len(insertion))
        cards[link_cond] = "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO))"
        syspass = cards.index("//         DD *", link_cond)
        cards.insert(syspass, "//         DD DSN=&&IOOBJ,DISP=(OLD,DELETE)")
        go_cond = cards.index(
            "//             COND=((0,NE,ASMAP),(0,NE,LKED))"
        )
        cards[go_cond] = (
            "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO),(0,NE,LKED))"
        )
    if args.native:
        source = args.native.read_text(encoding="ascii")
        if any(len(row) > 71 or row.startswith("//") or row == "/*"
               for row in source.splitlines()):
            raise ValueError("invalid native external module cards")
        insertion = [
            "//ASMNAT   EXEC PGM=IFOX00,REGION=256K,COND=(0,NE,ASMAP),",
            "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
            "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
            "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
            "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
            "//SYSPRINT DD SYSOUT=*",
            "//SYSPUNCH DD DUMMY",
            "//SYSGO    DD DSN=&&NATOBJ,UNIT=SYSDA,",
            "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSIN    DD *", *source.rstrip("\n").splitlines(), "/*",
        ]
        at = cards.index("//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',")
        cards[at:at] = insertion
        old_cond = (
            "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO))"
            if args.test_io_asm else
            "//             COND=(0,NE,ASMAP)"
        )
        link_cond = cards.index(old_cond, at + len(insertion))
        cards[link_cond] = (
            "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO),(0,NE,ASMNAT))"
            if args.test_io_asm else
            "//             COND=((0,NE,ASMAP),(0,NE,ASMNAT))"
        )
        syspass = cards.index("//         DD *", link_cond)
        cards.insert(syspass, "//         DD DSN=&&NATOBJ,DISP=(OLD,DELETE)")
        old_go_cond = (
            "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO),(0,NE,LKED))"
            if args.test_io_asm else
            "//             COND=((0,NE,ASMAP),(0,NE,LKED))"
        )
        go_cond = cards.index(old_go_cond)
        if args.test_io_asm:
            cards[go_cond:go_cond + 1] = [
                "//             COND=((0,NE,ASMAP),(0,NE,ASMFIO),",
                "//             (0,NE,ASMNAT),(0,NE,LKED))",
            ]
        else:
            cards[go_cond] = (
                "//             COND=((0,NE,ASMAP),(0,NE,ASMNAT),(0,NE,LKED))"
            )
    if args.case_dir:
        case = args.case_dir
        parm_fixture = case / "exec-parm.txt"
        if parm_fixture.is_file():
            value = parm_fixture.read_text(encoding="ascii").rstrip("\r\n")
            if not value or len(value) > 100 or not value.isascii() or any(
                ch in value for ch in ("'", "\n", "\r")
            ):
                raise ValueError(f"invalid EXEC PARM fixture {parm_fixture}")
            go = cards.index("//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),")
            cards.insert(go + 1, f"//             PARM='{value}',")
        anchor = cards.index("//SYSUDUMP DD SYSOUT=*")
        for name, dd, dlm in (("input.records", "BCPIN", "ZZ"),
                              ("input-b.records", "BCPINB", "ZY")):
            path = case / name
            if path.is_file():
                rows = path.read_text(encoding="ascii").splitlines()
                if not rows or any(len(row) > 80 or row.startswith("//")
                    or row.startswith("/*") or row.startswith(dlm)
                    for row in rows):
                    raise ValueError(f"unsafe fixture {path}")
                cards[anchor:anchor] = [
                    f"//{dd:<8} DD DATA,DLM={dlm}", *rows, dlm,
                ]
                anchor += len(rows) + 2
        # Generic input DD DATA fixtures for the dynamic-FINDINPUT marches.
        # Keep this independent of legacy BCPIN and BCPINB fixture names.
        sources = sorted(case.glob("input-dd*.records"))
        if len(sources) > 36:
            raise ValueError("too many dynamic input DD fixtures")
        for index, source in enumerate(sources):
            dd = source.stem[len("input-"):].upper()
            if not re.fullmatch(r"DD[A-Z0-9@$#]{1,6}", dd):
                raise ValueError(f"invalid dynamic DD fixture: {source}")
            delim = "X" + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index]
            rows = source.read_text(encoding="ascii").splitlines()
            if not rows or any(
                len(row) > 80 or row.startswith(("//", "/*"))
                or row == delim for row in rows
            ):
                raise ValueError(f"unsafe dynamic input fixture: {source}")
            cards[anchor:anchor] = [
                f"//{dd:<8} DD DATA,DLM={delim}", *rows, delim,
            ]
            anchor += len(rows) + 2
        if (case / "expected-alt.txt").is_file():
            cards.insert(anchor,
                "//BCPALT   DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)")
            anchor += 1
        # Candidate-only BCPL dynamic stream regression destinations.
        for dd in ("REPORT", "REPORT2"):
            if (case / f"expected-{dd.lower()}.txt").is_file():
                cards.insert(anchor, (
                    f"//{dd:<8} DD SYSOUT=*,"
                    "DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)"
                ))
                anchor += 1
        if n == 3:
            cards[cards.index("//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),")] = (
                "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,3),"
            )
    for index, card in enumerate(cards, 1):
        if len(card) > 71 or not card.isascii():
            raise ValueError(f"invalid JCL card {index}: {card!r}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(cards) + "\n", encoding="ascii", newline="\n")
    print(f"Prepared {library} runtime PDS regression: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"runtime-pds-regression: {exc}")
