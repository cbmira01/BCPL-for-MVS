# Dynamic BCPLIO stream milestone — M4 failure/lifecycle inventory

Status: **M4.0 targeted invalid-DD regression 134 ACCEPTED; complete 00..134 compatibility sweep pending; M4.1–M4.3 open**
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
