#!/usr/bin/env python3
"""Prepare opt-in independent APTOVEC experiment from accepted regression source.

Run the ordinary native regression first to create native-test.asm.
Never alter canonical BCPLMAIN or the existing native-test.asm.
"""
import argparse
from pathlib import Path
import re
import subprocess

CASES = {
    91: "091-aptovec-nested-call",
    92: "092-large-aptovec",
    93: "093-aptovec-stack-overflow",
}

def replace_one(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"expected one {old!r}; found {source.count(old)}")
    return source.replace(old, new, 1)

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("test", type=int, choices=sorted(CASES))
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    work = root / "workarea/native-regression" / CASES[a.test]
    source = work / "native-test.asm"
    text = source.read_text(encoding="ascii")

    text = replace_one(text, "BCPLMAIN CSECT\n",
                       "BCPLMAIN CSECT\n"
                       "         ENTRY STKOVFL\n"
                       "         EXTRN APTOVEC,APLIMIT\n")
    text = replace_one(text, "         LA    1,APTOVEC\n"
                       "         ST    1,160(12)\n",
                       "         L     1,=A(APTOVEC)\n"
                       "         ST    1,160(12)\n"
                       "         L     1,=A(APLIMIT)\n"
                       "         L     2,STKLIM\n"
                       "         ST    2,0(1)\n")

    # Trim exactly the original APTOVEC routine and its nearby constant.
    start = text.index("* APTOVEC -- TEMPORARY STACK VECTOR")
    start = text.rfind("***********************************************************************", 0, start)
    end_marker = "APMAXN   DC    F'16380'"
    end = text.index(end_marker, start) + len(end_marker)
    region = text[start:end]
    if len(re.findall(r"(?m)^APTOVEC\s+", region)) != 1:
        raise ValueError("expected one APTOVEC routine to remove")
    if len(re.findall(r"(?m)^APMAXN\s+", region)) != 1:
        raise ValueError("expected one APMAXN constant to remove")
    text = text[:start] + "* APTOVEC now supplied by BCPLAPT object.\n" + text[end:]
    if re.search(r"(?m)^APTOVEC\s+", text):
        raise ValueError("internal APTOVEC definition survived")

    outdir = work / "aptovec-object-probe"
    outdir.mkdir(parents=True, exist_ok=True)
    modified = outdir / "native-external-aptovec.asm"
    modified.write_text(text, encoding="ascii", newline="\n")
    deck = outdir / "aptovec-object-probe.jcl"
    cmd = ["python3",
           str(root / "native-compiler/regression/make-two-object-job.py"),
           str(modified),
           str(root / "tools/checks/bcplapt-linkage-probe.asm"),
           str(deck), "--entry", f"BCRG{a.test:04d}",
           "--job-name", f"AP{a.test:03d}R"]
    subprocess.run(cmd, check=True)
    print(f"Prepared: {deck}")
    print("Two independently assembled CSECTs; G40 uses external APTOVEC.")
    print("BCPLMAIN exports STKOVFL and sets external APLIMIT.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"aptovec-object-probe: FAIL: {exc}")
