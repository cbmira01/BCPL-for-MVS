# BCPLIO dynamic streams — M4.2 QSAM OPEN failure characterization

**Status: M4.2 CLOSED (scoped return-to-caller failure contract, 2026-10-17); regression 138 PASS; jobs 7874/7875/7876 returned handles; genuine failed SVC19 unobserved; M4.3 accounting and full-panel sweep remain pending.**
Date: 2026-10-17
Predecessor: **M4.1 CLOSED**, individual 135/136/137 targeted PASS.
Full native regression panel explicitly deferred by owner (last completed
panel 00..132: 132 PASS / 0 FAIL / expected SKIP 083).

## Governing M4.2 acceptance revision — approved 2026-10-17

**Decision: M4.2 CLOSED on the explicitly bounded return-to-caller
recovery contract.** This is the current acceptance ruling and **supersedes**
the original actual-failing-SVC19 exit requirement and later historical
"must remain open" notes below. Earlier observations and rejected
experiments are retained for traceability, not as active marching orders.

The BCPL application sees character streams, not DCBs or QSAM records.
The programmer's JCL/dataset setup must provide suitable DD allocations;
MVS validates, opens and performs record I/O. BCPLIO translates the
supported record shape to BCPL's stream contract and handles errors
that actually return control to it. BCPLIO need not intercept S013
or other unrecovered MVS abends, repair bad JCL, or guarantee that
every host OPEN failure is nonfatal. BCPLIO must still manage its own
DCBs, record buffers, descriptors, stable handles and cleanup paths.

The scoped acceptance evidence is:

| Gate | Evidence | Disposition |
|---|---|---|
| Ordinary name/allocation failure | Compiled-BCPL 134 targeted PASS | Accepted: zero FIND and unchanged selection/cursor |
| Storage-allocation branches | Compiled-BCPL 135/136/137 individually PASS (private synthetic GETMAIN failures) | Accepted branch behavior; **not** exact free counts |
| OPEN failure return branch | Compiled-BCPL 138 targeted PASS (private DQOPEN denial **before** SVC19) | Accepted: zero FIND, selected DD01 intact, later DD02 retry works |
| Real QSAM OPEN explorations | JOB 7874/7875/7876: all HANDLE, GO RC0000 | Characterized; **no** unsuccessful SVC19 observed or inferred |

Canonical assembler inspection shows `DIFIND`/`DQFIND`
taking `DIFCLEAN`/`DFFCLEAN` to `DREL` when `DQOPEN`
returns failure, without closing an unopened descriptor.
When HNEW fails **after** successful OPEN, the source first
invokes `DQCLOSE`, then `DREL`. These source paths and
the focused behavioral tests meet **M4.2's scoped exit**.
They are **not** independent instrumentation proving balanced
FREEMAINs, CLOSE counts, or the MVS 3.8J interpretation of
post-SVC19 DCB state. Those claims are explicitly reserved for M4.3.

The current supported logical dataset contract is documented in
[BCPLIO JCL and QSAM stream contract](BCPLIO-JCL-QSAM-stream-contract.md):
fixed-text 80-byte input translation and fixed 132-byte output
recordization; no blanket promise to accept variable/binary/PDS
or other QSAM formats. A suspected mismatch does not prove
the actual merged DCB attributes, nor does a returned handle
prove that a GET or PUT would succeed.

**What is closed:** M4.2's design and branch-behavior acceptance.
**What is not closed:** M4.3 exact resource accounting, M4.4
full compatibility regression (still owner-deferred), M5 physical
DD attribution, overall stream milestone, and any claim that a
real unsuccessful SVC19 was observed. No new MVS job, native
assembler change, installed DEVOBJ/OBJ change or OBJ promotion
is required/claimed for this documentary acceptance.

---

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
[probes/m42-real-open/README.md](../../native-compiler/probes/m42-real-open/README.md).

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

The `compile-mvs` command submits its **ordinary Cambridge compilation**
job to MVS. The subsequent JCL generator produces the potentially
abending GO deck **without submitting it**. **Review the
`workarea/m42-real-open/real-open.jcl` deck** before
the separate, potentially abending submission described
in the probe README. Preserve JES job number, all step CCs,
full report, IEC/IEF lines and exact ABEND reason. A
GO-step abend is a diagnostic outcome, not a regression PASS.
A zero FIND return alone does not prove SVC19 executed,
since `DDVERIFY` can fail earlier. No real SVC19 outcome
is claimed before operator evidence is supplied.

## Original exit criteria (superseded by governing 2026-10-17 revision)

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

## M4.2.1 prepared deck checkpoint — Cambridge JOB 7873

The operator fast-forwarded the repository from `5c890d3`
through `ab44dad`, compiled `native-compiler/probes/m42-real-open/source.bcpl`
with `tools/native/compile-mvs`, and reported:

```text
JOB 7873
saved Cambridge CODE: workarea/m42-real-open/generated.s370.asm
Prepared DEVOBJ runtime PDS regression: workarea/m42-real-open/real-open.jcl.base
Prepared non-submitting real-OPEN exploratory deck:
workarea/m42-real-open/real-open.jcl
DD01=DATA; DD02=SYSOUT; FINDINPUT(DD02) may ABEND.
No JES submission and no MVS PDS modifications occurred.
```

**ACCEPTED PREPARATION ONLY.** Cambridge JOB 7873 produced the
recovered assembler; it was not the experimental GO job.
The temporary base JCL was prepared and transformed into
the local `real-open.jcl` deck. Its **RG890R**
assemble/link/GO job has not been submitted, and there is
no real OPEN/IEC/IEF/ABEND evidence yet. The user-provided
log confirms generator completion but does not expose the
contents of the locally generated deck; do not assert its
line-by-line contents have been reviewed.

The next operation is an **explicitly exploratory,
potentially abending GO submission** against the unchanged
DEVOBJ(BCPLM6 + BCPLIO) candidate. Preserve the actual
JES job number and complete report. Full native regression
remains owner-deferred. Source and JCL generation are
repeatable from version-controlled inputs.

## M4.2.1 exploratory GO execution — JOB 7874 (2026-10-17)

The operator submitted the previously prepared
`workarea/m42-real-open/real-open.jcl` (source compiled
in Cambridge JOB 7873). The submission was recognized
as `RG890R`, **JOB 7874**. The operator's
`tools/mvs/job-summary 7874` output was:

```text
JOB 7874  RG890R
BCPL PDS REG
17 OCT 26  05.27.40 - 05.27.40

STEP       PROGRAM      RESULT
ASMAP      IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         PGM=*.DD     RC=0000

JOB RESULT: SUCCESS
HIGHEST RC: 0000

Assembler:
  Statements flagged: 0
  Highest severity:   0

Resources:
  Cards:     271
  SYSOUT:    489 records
```

The operator also redirected the complete job report into
`workarea/m42-real-open/real-open-report.txt`, but the
report's contents **were not supplied**. **Execution
outcome established:** the job ran and completed normally,
without an S013 or other step abend reported by the
job summary. The assembler and linker both returned 0000.

**OPEN-path attribution remains unresolved** until the
report is examined for the BCPL markers and IEC/IEF messages.
In particular, the normal GO completion cannot distinguish:
(1) early zero return at `DDVERIFY` / RDJFCB before SVC19,
(2) DQOPEN's SVC19 leaving a DCB unopened and returning 8,
or (3) an unexpectedly successful handle. The last case
should emit `M42 DD02 RETURNED HANDLE`; a zero result
should emit `M42 DD02 RETURNED ZERO`. The program also
emits `M42 BEFORE FIND DD02` and, when it survives to the
end, `M42 SURVIVED FIND DD02`. These strings must be
confirmed from the actual report, not inferred from RC0000.

**Next:** obtain the already-created
`real-open-report.txt` as an attachment, analyze its
program output and JES/IEC/IEF messages, then decide
whether a narrowly instrumented RDJFCB/SVC19 tracing
probe is required. Do not request re-running the
full native regression panel or source-only checks on
the operator's workstation. No new installed PDS
changes are implied by this execution.

## M4.2.1 JOB 7874 — full report disposition

The operator subsequently supplied the complete extracted
`real-open-report.txt`. It confirms:

```text
//DD01     DD DATA,DLM=X0
//DD02     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
IEF237I JES2 ALLOCATED TO DD01
IEF237I JES2 ALLOCATED TO DD02
IEW0000     INCLUDE OBJ(BCPLM6)
IEW0000     INCLUDE OBJ(BCPLIO)
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

`ASMAP`, `LKED`, `GO` each returned `RC=0000`.
No IEC OPEN error or abend is reported. The full report
shows `OBJ` and `DEVOBJ` DD statements both resolving
to `HERC02.BCPL.NATIVE.DEVOBJ`; the linked `BCPLIO`
was the installed unmodified development object, **not**
the isolated synthetic fault module.

**Disposition: unexpected OPEN acceptance, not failure.**
`FINDINPUT("DD02")` returned a nonzero stable handle.
In the canonical `DIFIND` path, that outcome requires
successful `DDVERIFY`, `DALLOC`, `DQOPEN` and
`HNEW`; `DQOPEN` invokes SVC 19 and checks
DCB-derived open state. Thus the report and
source together support a reached, apparently successful
real OPEN rather than an earlier RDJFCB denial or a
recoverable failed SVC 19.

The probe deliberately **does not GET** from the returned
SYSOUT-backed DD, so actual ability to read from that
stream remains unknown. More importantly, this experiment
did **not** satisfy the required actual failed-OPEN
gate. Do not close M4.2 or generalize SYSOUT/input
behavior to all datasets and MVS versions.

The next candidate is a QSAM input OPEN against an
allocated **partitioned dataset without a member**, such
as `SYS1.MACLIB` with `DISP=SHR`, whose DSORG differs
from the BCPLIO private DCB's `DSORG=PS,MACRF=GM`.
The behavior under TK5 is still to be observed; an
abend is possible. This candidate must be a separate
exploratory GO job, never a normal PASS regression,
and must not write to SYS1.MACLIB.

## M4.2.2 — nonmember-PDS OPEN attempt STAGED

The next separately numbered **exploratory** job,
`RG891R`, is generated by
`tools/checks/prepare-m42-pds-open-jcl.py`.
The generator reuses the already available Cambridge
assembler `workarea/m42-real-open/generated.s370.asm`
from JOB 7873, recompiling no BCPL, and regenerates
a normal DEVOBJ BCPLM6+BCPLIO link job. There are no
test-only GETMAIN/DQOPEN faults in this job.

This candidate allocates `DD01` as known DATA
and `DD02 DD DSN=SYS1.MACLIB,DISP=SHR` — a
read-only PDS **without a member selection**. The
same BCPL application calls `FINDINPUT("DD02")`,
prints whether FIND returned zero or a handle,
verifies DD01 stayed usable, and never calls RDCH
on an unexpected DD02 handle. The PDS is not edited.

Rationale: SYSOUT was apparently accepted as an input
OPEN under MVS 3.8J in JOB 7874. A PDS without a
member presents a different allocation/organization
case; modern IBM QSAM documentation describes a
PDS without a specified member as an error condition
(see https://www.ibm.com/docs/en/z-netview/6.5.0?topic=syntax-pipe-qsam).
**That documentation does not guarantee an error
under TK5.** DDVERIFY could reject the allocation
before SVC19, DQOPEN could reject it, the host could
abend, or a handle could still be returned. The
intentional probe logs whichever behavior actually
occurs and is not a regression PASS/FAIL test.

[Complete operator procedure](../../native-compiler/probes/m42-pds-open/README.md)
keeps the JCL-building command separate from the
possibly abending GO submission. Only assembler/link
JCL is generated; no MVS job, Python static checker,
or full regression is requested during preparation.

**STAGED, NOT EXECUTED.** No new MVS result,
assembler return code, diagnostic or OPEN failure is
yet available. The owner's deferral of full native
regression remains in effect.

## M4.2.2 operator preparation accepted — RG891R JCL generated

On 17 October 2026, the operator fast-forwarded the repository
from `ab44dad` through `3235115` and ran the development-only
`prepare-m42-pds-open-jcl.py` generator with the four required
DEVOBJ/BCPLM6 candidate variables. Output:

```text
Prepared DEVOBJ runtime PDS regression:
workarea/m42-real-open/pds-open.jcl.base
Prepared M4.2.2 read-only PDS QSAM OPEN exploratory deck:
workarea/m42-real-open/pds-open.jcl
RG891R: DD01=DATA; DD02=SYS1.MACLIB,DISP=SHR (no member)
The GO job was NOT submitted; no PDS object was modified.
```

**Preparation accepted, exploratory execution pending.**
The builder reused the already compiled Cambridge application
from JOB 7873; it generated a new non-submitting `RG891R`
assembler/link/GO deck, allocating DD02 to read-only
`SYS1.MACLIB` with no member. This is an experiment, **not**
registered regression 891. The operator output does not
include the generated card deck for line-by-line inspection,
nor any JES job number or MVS GO execution for RG891R.

On submission, preserve the job summary and complete
`workarea/m42-real-open/pds-open-report.txt`, including
IEF/IEC/ABEND messages. An actual unsuccessful SVC19 is
not yet established. The owner-deferred full regression
panel and prohibition on object promotion remain unchanged.

## M4.2.2 RG891R exploratory JOB 7875 — execution result

On 17 October 2026 the operator submitted the previously
prepared `workarea/m42-real-open/pds-open.jcl`, using
`DD02 DD DSN=SYS1.MACLIB,DISP=SHR` without a member
and the ordinary DEVOBJ/BCPLM6 runtime link. JES assigned
**JOB 7875**, `RG891R`. The operator reported:

```text
JOB 7875  RG891R
17 OCT 26  05.42.27 - 05.42.27
ASMAP      IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         PGM=*.DD     RC=0000

JOB RESULT: SUCCESS
HIGHEST RC: 0000
Assembler: Statements flagged 0; highest severity 0
Resources: 271 cards; 502 SYSOUT records
```

The task did **not** report an S013 or another GO abend.
The extracted JES report was saved to
`workarea/m42-real-open/pds-open-report.txt`, but its
contents have **not yet been supplied**. The GO RC0000
does **not** establish what `FINDINPUT("DD02")` returned
and does not prove whether the actual QSAM OPEN was
attempted or rejected. Inspect the report for
`M42 BEFORE FIND DD02`, `M42 DD02 RETURNED ZERO`,
`M42 DD02 RETURNED HANDLE`,
`M42 SURVIVED FIND DD02`, and any IEC/IEF messages.

**Disposition: completed exploratory execution; outcome of
OPEN still uncharacterized.** Neither M4.2.2 nor the
M4.2 real OPEN-failure gate can be closed on this summary
alone. Do not request new workstation checks, recompilation,
or a full native regression panel. The full-panel deferral
and no object-promotion policy remain in force.

## M4.2.2 JOB 7875 — full JES report accepted

The operator supplied the complete `pds-open-report.txt`
for exploratory job `RG891R`, JOB 7875 (17 October 2026).
The actual GO JCL and allocation evidence included:

```text
//DD02     DD DSN=SYS1.MACLIB,DISP=SHR
IEF237I 390  ALLOCATED TO DD02
IEF285I   SYS1.MACLIB   KEPT
IEW0000     INCLUDE OBJ(BCPLM6)
IEW0000     INCLUDE OBJ(BCPLIO)
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

ASMAP, LKED and GO completed `RC0000`. There was
no reported IEC OPEN diagnostic or abend. The GO
step's EXCP/device I/O accounting includes one I/O
on device 390, but does not prove a BCPL GET operation.
The BCPL source intentionally **never calls RDCH**
on this returned DD02 handle. Therefore it is not
evidence that a nonmember PDS is readable using
QSAM GET.

**Source-guided interpretation:** DIFIND can only
return a new handle after DDVERIFY, DALLOC, DQOPEN
and HNEW success. DQOPEN executes real SVC19 and
checks DCB-derived open state. Thus this was an
apparently successful real OPEN, **not a failed OPEN**,
just as JOB 7874 returned a handle for a SYSOUT DD.
The intended M4.2 actual unsuccessful OPEN gate
remains **NOT MET**; the test is exploratory, not
a regression PASS.

The next candidate should target an actual *OPEN-time
validation* fault, not merely a suspicious allocation.
A documented S013-20 situation is an FB QSAM DCB whose
BLKSIZE is not a multiple of LRECL. Consider a
separate, strictly read-only/temporary-data-set
exploratory GO job using deliberate
`RECFM=FB,LRECL=80,BLKSIZE=81`. JCL allocation
may reject it before SVC19 or MVS may ABEND; neither
outcome may be assumed. No full regression suite
or installed runtime changes are authorized.

## M4.2.3 — intentionally invalid FB DCB probe STAGED

Previous exploratory attempts did not fail at QSAM OPEN:
JOB 7874 (`DD02 SYSOUT=*`) and JOB 7875
(`DD02 SYS1.MACLIB,DISP=SHR` with no member)
**both returned a valid FINDINPUT handle**. The
application did not read DD02 in either case.

New candidate **RG892R** targets an independent
OPEN-time DCB consistency rule instead of relying
on the DD name or PDS organization. Its JCL
deliberately supplies:

```jcl
//DD02     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)
```

For QSAM RECFM=FB, the BLKSIZE must be a multiple
of LRECL; `81 mod 80 = 1`. The classic S013-20
diagnostic covers such a mismatch, but JCL may
reject the allocation first or MVS may behave
differently with SYSOUT input. **Do not claim that
this probe is guaranteed to reach SVC19 or abend.**

A dedicated, **non-submitting** and fail-closed
JCL builder is committed at
`tools/checks/prepare-m42-fb-open-jcl.py`.
It builds a base application link from the
already generated Cambridge assembler from JOB 7873,
with normal DEVOBJ BCPLM6+BCPLIO objects (not
instrumented test-only objects), and inserts
the one bad-DCB SYSOUT DD02 and an exploratory banner.
The builder checks job identity RG892R, exact
GO/DD anchors, duplicate DD detection, candidate
environment and 71-column JCL card safety.
It does not alter the canonical assembler,
installed PDS members or system DASD.

[Operator preparation and separately documented
submission](../../native-compiler/probes/m42-fb-open/README.md)
are staged but **no RG892R GO JCL or MVS result
has yet been produced**. Do not ask the operator
to run host-side source checks or the full regression.
If a system abend occurs, preserve full JES/IEC/IEF
diagnostics and do not call it a normal regression PASS.

This probe is only an incremental M4.2.3 experiment;
M4.3 accounting and M5 DD attribution remain separate.

## M4.2.3 RG892R JCL preparation verified by operator

The operator pulled through `19e658a` and ran the
non-submitting, development-only FB JCL builder against
existing Cambridge assembler from JOB 7873. It created:

```text
workarea/m42-real-open/fb-open.jcl
RG892R: DD02 SYSOUT,RECFM=FB,LRECL=80,BLKSIZE=81
INVALID: 81 is not divisible by 80; JES or OPEN may reject
GO job NOT submitted. No installed PDS member changed.
```

**PREPARATION ACCEPTED, MVS EXECUTION PENDING.** The builder
reports that RG892R GO was not submitted. The actual generated
local deck has not been pasted for independent line-by-line
review; the reported DD attributes and success of the guarded
generator are the evidence currently available. S013-20, JCL
rejection, a nonzero handle and a failed SVC19 remain possible
outcomes, not established facts. Continue with a single
exploratory submission and capture complete JES/IEC/IEF output.
M4.2 stays open, full regression deferred, no object promotion.

## M4.2.3 JOB 7876 — malformed FB JCL DCB accepted, HANDLE returned

Received operator's complete `RG892R` JOB 7876
JES report (17 October 2026, 05.50.01).
Actual GO JCL includes:

```jcl
//DD02     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)
```

The GO step received `IEF237I JES2 ALLOCATED TO
DD02`. The linker included the normal development
`BCPLM6` and `BCPLIO` objects, not a fault
injection. ASMAP/LKED/GO were each `RC=0000`,
with no reported IEC OPEN diagnostic or system
abend. BCPL output was:

```text
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

This **does not** prove that the post-OPEN DCB
actually retained RECFM=FB/LRECL=80/BLKSIZE=81,
nor that a GET would work. The application does
not GET from DD02. Canonical DIFIND returns a
nonzero new handle only after DDVERIFY succeeds,
DALLOC constructs the descriptor, DQOPEN executes
real SVC19 and observes apparently open DCB
state, and HNEW succeeds. Thus the attempted
malformed JCL DCB did **not** trigger a recoverable
or abending QSAM OPEN failure here.

### M4.2 technical course correction

Three actual allocated-DD attempts had the same result:
**JOB 7874** SYSOUT as input: HANDLE;
**JOB 7875** read-only nonmember PDS: HANDLE;
**JOB 7876** SYSOUT FB `80/81`: HANDLE.

The crucial implementation fact is that DALLOC
copies a `DQTIN` template into a 96-byte private
DCB at owned-region offset +132; `DQTIN` itself
declares `DSORG=PS,MACRF=GM,EODAD=INDYEOD`
**without explicit LRECL, BLKSIZE or RECFM**.
MVS merges those attributes at OPEN from whatever
applicable sources it accepts. We have not yet
measured the effective merged bytes. Merely
varying a JCL DD is not enough to establish
which in-memory DCB fields SVC19 validated.

**Next design gate (not executed):** a development-only,
source-generated disposable BCPLIO object, with
diagnostics immediately before and after the real
SVC19 in DQOPEN for **DD02 only**, observing the
DCB RECFM/LRECL/BLKSIZE and open-state. Verify
DCB field offsets against contemporary OS/VS2
DCBD macro or IFOX macro expansion **before**
writing to any byte. Keep DD01 unchanged as
a control and keep compiled BCPL marker output.
Only then consider a private, DD02-only invalid
DCB patch that reaches the real OPEN call and
may abend. An abend is a diagnostic, **never**
a native-regression PASS. Do not change
production BCPLIO, installed DEVOBJ/OBJ,
G-slot ABI, full-panel deferral or resource
accounting scope.

**M4.2's actual failed-OPEN acceptance remains OPEN.**
No new operator job is requested at this stage;
the next work is repository-side DCB verification
and design, not speculative JCL reruns.

## Release 3.8 IBM manual: SYSOUT/PR DCB normalization

Read the **period-correct** `OS/VS2 MVS Data Management
Services Guide`, `GC26-3875-0`, Release 3.8,
revised June 29, 1979, page **86** (PDF page 104,
zero-index page 103):

https://bitsavers.trailing-edge.com/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3875-0_OS_VS2_MVS_Data_Management_Services_Guide_Rel_3.8_Jun79.pdf

Under its printer-device section it specifies that
QSAM **RECFM=FB printer data sets** have their
DCB block size **adjusted to equal LRECL** and
are treated as RECFM=F. The same statement appears
for card punch data sets. This contemporaneous rule
is a plausible reason the intentionally malformed
`DD02 SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)`
in JOB 7876 did not fail at OPEN: JES SYSOUT
may have taken a printer-style path that rewrote
or normalized the effective DCB values.

**Do not overstate this inference.** The failed-OPEN
attempt had `DD02 SYSOUT=*`, but we did not capture
effective DCB RECFM/BLKSIZE/LRECL immediately before
or after SVC19, and the actual JES output class and
device-specific mapping to the documented PR case
were not independently measured. We therefore
cannot claim that DCBBLKSI was definitely corrected
in this exact run. It is a historically supported
hypothesis which should guide the next experiment.

Source review of canonical `native-compiler/asm/bcplio.asm`
reveals the actual diagnostic ownership and location:
- `DALLOC` obtains 32-byte descriptor plus 268-byte area.
- The QSAM DCB occupies **96 bytes at area +132**,
  copied from `DQTIN`; DDNAME is installed at DCB+40.
- The source `DQTIN` macro declares `DSORG=PS`,
  `MACRF=GM`, `EODAD=INDYEOD`; it does **not**
  specify `RECFM`, `LRECL`, or `BLKSIZE`.
- The 4-byte SVC19 parameter list is at area +228;
  `DQOPEN` issues `SVC 19` and probes the
  DCB-derived word at offset DCB+48 afterward.
- `DDVERIFY` first performs RDJFCB using a
  separate scratch DCB, but its success does not
  validate effective post-OPEN record-format semantics.
- `DIFIND` only allocates the stable handle after
  DQOPEN returns success.

**Next source-only gate:** verify historical `DCBD`
macro field labels/offsets from the actual MVS 3.8
`SYS1.MACLIB` macro and IFOX expansions, then
construct a private, disposable instrumented BCPLIO
that records DD02's effective DCB fields just before
and just after real SVC19. DD01 must remain the
unmodified control. Choose a harmless sequential
DASD dataset/record-format mismatch for a subsequent
true negative OPEN probe **only after** this data
is understood. No additional workstation checks
or JCL runs are presently requested.

This procedure avoids repeating speculative
SYSOUT and PDS JCL variants, and preserves the
owner's deferral of the complete native regression
panel, M4.3 separate resource accounting, and
unchanged installed runtime modules.

### Historical DCBD technique — verified from the same manual

Page **53** (PDF zero-index page **66**) of the same
1979 IBM Release 3.8 `GC26-3875-0` manual,
under *Modifying the Data Control Block*,
specifies the correct symbolic method:

- Use `DCBD DSORG=PS` to generate the
  `IHADCB` DSECT field mapping. The manual
  explicitly names the block-size field
  `DCBBLKSI`; related names `DCBLRECL`
  and `DCBRECFM` must be confirmed in the
  actual macro expansion before use.
- Load a base register with the actual
  in-storage DCB address, then refer to
  DCB fields symbolically using `IHADCB`.
- `DCBD` is coded **once** per assembly;
  it creates a DSECT and must be followed
  by a CSECT/DSECT statement if the original
  section is to resume.
- The manual cautions that fields are not
  always fullword-aligned; use the **assembly
  listing** to determine field length and
  alignment. Do not guess numerical offsets.

These instructions are contemporaneous with MVS 3.8
and directly applicable to building a disposable
M4.2 DCB introspection probe. It remains necessary
to validate actual IFOX/SYS1.MACLIB expansion
before claiming the probe is assemblable. This
is **source-study evidence only**; no assembler
job or field observation is claimed.
