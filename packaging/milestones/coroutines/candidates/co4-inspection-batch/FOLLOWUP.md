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
