# DR.5 — Focused native Base Library numeric input verification

**Status:** Candidate prepared; native verification pending. Source review
checkpoint `bcfa2c51cb4beaa024c2ded53762969f6a67b588`. No numbered regression allocation.

The [runtime/library reference](../../../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md)
chapter 5 describes historical BLIB READN (G!70) and TERMINATOR (G!71).
Current source review confirms the input algorithm, but existing compiler-host
option probes exercise a different interpreted reader. The installed BLIB
object's numeric-input behavior requires independent native evidence.

The [BCPL source](source.bcpl) reads the four [BCPIN records](input.records)
and asserts 12 value/terminator pairs against BCPL literals, reporting each
observed pair for comparison with the independent [numeric oracle](expected.txt).
Coverage: leading blanks and synthesized logical newline, both signs, actual
zero, nondigit and consumed punctuation, sign without digits, a blank after
a sign, successive records and repeated EOF. The oracle uses EBCDIC byte
values for ordinary characters and the corrected logical newline value 10.
No tab-input, overflow, malformed pointer, or complete BLIB export-trailer
claim is made. G!71 is read only after READN; no pre-call initialization
guarantee is implied.

The [driver](../../../../../tools/checks/run-dr5-readn-verification.py)
compiles the application using resident CAMBCOMP, then uses the existing
installed-object native deck generator with a private BCPIN fixture.
DR5READN and RG905R are temporary JES job names; 905 is solely a helper
naming parameter, not a numbered regression. Require compiler COMP/SVCODE
RC0 and CODE=0, native ASMAP/LKED/GO RC0, and all twelve exact ordered
records. Installed BOOT_OBJ is read-only, and no device output beyond
ordinary SYSPRINT, PDS replacement, release action or automatic retry occurs.
Private evidence stays under workarea/dr5-readn-verification/.

Host precommit validation: Python syntax/import and mocked compile/deck/submit
routing passed; independently simulated the historical READN algorithm over
the four EBCDIC records with BCPLIO's synthesized logical newlines and
verified all 12 expected pairs. Source cards checked for ASCII and width.
The assistant's local checkout remains unavailable (GitHub DNS); the full
repository helper integration and actual BCPL/IFOX/IEWL/GO were not run.
The four code/fixture blobs must match the locally checked copies before
commit. No production code, oracle of any existing case, or normative
authority is changed.
