#!/usr/bin/env python3
"""DR.5 read-only installed BCPLQSAM selection and absence verification."""
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
CASES = {
    True: ("DR5QSC", "DR5QS", ROOT / "tests/system-extensions/bcplqsam"
           / "163-qsam-query-capabilities", "BCPLQSAM Q4 QUERY CARRIAGE PASS"),
    False: ("DR5QNC", "DR5QN", ROOT / "tests/runtime-extensions"
            / "146-optional-empty", "R5 EXT 146 PASS"),
}
STEPS = [("ASMA", "IFOX00"), ("ASMG", "IFOX00"),
         ("LKED", "IEWL"), ("GO", None)]
QSAM_SECTIONS = ("QSMDESC", "QSMDISP", "QSMCORE", "QSMCLS1",
                 "QSMIO", "QSMFIN", "QSMCTRL", "QSMDCBS")
DSN = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+")
ENTRY = re.compile(r"(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+"
                   r"([0-9A-F]{1,8})[ \t]*$")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def make_deck(trail, generated, jobcard, obj, ext, mac, selected):
    for dsn in (obj, ext, mac):
        require(len(dsn) <= 44 and DSN.fullmatch(dsn), "invalid PDS DSN")
    require(len({obj, ext, mac}) == 3, "PDS aliases collide")
    require(jobcard[0].split()[:2] == ["//" + CASES[selected][1], "JOB"],
            "wrong authenticated job card")
    selection = "         BCXREQ BCPLQSAM" if selected else "* NO OPTIONAL EXTENSION"
    cards = [
        *jobcard,
        "//* DR.5 INSTALLED OBJECTS ONLY; NO PERMANENT WRITES",
        *trail["asm_step"]("ASMA", "APOBJ", trail["application_source"](generated)),
        "//ASMG     EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD',",
        "//             COND=(0,NE)",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DSN=&&REGDECK,UNIT=SYSDA,",
        "//             SPACE=(80,(100,20)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSGO    DD DUMMY",
        f"//SYSIN    DD DSN={mac}(BCXPRE),DISP=SHR",
        f"//         DD DSN={mac}(BCXCAT),DISP=SHR",
        "//         DD *",
        selection,
        "/*",
        f"//         DD DSN={mac}(BCXPOST),DISP=SHR",
        "//LKED     EXEC PGM=IEWL,REGION=256K,",
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE)",
        f"//OBJ      DD DSN={obj},DISP=SHR",
    ]
    if selected:
        cards.append(f"//EXTLIB   DD DSN={ext},DISP=SHR")
    cards += [
        "//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,PASS)",
        "//         DD DSN=&&REGDECK,DISP=(OLD,PASS)",
        "//         DD *",
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(BCPLRGS)",
        " INCLUDE OBJ(BCPLIO)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY R0APP",
        " NAME DR5QAPP(R)",
        "/*",
        "//SYSLMOD  DD DSN=&&LOADSET(DR5QAPP),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,",
        "//             TIME=(,2),COND=(0,NE,LKED)",
        "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,",
        "//             BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    require(all(x.isascii() and len(x) <= 71 and "\t" not in x for x in cards),
            "invalid JCL/IFOX card")
    require(cards.count("/*") == 3 and cards.count(" ENTRY R0APP") == 1,
            "unexpected source/control stream boundary")
    require(not any("CATLG" in x or "DISP=MOD" in x for x in cards),
            "permanent write forbidden")
    for line in cards:
        if line.startswith("//") and not line.startswith("//*") and "DSN=" in line:
            dsn = line.split("DSN=", 1)[1].split(",", 1)[0]
            require(dsn.startswith("&&") or line.endswith(",DISP=SHR"),
                    "non-temporary dataset not read-only")
    return "\n".join(cards) + "\n"


def verify(report, selected):
    require(report.count("CROSS REFERENCE TABLE") == 1, "expected one IEWL XREF")
    require(report.count("AUTHORIZATION CODE IS") >= 1, "missing linker boundary")
    before, go = report.rsplit("AUTHORIZATION CODE IS", 1)
    mapping = before.split("CROSS REFERENCE TABLE", 1)[1]
    require("LOCATION  REFERS TO SYMBOL" in mapping, "missing XREF boundary")
    mapping = mapping.split("LOCATION  REFERS TO SYMBOL", 1)[0]
    sections = {}
    for name, size in re.findall(
            r"(?m)^  ([A-Z0-9@$#]{1,8})\s+[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$",
            mapping):
        sections.setdefault(name, []).append(int(size, 16))
    for name in ("R0APP", "BCPLMAIN", "RGINIT", "RGFINI"):
        require(len(sections.get(name, [])) == 1, "missing/duplicate " + name)
    require(sections.get("BCPLREG") == [44 if selected else 28], "BCPLREG length")
    for name in QSAM_SECTIONS:
        require(len(sections.get(name, [])) == int(selected),
                "wrong QSAM CSECT presence: " + name)
    if selected:
        require(sections["QSMDESC"] == [56], "QSMDESC length")
        for symbol in ("QSMBEG", "QSMEND"):
            require(re.search(r"\b" + symbol + r"\b", mapping),
                    "missing extent symbol " + symbol)
    for name in ("DMODESC", "DMODISP", "TIMDESC", "TIMDISP"):
        require(name not in sections, "unexpected optional package " + name)
    require(bool(re.search(r"\bINCLUDE\s+EXTLIB\s*\(\s*BCPLQSAM\s*\)", before))
            == selected, "wrong IEWL QSAM INCLUDE evidence")
    entries = ENTRY.findall(before)
    require(len(entries) == 1 and int(entries[0], 16) == 0, "IEWL entry address")
    rows = [x.rstrip(" \r\t") for x in go.splitlines()]
    require(rows.count(CASES[selected][3]) == 1, "GO exact PASS record missing/duplicate")
    require(CASES[not selected][3] not in rows, "wrong GO record")


def check(trail):
    for selected, (_, name, case, marker) in CASES.items():
        require((case / "expected.txt").read_text("ascii").splitlines() == [marker],
                "fixture oracle changed")
        source = (case / "source.bcpl").read_text("ascii").splitlines()
        require(source and all(len(x) <= 80 and "\t" not in x for x in source),
                "invalid BCPL fixture")
        deck = make_deck(trail, trail["sample_generated"](),
                         [f"//{name} JOB (BCPL),'CHECK',CLASS=A"],
                         "DR5.BCPL.BOOT.OBJ", "DR5.BCPL.EXT.OBJ",
                         "DR5.BCPL.EXT.MAC", selected)
        require(deck.count(" EXEC PGM=IFOX00") == 2 and
                deck.count(" INCLUDE OBJ(BCPLRGS)") == 1 and
                deck.count(" INCLUDE OBJ(BCPLMAIN)") == 1, "wrong installed linkage")
        require(("//EXTLIB" in deck) == selected and
                ("BCXREQ BCPLQSAM" in deck) == selected, "wrong selection")
        names = {"R0APP": 100, "BCPLMAIN": 100, "RGINIT": 100, "RGFINI": 100,
                 "BCPLREG": 44 if selected else 28}
        if selected:
            names.update({x: 100 for x in QSAM_SECTIONS})
            names["QSMDESC"] = 56
        synthetic = (" INCLUDE EXTLIB(BCPLQSAM)\n" if selected else "")
        synthetic += "ENTRY ADDRESS 00000000\nCROSS REFERENCE TABLE\n"
        synthetic += "".join(f"  {x} 00000000 {n:08X}\n" for x, n in names.items())
        if selected:
            synthetic += "    QSMBEG 00000000\n    QSMEND 00000038\n"
        synthetic += "LOCATION  REFERS TO SYMBOL\nAUTHORIZATION CODE IS\n" + marker + "\n"
        verify(synthetic, selected)
        for bad in (synthetic.replace(marker, "FAIL"),
                    synthetic + marker + "\n",
                    synthetic.replace("ENTRY ADDRESS 00000000", "ENTRY ADDRESS 00000004"),
                    synthetic.replace(f"  BCPLREG 00000000 {names['BCPLREG']:08X}",
                                      "  BCPLREG 00000000 00000040"),
                    synthetic.replace("  RGINIT ", "  NOTREG ")):
            try:
                verify(bad, selected)
            except ValueError:
                pass
            else:
                raise ValueError("verifier accepted negative synthetic report")
    print("DR.5 installed QSAM CHECK PASS (synthetic JCL/XREF; no MVS)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = parser.parse_args()
    trail = runpy.run_path(str(ROOT / "bootstrap-toolchain/probes"
                               / "r0-export-trailer-probe/make-job.py"))
    check(trail)
    if args.check:
        return 0
    common = runpy.run_path(str(ROOT / "tools/checks/run-dr5-language-verification.py"))
    prior = runpy.run_path(str(ROOT / "tools/checks/run-dr5-bcplio-fix.py"))
    core = prior["CORE"]
    run, receipt = common["run"], common["receipt"]
    os.umask(0o077)
    parent = ROOT / "workarea/dr5-qsam-installed"
    parent.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    result = {"status": "FAIL", "stage": "preflight", "cases": []}
    env = dict(os.environ)
    for key in ("CAMBRIDGE_IMAGE", "BCPL_TAPE_OBJECT_PDS", "Q4_PUNCH_RESUME",
                "BCPL_RUNTIME_CANDIDATE_MEMBER", "R1_ACCEPTANCE"):
        env.pop(key, None)
    env.update(BCPL_RUNTIME_LIBRARY="OBJ", BCPL_RUNTIME_PDS="1",
               BCPL_RUNTIME_CANDIDATE="0", BCPL_PRINTER_WINDOW_TRIAL="0")
    try:
        result["git_head"] = run(["git", "rev-parse", "HEAD"],
                                 folder / "revision.log", env).strip()
        require(not run(["git", "status", "--porcelain", "--untracked-files=no"],
                        folder / "status.log", env).strip(), "tracked changes present")
        config = core["load_config"]()
        dsns = []
        for alias in ("BOOT_OBJ", "EXT_OBJ", "EXT_MAC"):
            spec = config["datasets"][alias]
            require(spec["dsorg"] == "PO" and spec["recfm"] == "FB"
                    and int(spec["lrecl"]) == 80, alias + " not FB80 PDS")
            if alias != "EXT_MAC":
                require(spec["content_type"] == "object", alias + " not object PDS")
            dsns.append(core["full_dsn"](config, spec))
        run(["tools/reconstruction/jes-idle", "--live"], folder / "idle.log", env)
        for selected, (cc, name, case, marker) in CASES.items():
            result["stage"] = "compile-" + name
            source = case / "source.bcpl"
            generated = folder / (name + ".asm")
            item = {"case": 163 if selected else 146,
                    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            result["cases"].append(item)
            output = run(["tools/bootstrap/compile-mvs", source,
                          "--job-name", cc, "--compiler-image", "CAMBCOMP",
                          "--cambridge-parm", ROOT / "bootstrap-toolchain/bootstrap-cambridge"
                          / "cambridge-options.txt", "--output", generated],
                         folder / (cc + "-compile.log"), env)
            item["compile_job"] = common["job_id"](output)
            report = receipt(folder, item["compile_job"], cc, common["CC_STEPS"], env)
            require(common["CODE"].findall(report) == ["0"], "compiler completion")
            item["generated_sha256"] = hashlib.sha256(generated.read_bytes()).hexdigest()
            result["stage"] = "native-" + name
            cards = make_deck(trail, generated.read_bytes().decode("latin-1"),
                              core["authenticated_job_card"](config, name, "DR5 QSAM", False),
                              *dsns, selected)
            deck = folder / (name + ".jcl")
            deck.write_text(cards, encoding="ascii")
            item["native_job"], report = prior["submit"](folder, name, deck, STEPS, env)
            require(not common["CODE"].findall(report), "unexpected interpreted GO")
            summary = (folder / (name + "-summary.log")).read_text("utf-8")
            for field in ("Statements flagged", "Highest severity"):
                values = re.findall(rf"{field}:\s*(\d+)", summary)
                require(values and all(int(v) == 0 for v in values), field + " not zero")
            verify(report, selected)
            item["status"] = "PASS"
            print(f"{name} JOB {item['native_job']} PASS: {marker}", flush=True)
        result.update(status="PASS", stage="complete")
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result["reason"] = str(exc)
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("DR.5 evidence: " + str(folder.relative_to(ROOT)))
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        print("STOP: retain evidence; do not retry automatically.")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
