# Dynamic BCPLIO stream milestone — M3 output/mixed-stream exit review

Status: **M3 logical mixed-stream gate 133 ACCEPTED on DEVOBJ; physical DD attribution and full 00..133 sweep remain open**
Date: 2026-10-17
Prerequisite: **M2 CLOSED**, complete DEVOBJ 00..132 **132 PASS / 0 FAIL / 1 expected SKIP 083**.

## Scope

The parent milestone M3 asks for independent dynamic FB132 output
buffering, FINDOUTPUT, SELECTOUTPUT/OUTPUT, WRCH/WRAPOUTPUT, ENDWRITE,
flush on close/termination, and mixed read/write operation while
preserving SYSPRINT and BCPALT. The M5 exit separately calls for
**lossless per-DD physical SYSOUT attribution**.

## Evidence already accepted under M1/M2

| Behavior | Existing native regression |
|---|---|
| Arbitrary named REPORT/REPORT2 output; independent partial buffers and close | 124 |
| Duplicate normalized FINDOUTPUT returns same live handle | 127 |
| FINISH flushes two still-partial dynamic reports | 128 |
| STOP(8) flushes two still-partial dynamic reports | 129 |
| Same dynamic DD reopened as new output handle; stale rejected | 131 |
| Baseline output, wrap and overflow semantics | 101–115 |
| Dynamic input and output open at once, some switching | 128/129 |
| Entire stable DEVOBJ baseline after those changes | 00..132: 132 PASS, 0 FAIL, expected SKIP 083 |

The regression record checker matches ordered logical records in
the combined JES output; it does **not** independently associate
the physical record with the originating DD. A passing REPORT
fixture does not yet establish true REPORT DD attribution, and
trailing physical FB132 spaces are not preserved by that checker.
Neither limitation should be disguised as verified.

## New focused gate — regression 133

`native-compiler/regression/133-dynamic-dd-mixed-stream-interleaving/`
contains a permanent candidate-only compiled BCPL source, separate
two-record DD01/DD02 input fixtures, distinct REPORT/REPORT2 output
fixtures, and a primary success marker. It opens all four streams
together, alternates input GET across two sources with output
partial-buffer writes, crosses FB80 record boundaries and EOF,
finishes each output's records, and closes all resources explicitly.

**NOT EXECUTED:** source/fixtures are staged only. No BCPLIO,
compiler, or JCL harness implementation changed. PASS 133 would
validate logical mixed-mode correctness in the existing checker.
M3 functional acceptance can then be documented with M5 still
responsible for lossless DD-specific attribution.

## Operator gate

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 133 --show-output
```

Expected GO RC0000, exact primary `BCPL MIXED STREAM OK`,
REPORT logical records `REPORT AB` and `SECOND 1`, and REPORT2
logical records `REPORT2 QR` and `SECOND 2`. If PASS, run
full `00..133` checkpoint and record exact evidence. Do not claim
regression 133 has executed before operator supplies the result.

M5 additionally requires reproducible separate DD SYSOUT extraction,
negative attribution tests (swapped DDs), and physical FB132 record
comparison before closing the overall dynamic-stream milestone.

## Focused regression 133 — ACCEPTED on DEVOBJ (MVS 2026-10-17)

Operator pulled Git main from `c4f7a8d` through `b25d643`
and ran `tools/native/run-regression 133 --show-output`
against the **unchanged** DEVOBJ `BCPLM6 + BCPLIO`
candidate. The observed regression summary was:

```text
NATIVE REGRESSION 133..133 (1 tests)
RUN 133 133-dynamic-dd-mixed-stream-interleaving
PASS 133 133-dynamic-dd-mixed-stream-interleaving
PASS 1
FAIL 0
SKIP 0
TOTAL 1
```

**ACCEPTED: M3 logical mixed-stream test gate.** This compiled
BCPL application opens two dynamic inputs and two dynamic outputs
simultaneously, repeatedly switches between their independent
cursor/buffer states, completes two records per named output, and
returns to primary output successfully. The existing combined-JES
checker accepted the expected *logical* records. No compiler,
runtime assembler, MVS PDS or harness change was required.
The preceding full 00..132 compatibility sweep remains the
last full accepted panel (132 PASS, 0 FAIL, expected SKIP 083);
a full 00..133 sweep has **not** been supplied.

**Important acceptance boundary:** Full parent M3 exit requires
proof that the records were physically emitted on the correct
JES DDs, not merely found in a flattened printer report. That
physical attribution is expressly a separate M5 infrastructure
gate and remains unverified. Record M3's functional/logical
criteria as demonstrated, but do **not** declare the entire
dynamic-stream milestone complete or claim strict per-DD identity.

Next: commence M4.0 ordinary invalid-DD-name tests without
runtime changes; perform a full compatibility sweep with the
newly staged cases before any runtime implementation change.
