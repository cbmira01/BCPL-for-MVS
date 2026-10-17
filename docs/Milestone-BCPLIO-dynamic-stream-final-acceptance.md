# BCPLIO dynamic stream — final milestone acceptance

**Decision:** ACCEPTED and CLOSED by the project owner, 17 October 2026.
**Scope:** the native Cambridge BCPL character-stream runtime on MVS 3.8J,
using independent BCPLIO and DEVOBJ(BCPLM6) candidate objects. This is a
milestone sign-off, **not** authorization to promote a module into
production NATIVE_OBJ.

## Acceptance rationale and evidence ledger

The owner explicitly agreed to close M5.5 after reviewing the
operator-supplied first completed final-panel output and the
successfully executed strict offline auditor.

| Evidence | Accepted result | Boundary |
|---|---|---|
| M4.4 compatibility | Prior 00..145 DEVOBJ run: 145 PASS / 0 FAIL / expected SKIP 083, 145/145 saved job logs audited | Prior compatibility baseline |
| M5.1.1, JOB **8184** | Original 114 workload; class A/SYSPRINT and class Z/BCPALT routed to separate observed printer images | Output routing; **not** raw JES2 spool-byte proof |
| M5.1.2, JOB **8185** | Original 124 workload; QSAM FB132 REPORT and REPORT2 written to distinct temporary datasets, read back with native verifier comparing all 132 EBCDIC bytes, record order/count and EOF; six steps RC0000 | Byte-exact **sequential dataset** output, not JES2 spool internals |
| M5.2, JOB **8186** | Verifier's *expected* 132nd FB132 padding byte deliberately altered; five preceding steps RC0000, VCHK expected RC0012; 8/8 offline tests and positive integrity review PASS | Checker demonstrated fail-closed comparison; GO application remained unchanged |
| M5.3 | Reviewed existing native stream cases 094–145 against source and accepted execution records | No duplicate regression needed; not all cases independently byte-verified through QSAM |
| M5.4 | Current dynamic-stream contract and canonical clean-room reconstruction runbook published | Documentation-only; does not assert an entirely fresh destructive PDS reconstruction |
| **M5.5 final operator run** | Commit **57c7354cf728ba3a46aef7e8f140006e1d3e5aeb**; 11/11 offline self-tests PASS (twice), candidate source preflight PASS; full native 00..145 runner **145 PASS / 0 FAIL / one expected SKIP 083 / TOTAL 146**; independent audit **145/145 fresh saved logs PASS**; no detected known-defect or abend exceptions; receipt created | Fresh DEVOBJ runtime final compatibility gate, not production OBJ |

The accepted M5.5 first-run output reported GO return-code distribution
**0000=139, 0008=3, 0012=1, 0100=1**, including expected nonzero
test completions; case 048 is compile-only and 083 is the deliberate
source-only skip. The successful run and immediately following
`m55-final-evidence.py verify` were reported together in the
operator's terminal output, and the checker wrote
`workarea/native-regression/m55-verification.json` with status
`VERIFIED_AWAITING_OWNER_ACCEPTANCE`. The owner subsequently
**accepted** the result in this milestone closure decision.

## Recorded evidence caveat: interrupted duplicate run

**After** the verified first run, the operator started the same
full regression a second time, completed tests 00 and 01, and
interrupted the job while testing 02. The second invocation
truncated the path `workarea/native-regression/m55-full-panel.log`
and may have replaced saved logs for cases 00–02.

This **does not rescind the successful first-run result** or its
completed contemporaneous verification. It **does** mean one must
not assert that the original full transcript and 145 pre-interruption
case files remain intact on disk. Preserve the original
`m55-verification.json`, first-run terminal paste, and the later
interrupted second-run files distinctly. A reconstructed transcript
from the paste is *not* treated as byte-identical to the original
unless its SHA-256 matches the receipt's recorded
`runner_transcript_sha256`; this comparison was not reported.
No repeat full regression is required for the milestone's owner
acceptance solely due to the later interrupted duplicate.

## Architectural scope and boundaries

The historical BCPL character-stream API is implemented on top of
MVS QSAM's record-oriented services. Native core streams expose
named JCL DDs, selected input/output and BCPL character operations,
not QSAM's full record/DSORG/RECFM semantics. FB80 right-trimmed
input with synthetic newline and FB132 EBCDIC blank-padded
output define the supported record translation.

MVS decides dataset compatibility and errors. BCPLIO's recovery
promises are limited to faults *returning control* to it;
unrecoverable MVS OPEN/GET/PUT/CLOSE abends are not required to be
caught. JES2 owns spool internals and subsequent output routing:
original strict raw JES2 spool-byte acquisition was
**explicitly superseded**, not demonstrated.

No BCPL compiler change, global-vector numbering change,
new QSAM/VSAM application library, JCL refactoring,
new runtime module, clean-room purge, or DEVOBJ-to-OBJ
promotion is part of this acceptance.

## Final disposition

**M0–M5.5 and the parent “Milestone — BCPLIO dynamic stream”
are formally CLOSED** under the above scoped contract.
The established DEVOBJ(BCPLM6+BCPLIO) implementation is
accepted as the milestone candidate. Historical milestones
retain their dated progress notes for audit.

**Nothing else is required to close this milestone.**
Optional future work, needing its own authorization and scope,
could include: archiving/restoring exact post-run evidence,
integrating independent QSAM verifiers into the ordinary
regression runner, performing the complete destructive
clean-room rebuild as a distinct reproduction exercise,
a decision on NATIVE_OBJ production promotion, or
designing an optional BCPLQSAM/VSAM record-access library.
None is a deferred acceptance criterion here.

Related documents:
[master milestone](Milestone-BCPLIO-dynamic-stream.md),
[M5.5 gate history](Milestone-BCPLIO-dynamic-stream-M5.5-plan.md),
[current runtime contract](BCPLIO-dynamic-runtime-contract.md),
[canonical clean-room procedure](../packaging/clean-room-mvs-reconstruction.md).
