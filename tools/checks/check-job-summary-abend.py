#!/usr/bin/env python3
"""Regression for false ABEND detection in copied BCPL source SYSOUT."""
from importlib.machinery import SourceFileLoader
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "job-summary"
# Use the parser's diagnostic regex directly; no live MVS environment.
import re
source = script.read_text(encoding="utf-8")
start = source.index("ABEND_RE = re.compile(")
end = source.index("\n\nJCL_ERROR_RE", start)
namespace = {"re": re}
exec(source[start:end], namespace)
pattern = namespace["ABEND_RE"]
for payload in (
    'WRITEF("*N*NSTEP ABEND USER CODE %N*N", CODE)',
    'WRITEF("%N*NSTEP ABEND SYSTEM CODE %X3*N", CODE)',
    '// NO ABEND OCCURRED IN THIS SOURCE COMMENT',
):
    assert not pattern.search(payload), payload
for diagnostic in (
    'IEF450I DSPALGET COPY - ABEND=S0C4 U0000 REASON=00000000',
    'IEF472I DSPALGET COPY - COMPLETION CODE - SYSTEM=0C4 USER=0000',
):
    assert pattern.search(diagnostic), diagnostic
print("PASS: source payload is not an ABEND; MVS ABEND diagnostics are")
