#!/usr/bin/env python3
"""Generate an MR10 TRN source derivative with a larger declaration-name vector.

The Cambridge CGA bootstrap probe (JOB 899) reached MR10 translation but hit
TRN report 143, "TOO MANY NAMES DECLARED".  The historical MR10 translator
allocates DVEC as VEC 1200 and stores each declaration as three words
(name, class, value), allowing roughly 400 simultaneously visible entries.

This generator leaves the historical mr10/bcplkit/trn file untouched.  It
splits its TRNHDR/TRN0... container into separately compilable source units and
changes only TRN0's declaration-vector capacity from 1200 to 2400 words.
Translation semantics are otherwise unchanged.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "richards-bcpltape" / "mr10" / "bcplkit" / "trn"
OUTDIR = ROOT / "workarea" / "bootstrap-cambridge" / "mr10-trn-large-names"

OLD_VEC = "LET A = VEC 1200"
NEW_VEC = "LET A = VEC 2400"
OLD_TOP = "DVEC, DVECS, DVECE, DVECP, DVECT := A, 3, 3, 3, 1200"
NEW_TOP = "DVEC, DVECS, DVECE, DVECP, DVECT := A, 3, 3, 3, 2400"


def split_sections(text: str) -> list[str]:
    sections: list[list[str]] = [[]]
    for line in text.splitlines(keepends=True):
        if line.strip() == ".":
            sections.append([])
        else:
            sections[-1].append(line)
    result = ["".join(lines).strip("\n") + "\n" for lines in sections if "".join(lines).strip()]
    if len(result) < 2:
        raise SystemExit("historical TRN container did not split into header + sections")
    return result


def section_name(text: str, index: int) -> str:
    if index == 0:
        if "TRNHDR" not in text:
            raise SystemExit("first historical TRN section is not TRNHDR")
        return "trnhdr"
    match = re.search(r"^//\s+TRN([0-9]+)\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit(f"historical TRN section {index} has no TRNn banner")
    return f"trn{match.group(1)}"


def main() -> None:
    source = SOURCE.read_text(encoding="ascii")
    sections = split_sections(source)
    names = [section_name(section, index) for index, section in enumerate(sections)]
    if len(names) != len(set(names)):
        raise SystemExit("duplicate generated TRN section names")
    if "trn0" not in names:
        raise SystemExit("historical TRN container has no TRN0 section")

    trn0_index = names.index("trn0")
    trn0 = sections[trn0_index]
    if trn0.count(OLD_VEC) != 1:
        raise SystemExit(f"TRN0: expected exactly one {OLD_VEC!r}")
    if trn0.count(OLD_TOP) != 1:
        raise SystemExit(f"TRN0: expected exactly one DVECT=1200 initialization")
    trn0 = trn0.replace(OLD_VEC, NEW_VEC, 1).replace(OLD_TOP, NEW_TOP, 1)
    banner = (
        "// BOOTSTRAP DERIVATIVE: MR10 TRN DECLARATION VECTOR 1200 -> 2400 WORDS\n"
        "// JOB 899 REQUIRED MORE THAN THE HISTORICAL ~400 ACTIVE NAME ENTRIES.\n"
        "// HISTORICAL SOURCE: richards-bcpltape/mr10/bcplkit/trn\n\n"
    )
    sections[trn0_index] = banner + trn0

    OUTDIR.mkdir(parents=True, exist_ok=True)
    expected = set(names)
    for old in OUTDIR.iterdir() if OUTDIR.exists() else []:
        if old.is_file() and old.name.startswith("trn") and old.name not in expected:
            old.unlink()

    for name, section in zip(names, sections):
        (OUTDIR / name).write_text(section, encoding="ascii", newline="\n")

    print("generated MR10 translator bootstrap sources:")
    for name in names:
        path = OUTDIR / name
        suffix = "  (DVEC 2400)" if name == "trn0" else ""
        print(f"  {path.relative_to(ROOT)}  {path.stat().st_size} bytes{suffix}")


if __name__ == "__main__":
    main()
