# DR.5 — Focused native Base Library numeric input verification

**Status:** Focused native verification PASS (owner-reported JOBs 1301/1302). Source review
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

## Native execution — PASS

Owner-reported checkout `7bc3196009c8036f4466c325afa06e8aace4c259`, private evidence
`workarea/dr5-readn-verification/run-vk9rmndr`. Compiler JOB 1301 and native
JOB 1302 passed the driver's COMP/SVCODE, interpreted CODE=0, ASMAP/LKED/GO
and exact ordered record gates. All twelve observed records match the
tracked independent oracle. Reported SHA-256 identities:

| Input | SHA-256 |
| --- | --- |
| source.bcpl | `0d79cdfed7e9ee3891948af84c5ca3d259a62bb5c03a9fa11a2d481733578fe2` |
| expected.txt | `854b610d9aa306b1b882cb6a08e82dd4dfb9c5177fefc165780843f940610aea` |
| input.records | `c696816a2352afa0cef89525a0d12cd1e98ff6fa92c3d2f67cd0187d143c8e23` |

Accepted scope: resident BLIB READN and TERMINATOR for these four input
records, including signed numbers, zero, leading blanks, consumed punctuation,
nondigits, logical newline, signs without digits, and repeated EOF. No
production correction required. Tab input, overflow, complete installed
export-trailer identity and other untested boundaries remain qualified.
The owner-supplied JSON was compared with the tracked oracle; private JES
receipts and installed bytes were not independently inspected. This is one
focused candidate, not a new numbered regression, and adds nothing to the
219 supported-pass count. No normative transfer or march closure.
