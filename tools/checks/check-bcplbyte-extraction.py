#!/usr/bin/env python3
"""Check the first independent BCPLBYTE extraction against current BCPLMAIN."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
old = (root / "asm/bcplmain-wip.asm").read_text(encoding="ascii")
new = (root / "asm/bcplbyte.asm").read_text(encoding="ascii")

def instructions(text, begin, stop):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if re.match(r"^" + begin + r"\s+", line))
    end = next(i for i in range(start+1, len(lines))
               if re.match(r"^" + stop + r"\s+", lines[i]))
    return [re.sub(r"\s+", " ", line.strip())
            for line in lines[start:end]
            if line.strip() and not line.startswith("*")]

old_get = instructions(old, "GETBYTE", "PUTBYTE")
old_put = instructions(old, "PUTBYTE", "GETVEC")
new_get = instructions(new, "GETBYTE", "PUTBYTE")
new_put = instructions(new, "PUTBYTE", "END")
assert old_get == new_get, f"GETBYTE extraction changed: {old_get!r} != {new_get!r}"
assert old_put == new_put, f"PUTBYTE extraction changed: {old_put!r} != {new_put!r}"
assert re.search(r"^BCPLBYTE\s+CSECT\s*$", new, re.M)
assert re.search(r"^\s+ENTRY\s+GETBYTE,PUTBYTE\s*$", new, re.M)
assert re.search(r"^\s+END\s+BCPLBYTE\s*$", new, re.M)
print(f"PASS BCPLBYTE extraction: {len(new_get)+len(new_put)} unchanged machine instructions")
print("NOTE: assembler/link-edit integration not yet established")
