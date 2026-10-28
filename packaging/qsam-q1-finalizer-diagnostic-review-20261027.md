# Milestone QSAM — March Q.1 single-job finalizer diagnostic candidate

**Status:** Test-only development candidate; Q.1 OPEN / NOT ACCEPTED.
**Source baseline:** GitHub `main` commit `75c2b37d5f12d85067f208c07ea4403d8b0fdc9a`.
**Authorization:** Preparation and offline tests only. No GitHub commit and no JES submission.

## Design

`prepare-q1-finalizer-diagnostic.py` derives **one** disposable `Q1FDIAG`
job from the already compiled, isolated, temporary-16-DD `Q16FIN` JCL.
It refuses any modified/duplicated `ASMQ` baseline; changes only ASMQ's
in-stream source, the JOB card identity and the temporary IEWL load-member
name; preserves GO REGION=256K, 16 distinct F1024 DDs and all other steps.
It creates its output with `O_EXCL`, only inside ignored Q.1 workarea.

The temporary QSMFIN overlay calls one independent `QFPROBE` CSECT on
entry, after the existing CLOSE loop, and at return. Three runtime WTO
records encode separate fullword (eight-digit EBCDIC hex) snapshots:

- `Q1F:E:<reason>:<live>:<DCBs>:<stages>`
- `Q1F:L:<successes>:<live>:<DCBs>:<stages>:<status>`
- `Q1F:X:<successes>:<live>:<DCBs>:<stages>:<status>`

The list-form WTO macro text begins four bytes after the list header,
as in the historical list/execute-form convention; **this needs IFOX/MVS
validation**. The probe uses standard register save/restore and the same
byte-to-EBCDIC-hex algorithm as the existing Q.1 identity diagnostic.
It uses no BCPLIO output, no public API change, no fault injection, and
no change to `BCPLMAIN`, `BCPLRGS`, or the source-controlled QSAM assembler.
A failed instrumentation output must not obscure native service results.

`check-q1-finalizer-diagnostic.py` requires the exact Q1FDIAG job/ten
steps RC=0, clean assembler severity, native Q16FIN application PASS,
and exactly one ordered `E,L,X` triplet from the **same JES job number**
between console `IEF403I` and `IEF404I`. Its expected observations are:
entry `[0,16,16,16]` and both post-loop/exit `[16,0,0,0,0]`.
Missing/duplicated/malformed/falsely correlated traces fail closed.

## Offline verification

`python3 -m py_compile` and 12 focused unit tests PASS locally, including
fixed-card width, three invocation sites, fail-closed `ASMQ` matching,
JCL identity isolation, wrong status/count/order, and listing-only/other
job rejection. The full repository-backed synthetic deck and actual
IFOX `WTO MF=L/MF=E` expansion **have not yet been executed**; those
are required before any native evidence can be accepted.

## Pending gates

1. Owner approval for a single test-only commit to GitHub `main`.
2. WSL full-source offline check and new JCL preparation (no JES).
3. Separate explicit approval for **one** `Q1FDIAG` JES submission.
4. Native report, hardcopy console WTO review, no RC-only acceptance.

The known `Q1NEG` caller error (`Q!1` not reset before invalid handle)
is a **separate pending test-only correction** and is not bundled into
this specifically requested single-diagnostic candidate.
