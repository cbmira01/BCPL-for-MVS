# Milestone QSAM — Q.4 SYSOUT punch evidence (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.4 — SYSOUT devices**  
**Scope:** Native BCPLQSAM FB80 output through a temporary QSAM dataset and JES2 `SYSOUT=B`.  
**Disposition:** **PUNCH DEMONSTRATION PASSED; Q.4 REMAINS OPEN.** The FBA SYSPRINT demonstration and complete Q.4 acceptance remain pending.

## Authority and test identity

- Source baseline: GitHub `main` commit [`554af921beee3f65fbba9f4ce4a305323adcdeb1`](https://github.com/cbmira01/BCPL-for-MVS/commit/554af921beee3f65fbba9f4ce4a305323adcdeb1).
- Source-controlled BCPL writer: `bootstrap-toolchain/extensions/bcplqsam/test-q4-punch.bcpl`.
- Independent IFOX readback: `bootstrap-toolchain/extensions/bcplqsam/q4-punch-verify.asm`.
- JCL generator: `bootstrap-toolchain/extensions/bcplqsam/prepare-q4-punch.py`.
- Runtime: resident Hercules/TK5 MVS 3.8J; optional BCPLQSAM source-mode BCEX/BCRG registration; accepted `BOOT_OBJ` components read-only.
- Resident demoted Cambridge compiler generated the application's System/370 assembler. This is **not** a claim that the future native/self-hosted Cambridge compiler compiled the source.
- The owner executed the jobs and supplied terminal results, job summary, diagnostic excerpts, and host-side punch comparison. The complete private JES listings were not independently supplied for archival review.

## Native compiler and preparation

The owner ran the guarded compiler/preparation procedure. Observed output:

| Activity | Observation |
| --- | --- |
| Synthetic Q4PUNCH JCL | PASS, 2,986 cards, RC=0; no JES work |
| Compiler | **JOB 7725**, `Q4PCOMP`; `tools/bootstrap/compile-mvs` RC=0 |
| Recovered compiler output | `workarea/bcplqsam-q4/q4punch-generated.asm` |
| Authenticated native deck | `workarea/bcplqsam-q4/q4punch.jcl`, 3,393 cards, preparation RC=0 |
| Prepared JCL SHA-256 | `537ae9ca00f6916cc808bcd4a23bda20776071f9224a2432fe3fbb74a93b5dde` |

The temporary-only generator checked source/IEWL boundaries, explicit optional BCPLQSAM selection, `&&Q4CARD` `NEW,PASS` -> `OLD,DELETE`, `RECFM=FB,LRECL=80,BLKSIZE=800`, `SYSPUNCH DD SYSOUT=B`, and no permanent PDS writes.

## Native JOB 7726 — Q4PUNCH

The owner submitted `Q4PUNCH` through the configured JES card reader; submission returned `JOB 7726`, RC=0.

**Owner-supplied MVS summary:** 30 OCT 26, 15:40:56–15:40:57 (resident JES clock). `JOB RESULT: SUCCESS`, `HIGHEST RC: 0000`, summary RC=0. IFOX reported **0 flagged statements, highest severity 0**. The complete ten-step execution reported:

| Step | Program | Observed result |
| --- | --- | --- |
| ASMA | IFOX00 | RC=0000 |
| ASMV | IFOX00 | RC=0000 |
| ASMN | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| ASMQ | IFOX00 | RC=0000 |
| ASMG | IFOX00 | RC=0000 |
| LKVR | IEWL | RC=0000 |
| LKED | IEWL | RC=0000 |
| WGO | Native BCPL | RC=0000 |
| VGO | Independent IFOX | RC=0000 |

The full JES report was successfully extracted locally (`Report RC=0`). Its supplied excerpts showed the required native output:

```text
BCPLQSAM Q4 FB80 PUNCH DUAL WRITE PASS
BCPLQSAM Q4 FB80 TEMP EXACT 3 PASS
```

The `WGO` BCPL application opened `Q4TEMP` and `SYSPUNCH` through G!200 `QSAMSVC` and wrote three identical FB80 records to both DDs. The `VGO` independent IFOX verifier read the passed `&&Q4CARD` dataset using QSAM GET, checked effective FB80 geometry, compared every EBCDIC byte including blanks and final-column markers, checked EODAD after three records, and returned RC=0000.

## JES2 punch file and separator interpretation

Read-only JES2 device reconnaissance before execution established `PUNCH1` at address `00D`, output queue/class `B`, mapped by Hercules to `mvs-state/pch/pch00d.txt`. The unchanged Hercules device definition uses **ASCII capture**:

```text
000D 3525 pch/pch00d.txt ascii
```

The host punch file began at **0 bytes**. After JOB 7726, the owner's inspection measured **172 bytes**. The initial comparator expected only three lines and reported an unmatched fourth empty record. The owner then compared the complete file against:

```python
expected = (
    b"Q4CARD01\n"
    + b"Q4CARD02" + b" " * 71 + b"X\n"
    + b"Q4CARD03" + b" " * 71 + b"Y\n"
    + b"\n"
)
```

The supplied result was:

```text
Capture bytes: 172
Three data cards plus blank separator: PASS
Inspection RC=0
```

The additional empty line is **consistent with a JES2 blank separator card**, but the capture comparison itself does not prove which component generated it. The initial host comparator's `NOT MATCHED / INCOMPLETE` was a false negative because it did not allow this observed separator.

The record data, as supplied in EBCDIC by the native BCPL program, comprised:

| Card | Columns 1–8 | Columns 9–79 | Column 80 |
| --- | --- | --- | --- |
| 1 | `Q4CARD01` | EBCDIC blanks `X'40'` | EBCDIC blank `X'40'` |
| 2 | `Q4CARD02` | EBCDIC blanks `X'40'` | `X` (`X'E7'`) |
| 3 | `Q4CARD03` | EBCDIC blanks `X'40'` | `Y` (`X'E8'`) |

The **independent temporary QSAM readback** establishes exact EBCDIC FB80 record content. The **ASCII Hercules punch capture** establishes that JES2 class-B punch output produced the three expected visible card lines and the additional separator. It does **not independently demonstrate physical 80-byte EBCDIC cards with trailing blanks at the device-capture layer**. No EBCDIC punch reconfiguration was necessary.

## Boundaries and remaining Q.4 work

- No Hercules device or configuration changes; no permanent installed MVS datasets or production BCPL object replacements.
- The temporary native build, source-selected BCPLQSAM and accepted Core Runtime remain distinct; no permanent System Extension release promotion.
- The test did not exercise `QS_FMT_FBA`, ASA carriage control, `SYSPRINT` FBA, or `QS_CAP_CARRIAGE`.
- The separate **SYSPRINT FBA carriage-control demonstration** and Q.4 acceptance/release decisions remain pending. Future FBA source or JES actions require their own approval under the project operator policy.
- Operator-local evidence: `workarea/bcplqsam-q4/q4compile.log`, `q4prepare.log`, `q4submit.log`, `q4summary.txt`, `q4report.txt`, and the host punch file. These are not checked into Git.

**Outcome:** Q.4's FB80 `SYSPUNCH` demonstration passed the owner-run native and host capture checks. **Q.4 — SYSOUT devices remains IN PROGRESS; not closed.**
