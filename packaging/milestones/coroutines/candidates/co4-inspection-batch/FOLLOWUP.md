# CO.4 inspection follow-up: ACCOUNT and DENY

The original three-case inspection runner remains available. Its LIMITS
case achieved owner-reported native PASS at `b0ce46fd965d1ca7720594fc5516ad7dd12f3993`.
ACCOUNT did not reach its first `INIT` marker; DENY was not yet attempted.

`tools/coroutines/run-co4-inspection-followup.py --run` submits the two
remaining independent cases, ACCOUNT then DENY, using the same accepted
Cambridge /CN, independent BCPL library, IFOX, IEWL, JES and read-only
`BOOT_OBJ` pipeline. The original LIMITS source, observer IFOX, accepted
CO.3 runtime/library and installed MVS objects are unchanged.

The two updated fixture sources use `PROBEPTR:305` and `SNAP(N,B)` to match
the native-PASS LIMITS observer call style. This reduces an unnecessary
fixture difference; it is **not** proof of any compiler bug. They preserve
all existing positive oracle tokens (8 ACCOUNT; 12 DENY) and expected
allocator counts/bytes. On negative paths only, diagnostic records such
as `CO4MEM FCOUNT`, `CO4MEM FBYTES` or `CO4DENY FPROBE` precede `FAIL`.
A diagnostic record is never accepted as PASS by the strict oracle.

The coordinator continues after an **output-oracle-only** failure because
that error can arise only after successful IFOX, IEWL, GO and JES checks
in the inherited driver. It does **not** continue after compilation failure,
JES nonzero result, abend, source drift, lost evidence or other failure.
The combined status is FAIL if either of the two cases fails. Its receipts
reside under `workarea/co4-inspection-followup/<UTC-run>/`, with separate
subdirectories for each MVS case. It prints only concise native status.

Host checks are performed by the assistant. `--check` is offline and
never submits MVS jobs; `--run` requires explicit operator invocation.
No new regression numbers, ABI assignments, installed MVS objects or
production artifacts are introduced. CO.4 remains IN PROGRESS.

## Second owner run — DENY native PASS; ACCOUNT bootstrap mismatch

At GitHub `main` `491f4acaa44a37eb4e63ff7e3bc75693c96211c7`,
independent MVS execution yielded `CO4MEM FCURR`, `CO4MEM FAIL` for ACCOUNT
and an exact `CO4DENY` native PASS for DENY. The combined result was
`FAIL (1/2 PASS)` with distinct receipts at
`workarea/co4-inspection-followup/20261115T140823Z-zg8lgr_p/`.
This is **not** a successful ACCOUNT run; do not merge the separate outcomes.

The `FCURR` record occurs before `CO4MEM INIT`: `CO3INIT()` has
published the BCPL root globals, but `BCPLCO.CURPTR` is initialized to
zero and is populated by `CO2INIT()` only when the **first worker** is
created. The original `SNAP` routine incorrectly demanded equality of
`CURPTR` and `CO3CURR` during this pre-registration interval. That
expectation was a test-fixture defect, not a demonstrated runtime or
compiler failure.

The corrected ACCOUNT fixture uses `BOOTSNAP` exclusively for the two
pre-worker snapshots (root descriptor allocation, then invalid-GETVEC
refusal). This checks zero machine `CURPTR`, initialized BCPL root
state, the empty worker list, exact allocation counts/bytes, and
allocation peak invariants. **The existing `SNAP` remains unchanged**
for all checks after the first `CREATECO`, including a strict test of
machine `CURPTR == CO3CURR`. New `FBPROBE`, `FBOOT`, `FBCOUNT`,
`FBBYTES`, and `FBPEAK` markers diagnose any bootstrap mismatch and
remain failure-only records. The eight-record successful ACCOUNT oracle
is unchanged.

The follow-up runner now accepts an optional `--case account` on
`--run`, still using the same independently compiled Cambridge, IFOX,
IEWL, GO and JES test pipeline. Unqualified `--run` continues to
execute ACCOUNT then DENY. `--check` always verifies both sources;
`--case` with `--check` is rejected. Evidence remains segregated by
UTC run and case; no prior receipts are overwritten. Because DENY has
already passed, the next operator command runs only ACCOUNT. Neither
LIMITS nor DENY is resubmitted.

No accepted CO.2/CO.3 runtime, IFOX bridge, installed MVS object, or
public global assignment changes. This correction is **HOST-CHECKED,
MVS-PENDING**; CO.4 remains IN PROGRESS and CO.5 NOT STARTED.
