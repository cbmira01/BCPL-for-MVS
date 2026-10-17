# BCPLIO dynamic streams — M4.3 resource accountability

**Status: M4.3.0, M4.3.1, M4.3.2a and M4.3.2b ACCEPTED (2026-10-17); focused 139–145 all PASS individually/in targeted groups. M4.3 formal closure awaits extraction of successful JES job IDs and per-step codes from existing local regression logs. Full panel remains owner-deferred.**
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

## Checker correction after attempted 140/141 launch (2026-10-17)

The operator pulled commit `74b0763` and tried the targeted
`140 141` invocation. The source checker stopped with
`AssertionError` at its expectation of eight `BNE M43TRAP`
references. The generated terminal assertion path contains **two**
`BNZ M43TRAP` list-nonempty checks and **six**
`BNE M43TRAP` counter-comparison checks. The assertion expected
the wrong mnemonic distribution, not an accounting failure.

The checker now verifies **2 BNZ + 6 BNE = 8** independently.
Because the invocation was chained with `&&`, **neither 140 nor
141 was submitted to JES**. No IFOX/IEWL/GO result, counter
observation or M4.3.2a acceptance is claimed. The canonical
BCPLIO and test-private instrumented assembler are unchanged.
## M4.3.2a acceptance — 2026-10-17

Operator rerun after source checker correction `04f55e0`:

```text
M4.3 post-IODRAIN terminal assertions: source check PASS
M4.3 native counter shim base setup: source check PASS
M4.3 private source accounting checks: PASS
RUN 140 140-dynamic-dd-finish-accounting
PASS 140 140-dynamic-dd-finish-accounting
RUN 141 141-dynamic-dd-stop-accounting
PASS 141 141-dynamic-dd-stop-accounting
PASS 2 / FAIL 0 / SKIP 0
```

**ACCEPTED:** In those isolated tests, after IODRAIN,
DHEAD/HHEAD were empty and the private successful 32/268/16-byte
GETMAIN/FREEMAIN and SVC19/SVC20 counters agreed. FINISH and
STOP(8) behaved according to their case expectations. The source
audit passed before submissions. The summary does not include
job IDs or individual step condition codes; independent MVS
storage-reclamation proof is not claimed. Deliberate test-only
S0C1 guards were not triggered. This is not evidence that BCPLIO
catches actual MVS abends.

**Still open:** M4.3.2b counts on synthetic failed GETMAIN
(32/268/16) and pre-SVC19 OPEN-denial cleanup/retry.
Neither full native compatibility sweep nor production
object installation is authorized by these results.

## M4.3.2a — post-IODRAIN tests 140/141 (accepted)

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

Source-only checks and targeted regression outcomes **PASS**.
Counted synthetic failure modes (M4.3.2b), the complete
compatibility panel, and production OBJ promotion remain separate.
## M4.3.2b acceptance — 2026-10-17

The operator pulled commit `ce8d3e1` and reran the source
audits and focused candidate-only 142..145 panel:

```text
M4.3 post-IODRAIN terminal assertions: source check PASS
M4.3 native counter shim base setup: source check PASS
M4.3 counted BCPL source records: <=80 columns PASS
M4.3 combined counted failure/terminal source checks: PASS
M4.3 private source accounting checks: PASS
NATIVE REGRESSION 142..145 (4 tests)
PASS 142 142-dynamic-dd-fault32-counted
PASS 143 143-dynamic-dd-fault268-counted
PASS 144 144-dynamic-dd-fault16-counted
PASS 145 145-dynamic-dd-open-denial-counted
PASS 4 / FAIL 0 / SKIP 0
```

**M4.3.2b ACCEPTED.** Each passing compiled-BCPL case
asserted ten private counter values immediately after the
single synthetic denial, another ten after the two successful
stream closes, and post-IODRAIN terminal equality and
DHEAD=HHEAD=0. Each case verified a later successful
GETMAIN or genuine SVC19 as appropriate, and retained
the source tests' original stream/cursor checks.
No claim is made that a real MVS failure returned control.

The first execution attempt at commit `5d204c3` failed
host-side before MVS because an inserted BCPL comment was
82 columns; that unsuccessful attempt remains documented
below and is superseded by this passing attempt.

**Focused M4.3 test status:** 139, 140, 141, 142, 143,
144 and 145 have all passed in their reported targeted runs;
the source audit also passed. These runs test the temporary
instrumented BCPLIO, linked with the existing development
candidate BCPLM6, rather than installing a new BCPLIO.

**Formal M4.3 closure evidence still to capture:** the
user's supplied PASS summary omits the successful-run JES
JOB IDs and individual Cambridge, IFOX, IEWL, GO step
condition codes required by the explicit M4.3 closure
contract. Those should be extracted from already-written
`workarea/native-regression/logs/139-*.log` through
`145-*.log` rather than rerunning the full panel.
The source-level and focused behavioral gates are now
complete. **Do not promote OBJ/DEVOBJ or silently
remove the owner's full-regression deferral.**
Physical MVS FREEMAIN verification and unreturned system
abends are outside the agreed scoped runtime contract.

## M4.3.2b first attempted run — no MVS execution (2026-10-17)

The operator pulled commit `5d204c3` and ran the source checker,
which passed all private BCPLIO source checks. The focused panel
142..145 then failed four times during host-side Cambridge source
preparation, each at line 19:

```text
source record exceeds 80 columns
PASS 0 / FAIL 4 / SKIP 0
```

The added BCPL comment occupied 82 columns. No IFOX/IEWL/GO
resource-accounting execution occurred, and the four failures do
not indicate a BCPLIO defect. The comments were shortened;
the M4.3 source checker now explicitly scans all four BCPL
test sources for ASCII and the 80-column limit, and confirms
20 private count assertions per case. **142..145 remain OPEN
until actual MVS results are received.**

## M4.3.2b — counted failure paths (accepted)

Regressions **142–145** combine the isolated 139 private counter
query, 140/141 post-IODRAIN terminal assertions, and the original
135–138 compiled-BCPL behavior. Only the **second** selected
operation is denied in the private assembler; the third attempt
uses the actual GETMAIN or SVC19 and must succeed.

| Test | Fault | Expected counts immediately after denial (G32/F32, G268/F268, G16/F16, OPEN attempt/success, CLOSE attempt/returned) |
|---|---|---|
| 142 | descriptor32 | 1/0, 1/0, 1/0, 1/1, 0/0 |
| 143 | buffer268 | 2/1, 1/0, 1/0, 1/1, 0/0 |
| 144 | handle16 | 2/1, 2/1, 1/0, 2/2, 1/1 |
| 145 | pre-SVC19 DQOPEN | 2/1, 2/1, 1/0, 1/1, 0/0 |

The BCPL tests also verify *after both successful stream closes*:
descriptor/buffer frees match their actual allocations,
OPEN/CLOSE counts match real SVC operations, and 16-byte
handle tombstones remain until FINISH. FINISH executes the
same private DRAINDN guard already accepted in 140/141:
all counts balanced and both lists empty.

Each new regression has **only** an `io-accounting.txt` marker,
with value `counters-fault-<mode>`; it does not use the original
`io-fault-mode.txt` or `io-open-fault.txt` to avoid
double-instrumenting BCPLIO. The marker requires a private,
separately assembled `native.asm` counter-query shim.
Existing regression 135–138 modes remain untouched.

A synthetic denied operation is **not a real MVS failure**,
and source-only checks are not IFOX or JES evidence. No
new QSAM interface, BCPL global, installed object or promoted
runtime source is introduced. Focused tests 142..145 have now **PASSED**; formal M4.3
closure evidence collection remains as specified above.

**M4.3.2 (accepted under the returned-error contract):** Add separately counted synthetic 32/268/16 and DQOPEN return-path failures and compare the count deltas to M4.1/M4.2 behavioral evidence. Add FINISH and STOP(8) termination checkpoints, including proof that IODRAIN leaves DHEAD and HHEAD empty and that G32=F32, G268=F268 and G16=F16, with open/close counts balanced on successful paths. Termination checks must execute *after* IODRAIN; pre-FINISH BCPL test 139 does not prove handle reclamation.

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
