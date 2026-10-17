# Handoff — repository cleanup and native regression-runner review

**Repository:** `cbmira01/BCPL-for-MVS`, branch `main`.
**Date:** 17 October 2026. **Scope:** a new
post-milestone read-only audit and discussion.
No cleanup deletions, implementation changes,
or new regression runs authorized yet.

## Accepted stable baseline

**BCPLIO dynamic stream is formally CLOSED**;
owner accepted all M0–M5.5 gates.
Authoritative records:
[final acceptance](../bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md),
[master history](../bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream.md),
[current runtime contract](../bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md)
and [single clean-room rebuild runbook]
(../clean-room-mvs-reconstruction.md).

- Compiler: **CAMBCOMP is INTCODE running under ICINT19**;
  produces native S/370 assembler; IFOX and IEWL
  assemble/link the application. It is not itself
  an S/370 native compiler load module.
- Runtime: `NATIVE_DEVOBJ(BCPLM6, BCPLIO, BCPLBYTE, BCPLAPT)`
  candidate; `NATIVE_OBJ(BCPLMEM, BLIB)` accepted
  support, and `NATIVE_OBJ(BCPLMAIN)` remains
  the existing production runtime. The DEVOBJ
  candidate was **not promoted** to NATIVE_OBJ.
- Owner-accepted candidate native suite 00–145:
  **145 PASS, 0 FAIL, one expected SKIP 083**;
  145/145 fresh saved-log/step audit PASS at
  Git `57c7354cf728ba3a46aef7e8f140006e1d3e5aeb`.
  Case 048 is compile-only; cases 052/093 use
  BCPLM6-specific GO-RC expectations. Some STOP
  cases deliberately return nonzero GO RC.
- Additional physical MVS evidence: JOB **8184**
  A/Z-separated default streams, **8185** two
  distinct dynamic FB132 QSAM datasets full 132-byte
  readback, **8186** verifier negative padding
  byte (expected VCHK RC0012). Not all native
  cases received physical FB132 checks; JES2
  spool internals are outside the BCPLIO scope.
- Fresh-run evidence caveat: a **second** suite
  invocation following successful M5.5 `verify`
  overwrote the normal transcript and some
  per-case logs, then was interrupted at case 02.
  Original acceptance stands. Preserve the
  original `m55-verification.json` receipt and
  complete operator paste. A 298-line recovered
  first transcript SHA-256
  `5623d6949629ccfa38833b8f4765c42053bd18a54bed795e4ec989a80eff63fe`
  has **not** been matched against the receipt;
  never claim byte-exact restoration without that test.

## Examine the existing runner before proposing a rewrite

| Function | Paths | Questions |
|---|---|---|
| Suite orchestration | `tools/native/run-regression` | Case discovery, numeric naming, inclusive ranges, candidate-only requirements, SKIP 083 and log overwrites |
| Compile/link/GO harness | `native-compiler/regression/run-test-mvs.sh`, `run-test.sh` | Cambridge compilation, JCL generation, job submission, named DD fixtures, JES extraction, error handling |
| Installed-PDS JCL generator | `tools/checks/prepare-runtime-pds-regression.py` | Explicit BCPLM6+BCPLIO DEVOBJ links, BCPLMEM/BLIB OBJ links and M4.3 test-only assembler injection |
| Numbered cases and fixtures | `native-compiler/regression/*/` | BCPL source, README, expected text and GO RC, DD records, candidate-only markers, compile-only test 048 |
| Existing preflight and audits | `tools/checks/check-m44-compatibility.py`, `check-m44-full-panel-logs.py` | 00..145 guard, 145 expected logs, nuanced RC tests, abend detection, generated job TSV |
| Final fresh-run receipt | `tools/checks/m55-final-evidence.py` + unit tests | Snapshot `begin`, run transcript, timestamp-gated `verify`, 11 tests, immutable archive and repeat-run safety |
| Physical QSAM probes | `tools/checks/m51-*.py`, `m52-padding-negative.py`, `test-dd-attribution.py` | Optional independent byte-accurate profile vs ordinary functional suite |
| MVS/PDS backend | `tools/mvs/`, `tools/datasets/dspal`, `config/dspal.yaml` | Authenticated job submission, JES numbers, DSNs, manifest members, source-vs-object handling |

## Repository cleanup candidates — inventory only

- Verify stale instruction files: `native-compiler/mvs-resident-cambridge.md`
  references old dataset aliases; `native-compiler/asm/README.md`
  may still call ICINT17 current; other dated M3/M4
  documents conflict with today's navigation. Keep
  historical evidence clearly marked rather than deleting it.
- Check `config/dspal.yaml` manifest against authoritative
  build files: `BLDDEVI` is mapped, while
  `BLDDEVM6` is explicitly installed by `dspal put`.
  Any change requires review of the clean-room path.
- Classify WIP assemblers, old candidate variants,
  one-off probes/JCL generators, wrappers, and copied
  descriptions as *active canonical*, *historical
  evidence*, *superseded*, or *potentially removable*.
  Inspect references and dependencies before deletion.
- `workarea/` contains precious post-acceptance
  evidence despite being a generated directory.
  `mvs-state/` contains persistent TK5 state.
  **Do not erase either**, call `purgebcpl`,
  edit secrets or modify MVS PDS modules during audit.

## Questions for the user before implementation

1. Should the standard runner prove **logical BCPL
   behavior only**, with optional external exact-QSAM
   physical verification, or should both run together?
2. Would numbered programs remain separate from
   M5.1/M5.2 external physical tests, or should
   a case support multiple verifier backends?
3. How much generated JCL/probe tooling should
   become reusable, without overengineering an
   obsolete language's simple historical runtime?
4. Should each run have a unique directory/ID with
   immutable logs, job manifest and receipt rather
   than overwriting prior `workarea/native-regression/logs`?
5. Should fresh-log/expected-RC/abend auditing
   move into routine regression execution? How
   to keep intentional nonzero GO RCs and candidate
   profiles correct?
6. Which historical docs and obsolete experiments
   merit archiving rather than removal?

## First march / operating rule

**First do a read-only repository and tool inventory.**
Produce a human-readable layout and current-vs-obsolete
classification with references, and discuss the
runner questions before authorizing cleanup.
No automatic removals, renumbering, runtime edits,
MVS job submission, or OBJ promotion. Preserve
the M5.5 **145/0/1** accepted regression as the
future non-regression target; never pretend prior
accepted outputs are newly measured.

**Suggested new-conversation opening:** 
"Begin repository cleanup and a review of the native
regression runner. First inventory and classify the
current repository, runner/JCL workflow and stale
historical tooling without changing files. I have
questions about regression execution and verification;
discuss the design choices before any refactor."
