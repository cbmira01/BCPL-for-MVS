# Milestone — BCPLIO dynamic streams: M5.3 compiled-BCPL coverage review

Status: **M5.3 REVIEW STAGED (2026-10-17), not yet accepted as a completed gate**.
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

## Proposed disposition

**M5.3 IN REVIEW** on known executed work; no new BCPL
runtime changes or JCL submission have been made at
this gate. Next is a tightly scoped coverage decision,
followed by M5.4 current runtime documentation and
M5.5 final full regression / formal acceptance.
The separate decision to promote DEVOBJ -> OBJ
remains outside this milestone.
