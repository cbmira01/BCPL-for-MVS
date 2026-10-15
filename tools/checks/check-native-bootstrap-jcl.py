#!/usr/bin/env python3
"""Static contract for authoritative M3 NATIVE_JCL(CAMBBLD) source."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
deck = (ROOT / "native-compiler/jcl/build-cambridge-resident.jcl").read_text(encoding="ascii")
assert "HERC02.BCPL.CAMBRIDG." not in deck
for old in ("HERC02.BCPL.SOURCE(", "HERC02.BCPL.INTCODE(", "HERC02.BCPL.LOAD,"):
    assert old not in deck, old
assert not re.search(r"^//(?:ASM|LKED)\s+EXEC", deck, re.M)
assert len(re.findall(r"^//C\d{2}(?:CMP|CG)\s+EXEC PGM=ICINT19", deck, re.M)) == 22
assert re.search(r"^//PACKCOMP\s+EXEC PGM=IEBGENER", deck, re.M)
assert "HERC02.BCPL.MR10KIT.LOAD,DISP=SHR" in deck
for member in ("SYNI", "CGI", "BLIBI", "ICLIB"):
    assert f"HERC02.BCPL.MR10KIT.SOURCE({member})" in deck
for member in ("TRNILRG", "CAMBCOMP"):
    assert f"HERC02.BCPL.NATIVE.INTCODE({member})" in deck
for member in ("BCPL", "SYN", "LEX", "TRNA", "TRNB", "CGA", "CGB", "CGC", "CGD", "CGE", "BOOTHOST"):
    assert f"HERC02.BCPL.NATIVE.SOURCE({member})" in deck
print("PASS: authoritative M3 CAMBBLD JCL stays within MR10_* and NATIVE_* PDSes")
