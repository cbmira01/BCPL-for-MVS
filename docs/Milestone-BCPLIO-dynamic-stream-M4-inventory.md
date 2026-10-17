# Dynamic BCPLIO stream milestone — M4 failure/lifecycle inventory

Status: **M4.0/M4.1 accepted; M4.2.0 synthetic 138 PASS; real-OPEN diagnostic M4.2.1 staged but not run; M4.3 open; full panel deferred**
Date: 2026-10-17
Predecessor: **M2 CLOSED**, DEVOBJ native 00..132 **132 PASS / 0 FAIL / 1 expected SKIP 083**.
Parallel prerequisite: [M3 focused review](Milestone-BCPLIO-dynamic-stream-M3-review.md), regression 133 PASSED individually; full panel through 133 not yet rerun.

## Purpose

M4 demonstrates ordinary failure behavior and exact resource
ownership for dynamic streams in native BCPLIO, rather than
extending channel count or changing the historical public
BCPL G-slot ABI. The intended outputs are deterministic
error-path evidence and matching allocation/closure accounting.

## Code-path inspection: current BCPLIO

The following is a static review of
`native-compiler/asm/bcplio.asm`, **not yet instrumented
MVS evidence**.

| Routine | Observed source behavior | Remaining proof obligation |
|---|---|---|
| `IONORM` | Rejects counted-string lengths outside 1..8; folds lowercase EBCDIC; accepts the documented DD alphabet | Permanent BCPL-level invalid/overlength/empty DD tests without selection changes |
| `DDVERIFY` | Uses RDJFCB on a private scratch DCB, returns failure when R15 nonzero | Distinguish unallocated DD from allocated DD with incompatible DCB/OPEN |
| `DALLOC` | Conditional GETMAIN 32-byte descriptor then 268-byte QSAM region; frees 32 bytes if second request fails; links DHEAD only after successful allocation | Inject failure at each allocation and prove no leaked descriptor or registered partial node |
| `HNEW` | Conditional GETMAIN 16-byte stable handle, links HHEAD on success | Inject failure after successful QSAM OPEN, verify CLOSE + DREL and unchanged selection |
| `DQOPEN` | SVC 19 then checks DCB-derived pointer/open state; sets descriptor +24 on success | Establish precise host behavior for incompatible DD, unsuccessful OPEN, SVC diagnostics and cleanup |
| `DQFIND` / `DIFIND` | Normalize; reuse live identity; RDJFCB; allocate; OPEN; allocate handle; release on failure | Verify every failure branch without abends or selection damage where ordinary failure is recoverable |
| `DQCLOSE` | SVC 20 on live DCB, then clears fullword +24; returns success | Instrument CLOSE attempt/result and confirm no double-CLOSE |
| `DREL` | Requires descriptor state closed, unlinks DHEAD, FREEMAIN 268 then 32 | Verify exact matching frees after explicit close and failure |
| `HCLOSE` | Invalidates handle +4 without releasing 16-byte identity | Show tombstones cannot be recycled during program lifetime |
| `IODRAIN` | Flushes partial output, CLOSEs and frees all live dynamic descriptors; FREEMAINs 16-byte identities at termination | Verify final counts with multiple live/retired handles and nonzero STOP |

Source comments identifying routines as “NOT WIRED” from earlier
staging may be historically stale; follow actual call sites,
not those comments, when assessing installed behavior.

## Already tested externally

- 116: unknown DD failure and selection preservation for bootstrap names.
- 124–125: dynamic unknown-name failures with selected stream preserved.
- 127: same-live-DD duplicate FIND without duplicate OPEN (previous S013-C0 fixed).
- 130: sixteen live inputs, independent EOF and reverse close.
- 131–132: fresh, nonrecycled output and input handles after close.
- 128–129: visible termination flush for FINISH and nonzero STOP.
- 113: documented overlong FB132 record STOP(12).
- Full 00..132: compatibility baseline with 132 PASS, 0 FAIL, 1 expected SKIP 083.

None of these by themselves **prove** exact SVC 19/20 counts,
GETMAIN/FREEMAIN matching, or graceful recovery from real host
OPEN errors and storage exhaustion.

## Proposed march gates in order

1. **M4.0 — ordinary negative-name validation:** permanent compiled-BCPL
   tests for empty, >8, invalid leading character, invalid embedded
   character, and unallocated valid names for both FINDINPUT
   and FINDOUTPUT. Assert zero return and unchanged selected streams.
   No runtime modification should be necessary if the current code
   fulfills its source-level contract.
2. **M4.1 — failure injection design:** development-only private
   hooks in an instrumented test build, not public BCPL globals or a
   production diagnostic interface. Inject each 32/268/16-byte
   GETMAIN failure deterministically, with exact recovery assertions.
   A bounded assembler wrapper or isolated candidate copy may be
   preferable to adding permanent branch complexity in core BCPLIO.
3. **M4.2 — incompatible allocated DD/OPEN:** design JCL-allocated
   DD that RDJFCB recognizes but QSAM OPEN cannot use with the
   requested DCB mode. Document observed IEC/IEF and SVC status;
   avoid making recoverability promises before examining MVS behavior.
4. **M4.3 — resource accountability:** count allocations and
   corresponding frees by object kind (32 descriptor, 268 QSAM,
   16 handle), and OPEN/CLOSE operations. Exercise explicit close,
   partial-allocation failure, handle creation failure, retained
   tombstones, FINISH and STOP(8). Require balanced owned resources
   at successful process termination. Instrumentation must be
   private and non-production.
5. **M4.4 — compatibility:** repeat entire DEVOBJ regression panel
   after any accepted runtime changes; preserve current 00..132
   baseline and the expected skip 083.

## Architectural restrictions

- Do not change BCPL G-numbering, native linkage, standard
  streams, DD discovery/normalization semantics or the sixteen
  stream target.
- Do not treat `workarea/` artifacts or MVS objects as
  irreplaceable source; preserve instrumented assembly
  and test recipes in the repository.
- Distinguish test-fixture errors, JCL OPEN diagnostics, true
  runtime failures and assertion STOP condition codes.
- Keep production `HERC02.BCPL.NATIVE.OBJ` untouched without
  explicit owner authorization.
- M5 physical DD attribution remains a separate acceptance gate.

**M4 has not yet been MVS executed or accepted.** Regression 133
now PASSED its focused M3 logical input/output interleaving test.
The next focused operational test is M4.0 regression 134 (below).
Failure-injection implementation must follow a concrete design/review gate.

## M4.0 — compiled-BCPL invalid-name gate 134 STAGED

Permanent DEVOBJ-only test:
`native-compiler/regression/134-dynamic-dd-invalid-name-preservation/`.
It opens real DD01 input and REPORT output, selects each, and
attempts both FINDINPUT and FINDOUTPUT of **five** invalid or
absent DDNAMEs: empty string, 9-character overlength name,
invalid leading digit, invalid embedded hyphen, and allocated-
nowhere but valid `NOFILE`. Each failure must return zero,
preserve both live selections, and leave their respective
input/output stream states intact. After the failures it
also tests lowercase duplicate FIND and RDCH cursor continuity.
The REPORT logical fixture is `NEGATIVE DD OK`, primary
SYSPRINT marker `BCPL DD FAILURES OK`.

**STAGED, NOT YET EXECUTED.** No installed DEVOBJ object or
BCPLIO source, compiler, or JCL generator was changed.
If compilation or runtime fails, retain the first diagnostic
and do not obscure it by assuming all five strings were accepted
by the historical Cambridge compiler.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 134 --show-output
```

The last full accepted panel remains 00..132:
**132 PASS / 0 FAIL / 1 expected SKIP 083**.
133 is accepted as a focused M3 PASS; a full 00..134 sweep
is reserved for after candidate test 134 passes.

## M4.0 gate acceptance — regression 134 (MVS 2026-10-17)

Following the source and fixture staging described above, the
operator pulled `main` through `3678e54` and ran
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6
tools/native/run-regression 134 --show-output`.
Reported:

```text
NATIVE REGRESSION 134..134 (1 tests)
RUN 134 134-dynamic-dd-invalid-name-preservation
PASS 134 134-dynamic-dd-invalid-name-preservation
PASS 1
FAIL 0
SKIP 0
TOTAL 1
```

**ACCEPTED:** M4.0 ordinary invalid-name/unallocated-DD
FINDINPUT/FINDOUTPUT behavior. The permanent compiled-BCPL test
checks that empty, >8-character, invalid-leading-digit,
invalid-embedded-hyphen, and unallocated `NOFILE` names all
return zero, preserve selected handles, preserve the input
cursor, and do not prevent subsequent valid duplicate FIND.
The test's success marker and REPORT logical fixture were
accepted by the combined-JES checker. It did not test actual
QSAM OPEN failures, GETMAIN exhaustion, SVC 19/20 call counts,
or exact physical REPORT DD association. No installed BCPLIO
module or candidate object changed.

The accepted full `00..132` panel remains **132 PASS /
0 FAIL / one expected SKIP 083**; the new 133 and 134
cases have both passed *individually*. They have not yet
been demonstrated together with the complete older panel.

**Next checkpoint:** complete DEVOBJ `00..134`, expected
**134 PASS, 0 FAIL, 1 expected SKIP 083, TOTAL 135**.
After a green compatibility gate, prepare an explicit isolated
fault-injection design and acceptance criteria for allocation
failures in 32-, 268- and 16-byte GETMAIN and for incompatible
QSAM OPEN before modifying any assembler. Keep instrumentation
private, rebuildable and limited to DEVOBJ or isolated probes.

## Owner decision: defer full regression, proceed to M4.1

Following focused **PASS 134**, the owner explicitly elected to
**defer** the proposed 00..134 full regression checkpoint and
continue directly to M4.1. Do not treat deferral as a failed or
completed panel and do not repeat the full-panel request as an
M4.1 precondition. Last accepted full panel remains **00..132:
132 PASS, 0 FAIL, one expected SKIP 083**. Focused regression
133 and 134 each passed independently.

## M4.1 implementation — test-only harness STAGED

[Detailed M4.1 design and test plan](Milestone-BCPLIO-dynamic-stream-M4.1-plan.md)
is now committed, together with a fail-closed source transformer
`tools/checks/prepare-bcplio-m41-fault.py`,
a marker-gated isolated assembler/link route in the native
regression runner and PDS JCL generator, and three permanent
candidate-only compiled BCPL regressions:

| Test | Forced GETMAIN failure | Expected cleanup |
|---|---|---|
| 135 | DALLOC LV=32 descriptor | no partially registered descriptor |
| 136 | DALLOC LV=268 QSAM region | free already acquired LV=32 |
| 137 | HNEW LV=16 handle after OPEN | DQCLOSE + DREL of LV=268 and 32 |

These tests synthesize nonzero R15 **on the second visit to
the chosen GETMAIN site**, allowing the first stream to remain
selected and a third allocation attempt to succeed. They do
not claim genuine host low-storage exhaustion. The private
BCPLIO object is assembled **within each GO JCL** as
`ASMFIO` and linked from `&&IOOBJ`; installed
`DEVOBJ(BCPLIO)`, `DEVOBJ(BCPLM6)` and production OBJ are
unchanged. No live MVS job, assembler result, link result or
BCPL assertion PASS has yet been supplied for cases 135–137.

**Next operator test** (single targeted case, not full suite):

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 135 --show-output
```

Require Cambridge COMP/SVCODE, IFOX ASMAP and ASMFIO,
IEWL LKED and GO normal completion with
`BCPL FAULT 32 OK`. Inspect job spool before any change
if the instrumented module has addressability/assembly issues.
Do not change canonical runtime source or promote installed
objects merely to fix test infrastructure. Then run 136 and
137 separately after validating the first case.

## M4.1 first focused gate accepted — regression 135

The operator pulled through `175fc2e` and reported
`python3 tools/checks/check-bcplio-m41-fault.py` PASS for
all three injection source modes. This is **host-side static
validation**, not MVS execution of all three cases.

The subsequent isolated compiled-native regression
`135-dynamic-dd-fault-descriptor32` completed:
**PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**. This accepts
the second-invocation synthetic failure of DALLOC
`GETMAIN RC,LV=32` and subsequent non-destructive
BCPL FINDINPUT retry. The installed DEVOBJ modules and
production OBJ remain unchanged. Neither a true MVS
low-storage condition nor independently counted FREEMAIN
or CLOSE operations has been proved.

**Next:** run focused 136 (268-byte region failure),
then 137 (16-byte handle failure after successful OPEN).
Both are staged and **not yet executed**. The full
00..134 panel remains **explicitly deferred**, with last
accepted complete suite 00..132 (132 PASS / 0 FAIL /
one expected SKIP 083).

## M4.1 268-byte failed-allocation gate accepted — regression 136

After fast-forwarding to `831ee82`, the operator ran
`tools/native/run-regression 136 --show-output` under the
isolated DEVOBJ candidate. It reported **PASS 136**, with
**PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.

The synthetic second-site `GETMAIN RC,LV=268` failure
occurred after successful acquisition of the 32-byte
descriptor. The BCPL program verified a zero return,
preservation of the selected DD01 input/cursor, a successful
subsequent DD02 open/read, and ordinary close. The source
contains the `DALNOMEM` FREEMAIN cleanup for the
32-byte descriptor, but no independent FREEMAIN count was
obtained. No real host low-storage condition was created.

**Next M4.1:** targeted 137, the 16-byte HNEW handle
allocation denial after QSAM OPEN, whose error branch
requires DQCLOSE/DREL. No full 00..134 panel is requested
at this stage: the owner deferred it explicitly. M4.2
OPEN diagnostics and M4.3 independently verified resource
counts remain outstanding. No installed OBJ or DEVOBJ
object was changed by this test.

## M4.1 close — all three isolated failure-path gates ACCEPTED

Following prior focused PASS 135 and 136, the operator
fast-forwarded `main` from `831ee82` to `ccb0f1b`
and ran candidate-only regression **137**, obtaining
**PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**. This exercises
HNEW's second-visit 16-byte handle GETMAIN failure after
successfully opening the candidate DD and verifies the
zero-valued FIND, selected DD01/cursor preservation and
successful later DD02 open, read and close. Actual DQCLOSE
and DREL invocation counts were **not** instrumented.

**M4.1 formally CLOSED:** source-only instrumentation
checks passed for all three 32/268/16 modes and
**135, 136, 137** passed *individually* under MVS.
This is deterministic synthetic failure-path behavior,
not true host GETMAIN exhaustion. Installed DEVOBJ
members and production OBJ remain unchanged.
The owner-deferral of full `00..134` regression remains
in effect; the last full panel is still `00..132`
with **132 PASS / 0 FAIL / 1 expected SKIP 083**.

Next: M4.2 MVS QSAM OPEN failure characterization, then
M4.3 independent GETMAIN/FREEMAIN and SVC19/SVC20
accountability. Do not treat a host abend as successful
recoverable FIND behavior.

## M4.2 preparation — distinguish returned failure from abend

Opened M4.2 with a [separate technical plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md).
Source inspection shows `DQOPEN` issues SVC 19, then
consults DCB-derived state before returning 0 or 8.
A nonzero DQOPEN return travels via `DIFCLEAN` /
`DFFCLEAN` to `DREL`, whereas HNEW failure after a
successful OPEN requires `DQCLOSE` first.

To verify that DQOPEN-reported errors preserve the caller,
staged permanent test-only compiled BCPL regression **138**
and an isolated transformer that denies the **second**
DQOPEN call **before SVC 19**, with the third call restoring
the real OPEN. The source-only check and MVS test **have
not yet been run**. No canonical runtime or PDS change
was made. This is a cleanup-branch probe, **not**
an actual incompatible-DD OPEN failure.

A later exploratory, isolated MVS job must characterize
**real** SVC 19 failure or x13 abend and record accurate
IEC/IEF codes. That gate is not staged or accepted.
The overall native regression panel is still deferred.

**Next focused operator command:**

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

## M4.2.0 targeted synthetic DQOPEN denial PASS

The operator pulled `main` through `5c890d3`,
successfully executed `tools/checks/check-bcplio-m42-open.py`,
and observed regression **138 PASS** against the
development candidate using a temporary test-only
BCPLIO object (**1 PASS, 0 FAIL, 0 SKIP, total 1**).
The injected second DQOPEN call returned failure **without
executing SVC 19**. The failed FIND returned zero, DD01
selection/cursor were preserved, and a subsequent DD02
attempt opened successfully. No installed object changed.

**This does not validate real host QSAM OPEN failure.**
The M4.2.1 exploration remains open for a truly incompatible
but allocated DD, potentially an S013 abend, with genuine
JES evidence. M4.3 independent resource counts and M5
physical DD attribution also remain outstanding. Full
regression remains owner-deferred.

## M4.2.1 real QSAM OPEN diagnostic probe staged

The stand-alone, **non-regression** exploratory files are
`native-compiler/probes/m42-real-open/`, with a
source-only fail-closed JCL construction check,
`tools/checks/check-m42-real-open-jcl.py`,
and a non-submitting JCL generator
`tools/checks/prepare-m42-real-open-jcl.py`.

The **normal installed DEVOBJ(BCPLM6+BCPLIO)**
candidate will be linked without fault instrumentation.
The exploratory `RG890R` GO job allocates valid input
`DD01 DD DATA` and deliberately gives `DD02`
`SYSOUT=*` attributes even though BCPL requests
`FINDINPUT("DD02")`. The generated deck is a manual
diagnostic only. OPEN may abend; if FIND returns zero,
RDJFCB failure vs QSAM OPEN failure must still be
distinguished from the actual JES/IEC/IEF evidence.
The source checker, Cambridge compilation and
real MVS job **have not run**. See
[M4.2 plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md)
and the probe's README for the prepare/inspect/submit
procedure. No installed object or canonical assembler
source has been altered. Full regression is still
owner-deferred.
