# BCPLIO dynamic streams — M4.2 QSAM OPEN failure characterization

**Status: 138 synthetic DQOPEN recovery ACCEPTED; M4.2.1 allocated-DD true-OPEN exploratory probe STAGED (not run); full panel owner-deferred.**
Date: 2026-10-17
Predecessor: **M4.1 CLOSED**, individual 135/136/137 targeted PASS.
Full native regression panel explicitly deferred by owner (last completed
panel 00..132: 132 PASS / 0 FAIL / expected SKIP 083).

## Scope and non-goals

M4.2 asks what occurs when an ordinary, allocated MVS DD is
incompatible with BCPLIO's requested QSAM OPEN, and whether
BCPLIO can return a zero stream handle without leaking a
partially built descriptor. A failed JCL DD allocation,
an RDJFCB lookup failure, a deliberately denied DQOPEN
call and a **real failing MVS SVC 19** are four distinct
conditions. We must not use one as evidence of another.

Do not change G numbers, canonical BCPLIO, installed
`DEVOBJ`, production `OBJ`, or the existing stream
records/handle contract merely to produce a negative result.

## Canonical code inspection

`native-compiler/asm/bcplio.asm` currently uses the
following path (assembler source, not yet failure-probe evidence):

1. `DIFIND` / `DQFIND`: normalize DD name, search
   for already-open identity, and `DDVERIFY` with RDJFCB.
2. `DALLOC`: acquire 32-byte descriptor and 268-byte
   region and construct input/output QSAM DCB.
3. `DQOPEN`: SVC 19 using private parameter list,
   then consult DCB-derived state (`L 7,48(7)`);
   return zero on apparent success or 8 on failure.
4. If DQOPEN returns nonzero, `DIFCLEAN` /
   `DFFCLEAN` calls `DREL` (without DQCLOSE),
   expected when there is no opened DCB.
5. Successful OPEN followed by HNEW handle allocation
   failure takes `DQCLOSE` then `DREL`; covered
   behaviorally by M4.1 regression 137.
6. `DQCLOSE` issues SVC 20, clears the descriptor's
   open-state field, and is not invoked on ordinary DQOPEN
   failure paths.

An MVS OPEN can return with an unopened DCB or can abend
with an x13 system completion code, including S013. IBM's
later z/OS OPEN documentation describes the DCB OPEN flag
as a way to detect success, but it is **not evidence that
this specific `L 7,48(7)` sequence and every failure
case work identically in MVS 3.8J**. A contemporary
OS/370 System Messages reference and actual TK5 JES
trace should arbitrate observed cases.

Reference starting points (not substituted for TK5 execution):
- https://www.ibm.com/docs/en/zos/3.2.0?topic=nvmd-open-connect-program-data-bdam-bisam-interface-vsam-bpam-bsam-qisam-interface-vsam-qsam
- https://bitsavers.org/pdf/ibm/370/MVS/GC28-1375-1_MVS_370_Message_Library_System_Messages_Volume_2_IEC-ISG_Jan85.pdf

## M4.2.0 — isolated negative DQOPEN return (regression 138)

A **test-only**, temporary source transform:
`tools/checks/prepare-bcplio-m42-open.py`.

It replaces only the unique BCPLIO DQOPEN SVC19 site.
The first call (DD01) executes true SVC19, the second
call (DD02) **returns R15=8 via DQBAD before any SVC19**,
and the third retry DD02 executes true SVC19. On denied
OPEN, descriptor +24 remains zero and DIFCLEAN frees
the descriptor and region through DREL.

Permanent compiled-BCPL case:
`native-compiler/regression/138-dynamic-dd-open-denial-before-svc19/`.
It checks failed FIND returned zero, DD01 selection/cursor
unchanged, retry DD02 successful, read/close of both streams.
The expected primary marker is `BCPL OPEN BRANCH OK`.

JCL compiles the application normally, inline-assembles
the test-only modified BCPLIO in ASMFIO into `&&IOOBJ`,
omits the installed DEVOBJ(BCPLIO) INCLUDE for **this
marked case only**, and links all other normal installed
candidate objects. No PDS member is overwritten.

**Evidence boundary:** PASS 138 would validate BCPLIO cleanup
and retry *when DQOPEN returns 8*, not actual MVS SVC19 error
status, S013 abend or system messages. It cannot close M4.2.

### First operator gate (focused only)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-bcplio-m42-open.py
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 138 --show-output
```

Expected source transform audit PASS and, only after MVS execution,
`PASS 138` with `BCPL OPEN BRANCH OK`. If assembler or
link step fails, first triage private instrumentation and
preserve exact JES CC/job evidence.

## M4.2.1 — actual incompatible allocated DD exploratory job

**PROBE STAGED, NOT YET BUILT OR EXECUTED UNDER MVS.** This uses a separate,
fail-closed experimental JCL deck with a DD for which
`RDJFCB` succeeds but the requested QSAM input/output
DCB attributes or mode cannot be satisfied. Possible
mismatches include a SYSOUT allocation requested for
input or incompatible sequential dataset DCB attributes;
**which combinations are admitted by JES and how OPEN
reacts under TK5 must first be checked, not assumed**.

A real exploratory job must report:
- JCL DD allocation and RDJFCB evidence.
- Whether SVC19 returned or the GO task terminated/abended.
- Actual IEC/IEF, ABEND completion and DDNAME, if any.
- Whether DCB was opened, whether a BCPL handle was produced,
  and whether previously selected streams remained usable.
- Resource cleanup only if the problem program retained
  control; a system abend cannot be counted as graceful
  failed FIND.
- An exact distinction between expected-abend diagnostic
  evidence and a successfully handled error.

Do not turn an abending exploratory job into a normal
regression PASS merely because the abend was anticipated.
M4.3 must independently instrument CLOSE/FREEMAIN
accounting and likely verify DCB open-state interpretation.

## M4.2.1 source and JCL preparation — STAGED, NOT EXECUTED

A separate, non-regression diagnostic program is now committed
at `native-compiler/probes/m42-real-open/`. It compiles with the
historical Cambridge compiler and links the **unmodified
installed** `DEVOBJ(BCPLM6)` and `DEVOBJ(BCPLIO)`
candidate objects. No synthetic DQOPEN bypass or SVC19
interceptor is present.

The GO step intentionally allocates `DD01` as ordinary
instream DATA and `DD02` as `SYSOUT=*` with FB132
DCB attributes. BCPL opens DD01 normally, flushes a
diagnostic marker, and executes `FINDINPUT("DD02")`.
Thus DD02 is JCL allocated but its intended SYSOUT
direction is incompatible with the BCPL application's
requested QSAM input. **It is not yet known whether
RDJFCB rejects the DD first, whether the SVC 19 request
returns unopened, or whether TK5 abends.** The
experiment is designed to distinguish those outcomes
when combined with actual JES/IEC/IEF evidence.

`tools/checks/prepare-m42-real-open-jcl.py` creates
the exploratory `RG890R` assembler/link/GO JCL from
compiler-generated assembler using the existing
`prepare-runtime-pds-regression.py` for base structure.
It checks all relevant JCL anchors, requires the
DEVOBJ/BCPLM6 candidate environment, inserts exactly one
`//DD02 DD SYSOUT=*`, and **never submits** a job.
The host-only checker
`tools/checks/check-m42-real-open-jcl.py`
validates the patcher with both correct and deliberately
corrupted JCL fixture text. This checker **has not yet
been executed**.

The probe has its own source and instructions:
[probes/m42-real-open/README.md](../native-compiler/probes/m42-real-open/README.md).

### Operator commands — prepare, inspect, then optionally submit

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-m42-real-open-jcl.py

python3 tools/native/compile-mvs \
  native-compiler/probes/m42-real-open/source.bcpl \
  --job-name RG890C --listing light --timeout 180 \
  --output workarea/m42-real-open/generated.s370.asm

BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
python3 tools/checks/prepare-m42-real-open-jcl.py \
  workarea/m42-real-open/generated.s370.asm \
  workarea/m42-real-open/real-open.jcl
```

These commands produce the controlled diagnostic deck
without submitting its GO step. **Review the
`workarea/m42-real-open/real-open.jcl` deck** before
the separate, potentially abending submission described
in the probe README. Preserve JES job number, all step CCs,
full report, IEC/IEF lines and exact ABEND reason. A
GO-step abend is a diagnostic outcome, not a regression PASS.
A zero FIND return alone does not prove SVC19 executed,
since `DDVERIFY` can fail earlier. No real SVC19 outcome
is claimed before operator evidence is supplied.

## Exit criteria

M4.2 can close only after documented TK5 evidence for at
least one **actual** incompatible allocated-DD OPEN attempt,
a characterized and accurate outcome (recoverable failure
or host abend), and corresponding scope-limited cleanup
contract. If recovering every host OPEN abend would
require ESTAE/recovery design outside the milestone, record
that explicitly as a limitation rather than silently
claiming nonfatal behavior.

The owner's deferral of the full regression panel remains
in effect throughout this characterization. No DEVOBJ-to-OBJ
promotion is authorized.

## M4.2.0 accepted — focused regression 138 (2026-10-17)

The operator fast-forwarded `main` from `ccb0f1b` through
`5c890d3`, then executed the host-side
`check-bcplio-m42-open.py`, which reported:

```text
M4.2 synthetic OPEN source-only checks: PASS
M4.2 actual MVS OPEN failure: NOT TESTED
```

The operator subsequently ran the isolated BCPLIO
`138-dynamic-dd-open-denial-before-svc19` regression
under the standard four DEVOBJ/BCPLM6 candidate settings:

```text
NATIVE REGRESSION  138..138  (1 tests)
RUN   138  138-dynamic-dd-open-denial-before-svc19
PASS  138  138-dynamic-dd-open-denial-before-svc19

NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
SKIP  0
TOTAL 1
```

**ACCEPTED M4.2.0:** source-generated private branch denies
the second DQOPEN *before SVC 19*, returns failure, and
correctly preserves an existing stream/cursor and allows
retry/open/use/close. This is a BCPL-level behavior test
with a synthetic DQOPEN return, **not a real MVS QSAM OPEN
error**. No separate JES job number or assembler/link/GO
step RCs were provided. No installed object was changed.

M4.2 cannot close until **M4.2.1** actually attempts an
incompatible, allocated-DD OPEN under TK5 and records
JES/IEC/IEF/ABEND outcomes. Full 00..138 compatibility
continues to be deferred per owner instruction.
