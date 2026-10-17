# Milestone — BCPLIO dynamic streams: M5.3 compiled-BCPL coverage review

Status: **M5.3 CLOSED (2026-10-17), scoped compiled-BCPL coverage accepted using existing test and MVS evidence; no new M5.3 program/JES job required.**
Prerequisites: M5.0/M5.1/M5.2 CLOSED. The last accepted full DEVOBJ
regression panel is **00..145: 145 PASS / 0 FAIL / expected SKIP 083**,
with **145/145 saved logs audited**, from M4.4.
Physical proof: A/Z printer routing **JOB 8184**; exact
QSAM FB132 separate sequential-dataset readback **JOB 8185**;
wrong final FB132 pad byte rejected **JOB 8186**.

## Purpose and restraint

M5.3 confirms that the *compiled Cambridge BCPL* runtime exercises
the relevant stream behaviors and that the physical-output
proofs adequately cover the core QSAM boundary.
**Do not multiply existing tests without finding a real gap.**
The owner closed M5.1 by separating QSAM record formation
(BCPLIO responsibility) from JES2 internal spooling (MVS responsibility).
We must neither reopen original raw JES2 spool extraction nor
claim it was proven.

## Existing permanent native regression coverage

| Area | Existing tests | Already observed evidence |
|---|---|---|
| Built-in SYSPRINT/BCPALT, output buffer separation, switching | 101–115 (especially 101, 102, 103, 106, 110–115) | M4.4 full panel, plus M5.1.1 JOB 8184 class-separated physical routing on case 114 |
| Newline recordization, empty output records, exact 132-byte limit and overflow | 110–113 | M4.4 full panel; combined JES text alone **cannot** validate raw FB132 trailing padding |
| Dynamic REPORT/REPORT2, independent output handle selection and switching, missing DD rejection, close and partial final record | 124 | M4.4 full panel; **JOB 8185** physical REPORT/REPORT2 FB132 byte-exact QSAM readback |
| Dynamic input DDs, multi-open and per-stream cursor state | 125, 126, 130 | M4.4 full panel; these tests are primarily *input* semantics |
| Duplicate FIND handle; stale selection; close/reopen | 127, 131, 132 | M4.4 full panel; case 131 focused acceptance |
| FINISH drains partial dynamically buffered output | 128 | Accepted focused test and M4.4 full panel, **logical** expected REPORT/REPORT2 records |
| STOP(8) drains partial dynamically buffered output | 129 | Accepted focused test and M4.4 full panel; GO **RC0008 expected**, not an abend |
| Interleave two input DDs and two output DDs with all streams live | 133 | Accepted focused M3 case and M4.4 full panel, **logical** fixtures |
| Invalid names, failure-side descriptor lifecycle and accounting | 134–145 | M4.4 focused gates and full panel/audit; actual host-side post-QSAM JES spooling outside scope |
| Independent byte-accurate QSAM checker and a real negative padding fault | External probes JOBS 8185 and 8186 | Verified full EBCDIC 132-byte GET/CLC and intended RC0012 on altered expected padding |

The *scope of combined proof* matters. The full panel establishes
behavior under the existing per-case logical regression harness;
JOB 8184 provides a distinct device-routing observation;
JOB 8185 provides complete QSAM FB132 *record* comparison
for the case-124 output pattern; JOB 8186 demonstrates that the
same checker rejects a changed byte. These are complementary.
They are **not** an exhaustive byte-accurate physical execution
of every case in the full suite.

## M5.3 review/gap decision

- Preserve original numbered case sources, expected fixtures, and
  current DEVOBJ candidate object PDS members.
- Check the original program and accepted result of each identified
  behavior against the inventory. Cite known accepted earlier
  evidence rather than marking previously executed jobs as new runs.
- Treat the prior 145/0/1 full panel as the accepted compatibility
  baseline; **M5.5** remains the final fresh full-panel gate.
- The *outstanding detail* is whether any promised output
  behavior needs a byte-exact QSAM proof beyond case 124's
  two DDs and the class-separated 114 routing. Cases 128/129/131/133
  were accepted logically; their *internal JES SYSOUT* bytes must
  not become a new obligation by accident. If the acceptance
  boundary remains QSAM output, existing evidence may suffice
  for M5.3 without a new job.
- Don't claim native physical record fidelity for all cases
  merely from JOB 8185. If new *BCPLIO-to-QSAM* coverage
  is required, specify exactly one missing scenario and
  one focused candidate-only verification, rather than
  creating a new generalized spool acquisition system.

## M5.3 final source-to-evidence reconciliation — CLOSED 2026-10-17

The owner authorized completion of M5.3 after M5.2 had
closed on the deliberate JOB 8186 negative result. The
review compared the actual permanent compiled-BCPL
sources for tests 101, 103, 110–114, 124, 127–129,
131–133, the relevant existing case descriptions, and the
M4.4 full DEVOBJ regression acceptance and audited logs.
The following test intentions are present in source:

| Question | Concrete permanent compiled-BCPL evidence | Accepted execution evidence |
|---|---|---|
| Can two default output buffers remain independent when selected alternately? | 101 and 114 interleave characters between SYSPRINT and BCPALT; 114 terminates some records by newline and others by FINISH | M4.4 00..145; A/Z class-separated printer experiment JOB 8184 on 114 |
| Does newline create a record, even an empty one, and does the exact record length limit hold? | 110 writes A/newline/B; 111 writes consecutive newlines; 112 writes exactly 132 'A' bytes; 113 writes 133 'A' bytes for rejection | M4.4 suite including expected nonzero returns; *logical* record/RC evidence, not independent full-byte readback for each case |
| Are dynamic named output DDs, switching and close handled correctly? | 124 uses distinct REPORT and REPORT2, interleaves output with a partial record, rejects missing NOFILE and stale handles, closes with ENDWRITE | M4.4 suite and physical QSAM FB132 byte-exact verification of case 124 via JOB 8185 |
| Do dynamic input streams and handle identities work? | 125, 126, 130 exercise multiple dynamic input DDs; 127 duplicate FIND; 131 output DD close/reopen; 132 input DD reopen without promising rewind | M4.4 suite; earlier focused acceptance for 131 |
| Is pending output drained on FINISH and STOP? | 128 has two partial dynamic output records with no ENDWRITE, finishes normally; 129 uses STOP(8) without explicit close and requires deliberate GO RC0008 | Earlier focused cases 128/129 and M4.4 accepted suite; **logical** output evidence |
| Can multiple dynamic input/output streams be interleaved? | 133 opens DD01, DD02, REPORT, REPORT2 simultaneously and alternates reads/writes, records and EOF | Earlier M3 acceptance plus M4.4 suite; **logical** output evidence |
| Does the FB132 record verifier reject a bad trailing byte rather than accept right-trimmed text? | JOB 8185 VCHK QSAM GET followed by CLC of full 132 bytes; JOB 8186 inserts only MVI EXP11+131,C'X' in expected buffer | JOB 8185 VCHK RC0000; JOB 8186 VCHK **RC0012**, all preceding steps RC0000 |
| Are failure cleanup and ordinary stream contracts compatible with historical BCPL interfaces? | 134–145 and baseline 094–119; temporary fault tests do not introduce public BCPL globals | M4.4 full run and audited 145/145 saved logs |

### Actual accepted checkpoint (no new run)

- **M4.4 candidate regression 00..145:** 146 cases,
  145 PASS, 0 FAIL, expected SKIP 083; 145/145
  saved logs audited. Compile-only case 048 has no
  GO. Candidate runtime is DEVOBJ(BCPLM6 + BCPLIO).
- **M5.1.1 JOB 8184 AT114R:** separate class A/Z
  printer routes for SYSPRINT and BCPALT; ASMAP,
  LKED and GO RC0000.
- **M5.1.2 JOB 8185 M5D124B:** compiled BCPL GO
  and independent assembler GET/CLC verifier returned
  RC0000 across all six steps; REPORT (two records)
  and REPORT2 (one record) checked in separate
  physical FB132 sequential datasets, all 132 bytes
  including EBCDIC pad and exact EOF.
- **M5.2 JOB 8186 M52PAD:** deliberate wrong
  EBCDIC padding expectation caused VCHK RC0012
  while ASMAP/LKED/GO/VASM/VLINK all RC0000.
  This is the expected result for the negative test.
- **Offline negative controls:** previously accepted
  A/Z attribution tests 10/10; M5.2 8/8; M5.2
  generated-artifact review PASS.

These are **previously observed** results, not jobs
rerun during this M5.3 review. Original PDS, compiler,
BCPLIO and BCPLMAIN remained unchanged.

### Boundary and remaining work

- The byte-exact QSAM experiment covered the
  **case 124** output pattern; do not claim every
  numbered case independently received byte-exact
  physical readback. Cases 128/129/131/133 remain
  logically verified under the existing harness.
- The class-separated printer experiment establishes
  the observed SYSPRINT/BCPALT routing, **not** unchanged
  raw JES2 spool records. JES2 internal spooling is
  outside the agreed BCPLIO acceptance boundary.
- The original strict M5.0 demand for exact per-DD
  raw JES2 spool acquisition was expressly superseded
  and M5.1 closed on the QSAM record boundary.
- No remaining *BCPLIO-to-QSAM behavior gap* requires
  a new dedicated M5.3 compiled test for the agreed
  milestone scope. Expanding into byte-exact datasets
  for every case would duplicate existing tests without
  a specific observed defect.
- **No regression runner or standard JCL was changed
  in M5.3.** The separate M5.1/M5.2 experimental JCL
  and checkers are reusable research artifacts; whether
  to consolidate them into the ordinary runner is a
  separate, optional maintenance decision, not a
  prerequisite to accepting BCPLIO.

**M5.3 CLOSED (scoped).** This is a review and
reconciliation of accepted test evidence, not a
fresh full candidate regression. Proceed to M5.4
for a **current** dynamic BCPLIO contract and
clean-room reconstruction/runbook, retaining
historical contracts as dated predecessors.
**M5.5 remains open** for a fresh DEVOBJ 00..145
full run, log audit and final milestone acceptance.
Promotion from DEVOBJ to production OBJ is neither
performed nor implied.
