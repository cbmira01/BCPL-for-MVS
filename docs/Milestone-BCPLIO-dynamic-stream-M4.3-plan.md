# BCPLIO dynamic streams — M4.3 resource accountability

**Status: M4.3.0 and M4.3.1 ACCEPTED (2026-10-17); focused regression 139 PASS on corrected helper; M4.3.2 terminal/failure accounting OPEN.**
Date: 2026-10-17

## Contract

M4.3 measures BCPLIO-owned dynamic resource lifetime, without modifying canonical BCPLIO or installing any MVS object. M4.2's narrower returned-error recovery contract remains accepted. A real MVS abend is not an accounting regression PASS.

Each ordinary dynamic stream owns a 32-byte descriptor and 268-byte record/DCB region. A separate 16-byte stable handle identity is retained after ENDREAD/ENDWRITE as a tombstone until IOFIN invokes IODRAIN. Private DQOPEN enters SVC19; private DQCLOSE enters SVC20. Bootstrap/static streams and all other runtime storage are excluded.

## Private counters

An isolated generated BCPLIO adds an internal assembler entry named `IOACCT` (R1 ID, R15 count; -1 for invalid ID). It does not add a production BCPL global.

| ID | Counter | Meaning |
|---|---|---|
| 0 | M43G32 | successful descriptor GETMAIN |
| 1 | M43F32 | returned descriptor FREEMAIN |
| 2 | M43G268 | successful region GETMAIN |
| 3 | M43F268 | returned region FREEMAIN |
| 4 | M43G16 | successful stable handle GETMAIN |
| 5 | M43F16 | returned stable handle FREEMAIN |
| 6 | M43OATT | dynamic SVC19 attempts |
| 7 | M43OSUC | post-SVC19 DCB observed open |
| 8 | M43CATT | dynamic SVC20 attempts |
| 9 | M43CRET | returned dynamic SVC20 |

A returned FREEMAIN call does not by itself prove physical MVS reclamation; nor does SVC20 returning establish every host CLOSE result. Counters reflect instrumented runtime control flow, with separate lifecycle and host-completion evidence.

## First MVS run and correction (2026-10-17)

The operator ran the source audit successfully. Cambridge compilation
**JOB 7877** generated CODE. The first candidate-only GO deck,
**JOB 7878 (RG139R)**, produced:

| Step | Result |
|---|---|
| ASMAP / IFOX00 | RC=0000 |
| ASMFIO / IFOX00 (instrumented BCPLIO) | RC=0000 |
| ASMNAT / IFOX00 (native helper) | RC=0008 |
| IEWL LKED | Bypassed |
| GO | Bypassed |

ASMNAT statement 9 failed with **IFO209 ADDRESSABILITY ERROR** on
`L 15,=V(IOACCT)`. The test-only helper had no established base
register for the address-literal load. Its source was corrected with
`BALR 10,0` and `USING *,10` (with a subsequent `DROP 10`).
This is a harness error, not a tested BCPLIO accounting imbalance.
**That initial execution did not pass.** The corrected native helper was subsequently rerun; see acceptance evidence below.

## M4.3.1 acceptance — 2026-10-17

Operator-reported local rerun at commit `18a18f1`:

```text
M4.3 native counter shim base setup: source check PASS
M4.3 private source accounting checks: PASS
NATIVE REGRESSION 139..139 (1 tests)
PASS 139 139-dynamic-dd-resource-accounting
PASS 1 / FAIL 0 / SKIP 0
```

**M4.3.0 and M4.3.1 accepted** on that evidence. The supplied
summary did **not** contain the latest JES job number, individual
IFOX/IEWL GO codes, or a raw count trace. The deterministic
BCPL-side assertions in regression 139 establish the passing
pre-termination counter values and handle behavior within the
isolated instrumented GO job. They do not establish MVS's physical
FREEMAIN semantics, post-IODRAIN tombstone reclamation, or
failure-path accounting. Those remain M4.3.2. JOB 7878
is retained above as the superseded, unsuccessful attempt.

## Staged acceptance gates

**M4.3.0:** Run the source-only audit `python3 tools/checks/check-bcplio-m43-account.py`. It validates the exact GETMAIN/FREEMAIN/SVC source sites and rejects source drift, repeat instrumentation and overwide IFOX cards. Only an observed PASS can accept this gate.

**M4.3.1 (ACCEPTED):** Focused candidate-only compiled-BCPL test 139 uses existing regression G151 to call a separate test-only NATIVEAD assembler shim. It queries private IOACCT. Under MVS, ASMAP assembles the compiled BCPL program, ASMFIO assembles isolated BCPLIO, ASMNAT assembles NATIVEAD, and IEWL links both temporary objects with DEVOBJ(BCPLM6), without installed DEVOBJ(BCPLIO). GO asserts two live opens, duplicate FIND no extra OPEN, explicit ENDREAD releases descriptor/region but not the tombstone, fresh reopened identity, and three closes. It never reads the reopened instream DD DATA, avoiding an unfounded rewind guarantee. Marker: `M43 PRE-DRAIN COUNTS OK`.

## M4.3.2a — post-IODRAIN tests 140/141 staged (not run)

The private instrumentation supports an opt-in `--terminal-check`.
At DRAINDN, after the last descriptor and handle have been
processed, it requires DHEAD=HHEAD=0 and compares successful
32/268/16-byte GETMAIN counts to returned corresponding FREEMAIN
counts, as well as OPEN attempts, observed success, CLOSE attempts
and CLOSE returns. A mismatch intentionally branches to an invalid
opcode, generating S0C1 **in the private test-only module**.
Normal GO completion therefore demonstrates execution of the
assertions without mismatches; it is not independent proof of
physical MVS storage reclamation.

Cases 140 FINISH and 141 STOP(8) reuse the accepted regression
128 and 129 input/program/output fixtures respectively, adding only
the private terminal-check marker and isolated BCPLIO source.
The latter retains expected GO RC=0008. Their existing fixture
checks validate primary and named-output drain contents.
Do not replace canonical source or install any generated object.

Source-only checks and IFOX/IEWL/GO evidence are **pending**.
Counted synthetic failure modes (M4.3.2b), the complete
compatibility panel, and production OBJ promotion remain separate.
**M4.3.2 (partially staged):** Add separately counted synthetic 32/268/16 and DQOPEN return-path failures and compare the count deltas to M4.1/M4.2 behavioral evidence. Add FINISH and STOP(8) termination checkpoints, including proof that IODRAIN leaves DHEAD and HHEAD empty and that G32=F32, G268=F268 and G16=F16, with open/close counts balanced on successful paths. Termination checks must execute *after* IODRAIN; pre-FINISH BCPL test 139 does not prove handle reclamation.

**M4.3 CLOSE:** Record the MVS job IDs, Cambridge/IFOX/IEWL/GO outcomes, generated object/link isolation and count observations, identify remaining host-level limitations, then accept only after all supported paths are proven. The owner's full regression deferral, M4.4 compatibility, M5 per-DD attribution and no OBJ promotion remain unchanged.

## First targeted operator check (no full regression)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-bcplio-m43-account.py
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 139 --show-output
```

DO NOT claim any PASS for 139 until the above actually executes under MVS.
