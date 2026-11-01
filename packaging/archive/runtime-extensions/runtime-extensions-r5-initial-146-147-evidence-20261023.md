# R.5 — Initial MVS regressions 146 and 147, 23 October 2026

**Tested Git revision:** `49320a61207dcd71186d5f564f4a8bd8a5b334c3`. **Disposition:** successful
compiler/IFOX/IEWL/GO execution; **automated R.5 gate FAIL** pending
corrected IEWL report verification.

| Regression | Compiler job | Native job | IFOX, IEWL, GO | Output |
| --- | --- | --- | --- | --- |
| 146 (empty) | 3723 | 3724 (RG146R) | All RC=0000 | `R5 EXT 146 PASS` |
| 147 (BCPLDEMO QUERY) | 3725 | 3726 (RG147R) | All RC=0000 | `R5 EXT 147 PASS` |

Both assembler listings reported zero flagged statements, severity 0.
The normal BCPL logical-record verifier matched one occurrence per
job, but **JES DD attribution was not verified**. The six original
host-side unit tests passed; synthetic JCL for all thirteen cases,
installed-mode synthetic JCL, Bash syntax and regression-numbering
checks passed.

The new R.5 MAP checker alone failed both cases with the message
`entry address was not zero`; final regression tally **0 PASS,
2 FAIL, 0 SKIP**. Its code incorrectly restricted the entry-address
search to the cross-reference table before `LOCATION REFERS TO
SYMBOL`. The entry field may appear elsewhere in the report.
The repair reads the full JES report, requires exactly one zero
entry address and does not alter the existing package/map checks.

The operator supplied only the overall regression console log,
not the full JOB 3724/3726 IEWL maps. The correction therefore
remains subject to rechecking the already saved reports; no claim
that the actual entry address was zero is yet made.

No production compiler, runtime, BCEX/BCRG ABI, or persistent
object PDS was modified. R.5 remains IN PROGRESS.
