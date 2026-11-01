# Milestone QSAM — Q.4 FBA133 printer evidence (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** **Q.4 — SYSOUT devices**
**Disposition:** **STANDALONE FBA DEMONSTRATION PASSED; NUMBERED Q.4 REGRESSIONS AND CLOSURE PENDING.**

## Native execution and authority

- GitHub source baseline: `main` [`30b6c32cae58b44c857db46f0e321d3c092a89cc`](https://github.com/cbmira01/BCPL-for-MVS/commit/30b6c32cae58b44c857db46f0e321d3c092a89cc).
- The owner executed the test on resident Hercules/TK5 MVS 3.8J and supplied terminal results and JES report excerpts. Full local logs remain under `workarea/bcplqsam-q4/` and are not tracked in Git.
- Compiler JOB **7727** ran the **resident demoted Cambridge compiler** and saved the generated System/370 assembler as `q4fba-generated.asm`; compiler RC=0.
- Seven offline generator tests passed, RC=0; authenticated JCL preparation produced **3,434 cards**, SHA-256 `228a02c9fde6d0f351e5a75ed9eb131ab897ef82e071b4aa4255567a3e46b79b`.
- Native **JOB 7728 — Q4FBA**, 30 OCT 26 18:20:00–18:20:01 by resident JES clock, `JOB RESULT: SUCCESS`, highest `RC=0000`, summary and full report extraction RC=0.

| Native step | Program | Result |
| --- | --- | --- |
| ASMA, ASMV, ASMN, ASMR, ASMQ, ASMG | IFOX00 | All RC=0000 |
| LKVR, LKED | IEWL | Both RC=0000 |
| WGO | Native BCPL source-mode QSAM writer | RC=0000 |
| VGO | Independent IFOX FBA133 binary verifier | RC=0000 |

IFOX summary: **0 statements flagged**, highest severity **0**.
The owner-provided report contained exactly the required application markers:

```text
BCPLQSAM Q4 FBA133 DUAL WRITE PASS
BCPLQSAM Q4 FBA133 TEMP EXACT 3 PASS
```

## Record and printer evidence

The BCPL application opened `Q4TEMP` and `Q4PRINT` independently at G!200, checked INFO enum **5** and effective **LRECL 133**, and wrote three complete FBA133 logical records to both DDs. The IFOX verifier checked the temporary FBA133 dataset's DCB geometry, all **133 EBCDIC bytes**, final data-column marks and exact EOF. Its RC=0000 supplies independent full-record byte evidence.

- Record 1: ASA EBCDIC blank (`X'40'`), `Q4FBA001` data.
- Record 2: ASA EBCDIC `0` (`X'F0'`), `Q4FBA002`, final data byte `X`.
- Record 3: ASA EBCDIC `1` (`X'F1'`), `Q4FBA003`, final data byte `Y`.
- Interior and trailing payload blanks are EBCDIC `X'40'`.

JCL used `Q4PRINT DD SYSOUT=A,DCB=(RECFM=FBA,LRECL=133,BLKSIZE=133)`, **not** Core Runtime BCPLIO's `SYSPRINT`, and a `&&Q4FBA` temporary dataset passed to independent IFOX. The Hercules printer-capture check printed:

```text
New printer bytes: 571573
Form feeds: 159
Printer record context: ...Q4FBA001\n\nQ4FBA002...
Printer record context: ...X\x0cQ4FBA003...
Printer inspection RC=0
```

The captured contexts show the expected single spacing, double spacing and form feed before the third printer record. The **571,573-byte delta and 159 form feeds include other JOB 7728 class-A printer output**; they cannot all be attributed to the three application records. The ASCII printer capture is evidence of JES2/Hercules presentation, not a second independent source of the complete 133-byte EBCDIC record images.

No Hercules changes, installed System Extension object promotion, or permanent MVS dataset modifications were part of these jobs.

## Q.4 closeout still pending

The standalone FB80 punch result is separately documented in
[Q.4 punch evidence](qsam-q4-punch-evidence-20261030.md) for
JOBs 7725/7726, including its 172-byte class-B output and blank separator.

The numbered **175 punch**, **176 FBA**, and **163/170 updated QUERY carriage capability** regressions remain unexecuted as of this record. The target focused **163–176** and full production **00–176** panels need fresh native MVS results before formal Q.4 closure. This record does not claim a regression pass or owner closeout decision.
