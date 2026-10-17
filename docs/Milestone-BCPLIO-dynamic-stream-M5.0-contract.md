# Milestone — BCPLIO dynamic streams: M5.0 evidence and acceptance contract

**Status: M5.0 ACCEPTED BY OWNER (2026-10-17); M5.1 acquisition feasibility IN PROGRESS; M5.2–M5.5 NOT STARTED.**
Parent: [Milestone-BCPLIO-dynamic-stream.md](Milestone-BCPLIO-dynamic-stream.md)
Prerequisite: M4.4 DEVOBJ(BCPLM6 + BCPLIO) CLOSED, full native 00..145 **145 PASS / 0 FAIL / 1 expected SKIP 083**, with **145/145 saved logs audited**.
M5.0 performs source inspection and designs a proof. **No JES/MVS experiment, PDS update, runtime/ABI change, or physical byte capture has been performed by this gate.**

## 1. Proof obligation and why M4.4 is insufficient

M4.4 established behavior as represented by the existing tests. M5 must
independently establish physical output identity and record fidelity:

1. **Logical content:** compiled BCPL emitted an expected ordered logical
   sequence found in its combined JES job report. Already covered.
2. **Physical attribution:** that job, GO step and actual JCL DD received
   the record, not merely some printer/report suffix.
3. **Record fidelity:** the original *ordered, complete 132-byte EBCDIC
   FB132 records* match their expected contents and trailing X'40' blanks,
   with no printer reformatting, right-trim, transcoding or inserted newlines.
4. **Completeness:** no missing, extra, repeated, reordered or cross-DD
   records. Matching only a contiguous subsequence is insufficient.

M5 final acceptance requires (2), (3) and (4), with genuine independently
identified DD output artifacts. Do not claim that an independently
readable sequential dataset is an unchanged JES spool image, or vice
versa. If the literal raw SYSOUT bytes cannot be acquired, disclose
the limitation and require an explicit acceptance-scope decision.

## 2. Inventory of currently available mechanisms

| Existing file/test | Observed source behavior | Evidence boundary |
|---|---|---|
| tools/checks/check-combined-jes-records.py | Searches post-link printer report, right-trims trailing whitespace | Proves expected logical sequence exists somewhere in combined output; loses DD identity and padding |
| tools/checks/check-dd-attribution.py | Reads job-delimited class-A / PRINTER1 and class-Z / PRINTER2 printer-file sections from saved offsets; right-trims output | Can distinguish separate printer routes for a controlled probe, **not** the original full 132-byte QSAM records |
| tools/checks/test-dd-attribution.py | Offline positive and negative synthetic printer tests (wrong job, swapped output, lost record, foreign banner, leading whitespace, etc.) | Reusable checker test foundation; no direct JES byte capture |
| tools/checks/prepare-dd-attribution-probe.py | Rewrites generated regression 114 GO JCL to AT114R, SYSOUT=A for SYSPRINT and SYSOUT=Z for BCPALT | A probe generator, not a submission/capture utility. Its class/device assumptions require actual TK5 configuration confirmation |
| tools/mvs/dump-report-for-job, native regression runner | Job/step diagnostics, combined JES output, per-case logs | M4.4 job outcomes and logical content, not independent lossless DD bytes |
| tools/datasets/dspal | Managed dataset metadata and text PDS member retrieval and JCL submission | Its get facility is for text PDS members; binary sequential FB132 host export is **not demonstrated** |
| Regressions 114, 124, 128, 129, 131, 133 | Interleaving, REPORT/REPORT2 routing, FINISH and STOP(8) partial flush, output reopening, mixed stream behavior | Passed logically in M4.4; **not physical DD-specific, byte-exact proof** |
| native-compiler/regression/native-stream-contract.md | Earlier fixed-DD baseline and printed-output caveats | Retain as history, add current dynamic contract during M5.4 |

These are **source inspection results**, not a claim that printer class Z,
raw JES2 spool export, or host-side binary sequential-dataset extraction
is operational on the user's running MVS system.

## 3. Frozen compatibility and representation contract

| Name/service | Type | M5 treatment |
|---|---|---|
| BCPIN and BCPINB | Built-in QSAM FB80 input | Preserve and include baseline checks |
| SYSPRINT | Built-in QSAM FB132 output, startup-open | Validate physical output destination |
| BCPALT | Built-in second QSAM FB132 output | Validate physical output destination |
| FINDINPUT of arbitrary valid allocated DDs | Runtime-managed QSAM FB80 | No predeclared-name/slot ceiling; preserve dynamic discovery |
| FINDOUTPUT of REPORT, REPORT2, and arbitrary valid DDs | Runtime-managed QSAM FB132 | Principal output DD attribution target |
| FINDPARM / G39 | EXEC PARM memory-backed pseudo-stream | Preserve, not a physical QSAM DD |

The built-in input name is **BCPIN**, not BCPLIN. The four static DDs
remain supported and special. PARM is distinct from ordinary MVS DD
resolution. No new built-in stream names or public BCPL globals are needed.

Preserve the accepted FB80 input behavior: trim trailing padding,
synthesize newline character 10, EOF -1, independent UNRDCH; significant
trailing input blanks remain a documented limitation. Preserve FB132
output behavior: newline emits one blank-padded 132-byte record,
partial final record flushes at ENDWRITE / FINISH / STOP, newline can
emit an empty logical record, 132-character maximum, STOP(12) on
overlength. EBCDIC space padding is X'40'. The tests must not
alter accepted stream semantics to satisfy the physical checker.

## 4. Mandatory captured artifact and oracle

For each independent output destination, retain:
- exact Git revision, BCPL source/fixture identity, candidate runtime
  DEVOBJ BCPLM6 + BCPLIO and relevant installed object/build evidence;
- JES job ID, job name, GO step, **actual DD name**, physical allocation
  (SYSOUT class/device or distinct dataset) established independently
  from JCL and the acquisition mechanism;
- record organization (RECFM FB, LRECL 132, verified BLKSIZE), exact
  record count and ordered raw 132-byte EBCDIC payloads;
- expected records generated independently from an explicit padded
  EBCDIC fixture; byte-for-byte equality of the **entire sequence**;
- unambiguous PASS/FAIL, acquisition path, saved input/output artifacts
  and rejection diagnostics, not just a logical text match.

A 132*N-byte binary file may represent N concatenated FB132 records
only when DD identity, no transport headers, known record boundaries,
and exact length are independently established. A printer-formatted
file with page-feed/control bytes is **not** that binary capture.
The oracle must preserve significant leading characters and trailing
padding, identify EBCDIC vs host text, and reject additional records.

Mandatory offline negative cases: swap REPORT and REPORT2/DD identity,
wrong job or step, missing/extra/duplicate/reordered record, one
wrong meaningful byte, one modified trailing X'40' byte, wrong
record length, and cross-DD contamination. Every negative must fail
for the intended reason, not because the fixture cannot be parsed.

## 5. Proposed M5.1 acquisition decision tree

| Method | Advantage | Disposition |
|---|---|---|
| Direct **DD-labelled** raw JES2 SYSOUT spool acquisition | Could jointly establish actual spool DD identity and complete FB132 bytes | **Preferred if demonstrably available** in current TK5/JES/Hercules deployment; not established by source inventory |
| Separate SYSOUT classes routed to PRINTER1/PRINTER2 | Existing class-A/Z code provides a useful DD-route observation | **Supplement only**: printable images can strip padding or insert page marks; two classes do not automatically resolve four independent DDs |
| Separate, scratch FB132 sequential datasets assigned to each GO DD, with binary host export or independent MVS QSAM readback that compares all 132 bytes | Practical exact-record validation without the print-image transformation | Requires independently checked dataset/DD identity, correct record export/readback and negative tests; proves actual QSAM dataset path, **not automatically unchanged SYSOUT spool bytes** |
| Combined printer report or text PDS member extraction | Existing diagnostics | **Not acceptable** for final physical/byte proof |

**First experiment:** establish actual JES2/TK5 class/device routing and
available raw spool or record-level capture mechanisms, then use the
existing regression-114 A/Z probe as a minimal physical-routing check.
Run its offline unit tests first. A minimal MVS probe must preserve job
number, pre-submit offsets, printer paths, physical destination, actual
GO step codes, and captured artifacts. No direct raw-spool interface is
assumed to exist.

If direct raw spool acquisition is impossible, investigate independent
scratch FB132 sequential datasets and an independent byte-exact MVS
QSAM reader/export. Do not invent a binary dspal get operation, assert
an unverified JES API, or confuse printer text with an FB132 record.
If the resulting split evidence cannot satisfy the originally promised
SYSOUT requirement, flag a narrow scope decision instead of claiming
M5 acceptance.

## 6. March gates, exit criteria and stop rules

**M5.0 — this inventory and proof contract.** Exit is written,
traceable design for owner review with candidate acquisition methods,
strict success/negative conditions and a first experiment. Owner
review/acceptance is still required; design preparation does not
claim capture functionality.

**M5.1 — acquire per-DD evidence.** Demonstrate a repeatable,
attributed physical output artifact on actual TK5. Characterize
whether the artifact is raw spool data, printer image, or sequential
dataset, and whether it preserves original 132-byte records. Record
all exceptions and stop if only right-trimmed text is available.

**M5.2 — exact byte verification.** Build a fail-closed independent
verifier that compares entire ordered EBCDIC FB132 records for each
DD. Pass all positive/negative fixture tests, including changed
padding bytes, swapped DDs, omitted and extra records.

**M5.3 — compiled-BCPL physical tests.** Use accepted cases 114,
124, 128, 129, 131 and 133 as starting points, adding narrowly
scoped candidate-only regression cases >145 if needed. Validate
SYSPRINT/BCPALT, REPORT/REPORT2, interleaving, close/reopen,
FINISH/STOP, empty records, full length, padding, exact DD identity
and absence of contamination. Preserve original BCPL and ordinary
tests; do not replace the entire regression mechanism.

**M5.4 — current dynamic runtime contract and reconstruction runbook.**
Document special and dynamic streams, PARM, DD normalization,
FB80/FB132 and EBCDIC semantics, lifetime/cleanup, supported
error boundaries, M4.3 accounting evidence limitations,
successful clean-room DEVOBJ build/link/test procedure, and
precisely what the M5 acquisition approach proves. Keep historical
fixed-DD documentation as a dated predecessor.

**M5.5 — expanded full regression and final acceptance.**
Run all then-current DEVOBJ native tests (M4.4 baseline 00..145:
145 PASS / 0 FAIL / expected SKIP 083), new physical output
regressions and strict positive/negative checks. Retain JES
job IDs, step RC, complete artifacts and evidence ledger.
Complete only with owner acceptance and documented exceptions.
Production OBJ promotion is a **separate explicit decision**.

Not in scope: reopening M4 synthetic failures; modifying BCPLIO/
BCPLMAIN, compiler or global vector just to simplify capture;
new QSAM/VSAM application library; dataset dynamic allocation;
VB/BSAM; reentrant redesign; claimed recovery from real host
abends. All runtime/PDS changes require their own reviewed gate.
During M5.0 no jobs are submitted and no baseline is rerun.

## 7. M5.0 disposition

Repository evidence and test design are **prepared** at this gate.
No offline checker tests or MVS probe execution are represented as
completed merely by their presence in source. No lossless physical
DD acquisition is accepted, and the parent dynamic-stream
milestone remains OPEN. The next owner decision is whether
to accept this strict contract and authorize the limited
M5.1 feasibility experiments.

## 8. Formal acceptance of M5.0 — 2026-10-17

The owner explicitly accepted the M5.0 strict physical-evidence contract
and directed commencement of M5.1. Both true DD ownership and original
FB132 byte fidelity remain required; class-separated printable output
cannot substitute for full raw record verification.

**M5.0 CLOSED as a design gate.** No new MVS/JES experiment was carried
out to accept M5.0. M5.1 has its own limited feasibility scope.
See the M5.1 plan for the first deliberately non-submitting
preparation and controlled class-A/Z experiment.
