# CO.4 — Native stack-limit and allocator inspection batch

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Status:** HOST-CHECKED / **NATIVE MVS PENDING**
**Baseline:** previously qualified native CO.3 code and owner-reported CO.4
three-case batch PASS at `976c20da29943a72867195a24e010afe4e395e1a`.

## Design and boundaries

This is an *isolated candidate*, not a runtime change or permanent
interface. It reuses exactly the accepted independent BCPL library,
private CO3DROP unregister extension, `/CN` Cambridge options, and
independent compilation/IFOX/IEWL/GO/JES driver. It leaves the
installed `BOOT_OBJ`, accepted BCPLCO, BCPLMAIN, BCPLMEM and previous
CO.3/CO.4 test sources and evidence unchanged.

A private IFOX subroutine `CO4PROB` is spliced into the ephemeral
`BCPLCO` assembly stream together with the accepted `CO3DROP`. The
application global-trailer binder resolves candidate-only G!301 to
that entry; G!302–305 are temporary application-state globals where
used, not proposed allocations. The linker resolves `MEMSTAT` from the
existing accepted `BCPLMEM` object. No new installed Core Runtime
object is created, and no permanent global slots are assigned.

`CO4PROB(V)` accepts a **known-live, caller-allocated** nine-word vector
(`GETVEC(8)`). It writes:

| Word | Source/meaning |
| ---: | --- |
| V!0 | Actual `STKLIM` byte address from BCPLMAIN |
| V!1 | Actual `APLIMIT` byte address from BCPLAPT |
| V!2 | G!54 `STACKBASE` BCPL word pointer |
| V!3 | G!55 `STACKEND` BCPL word pointer |
| V!4 | Private `CURPTR` converted to a BCPL word pointer |
| V!5 | `MEMSTAT` currently allocated vector count |
| V!6 | `MEMSTAT` peak vector count |
| V!7 | `MEMSTAT` currently allocated bytes |
| V!8 | `MEMSTAT` peak allocated bytes |

The probe is read-only with respect to runtime/allocator state; it
writes only to the supplied vector and returns zero for a valid nonzero
pointer, -1 for null. Its IFOX implementation preserves the BCPL call
ABI and R14 across the private R14-linked `MEMSTAT` call. The observer
runs only in quiescent single-threaded contexts, never amid an active
GETVEC/FREEVEC. This is *not* a public interface and does not provide
arbitrary-pointer validation.

`BCPLMEM` allocates `4*(N+1)+12` bytes for `GETVEC(N)`. Thus the
root descriptor `GETVEC(23)` is **108 bytes**, a worker descriptor
`GETVEC(27)` is **124 bytes**, and a worker stack `GETVEC(1087)` is
**4,364 bytes**. Each live worker adds exactly two vectors/4,488 bytes;
two workers plus the root descriptor add five vectors/9,084 bytes.
The tests compare deltas from a baseline taken with the observer
vector already allocated, avoiding assumptions about unrelated
runtime startup allocations.

## Three separate native cases / one coordinated operator batch

| Order | Fixture / prefix | Precise verification | Oracle |
| ---: | --- | --- | ---: |
| 1 | `limits-source.bcpl` / `CO4LIM` | Root and both worker contexts: **live** STKLIM == APLIMIT == descriptor safe limit; G54/G55 == descriptor stack boundaries; return/restoration after each yield and natural return; exact vector/byte deltas and reclamation | 12 records |
| 2 | `account-source.bcpl` / `CO4MEM` | Twelve two-worker create/yield/resume/delete rounds, each with exact MEMSTAT count/byte deltas; invalid GETVEC sizes and third-worker registry-capacity refusal produce no outstanding allocation | 8 records |
| 3 | `deny-source.bcpl` / `CO4DENY` | Deterministic temporary G87 GETVEC wrapper returns zero on the first or second `CREATECO` allocation; G87 is restored immediately; exact MEMSTAT rollback and live-worker continuity, then third-worker capacity refusal and cleanup | 12 records |

Expected output from the fixtures (exact order, individually flushed):

```text
CO4LIM ROOT
CO4LIM MADE
CO4LIM A1
CO4LIM RA1
CO4LIM B1
CO4LIM RB1
CO4LIM A2
CO4LIM RA2
CO4LIM B2
CO4LIM RB2
CO4LIM CLEAN
CO4LIM PASS
```

```text
CO4MEM INIT
CO4MEM INVALID
CO4MEM C03
CO4MEM C06
CO4MEM C09
CO4MEM C12
CO4MEM CLEAN
CO4MEM PASS
```

```text
CO4DENY MADE
CO4DENY DENY1
CO4DENY A1
CO4DENY DENY2
CO4DENY A2
CO4DENY FULL
CO4DENY RA3
CO4DENY B1
CO4DENY B2
CO4DENY B3
CO4DENY CLEAN
CO4DENY PASS
```

Any explicit `FAIL`, unexpected/malformed/truncated record, compiler
failure or nonzero native step is a hard failure. The batch runs cases
in order and stops at the first failure; earlier case receipts remain
separate. No test IDs are added or renumbered.

## Required evidence and limitations

The driver requires two real independently compiled Cambridge jobs for
each case, four RC=0000 IFOX steps, RC=0000 IEWL, RC=0000 GO, JES
SUCCESS/highest RC=0000, plus the exact ordered per-case BCPL oracle.
It stores inherited compiler logs, assembly JCL, JES reports,
`result.json` and a `co4-case-result.json` for each case, along with
`batch-result.json` under `workarea/co4-inspection-batch/`.

**Crucial distinction:** `deny-source.bcpl` simulates `GETVEC=0` at
exactly controlled invocation counts by temporarily replacing G87.
It does **not** force MVS `GETMAIN` EC failure, test a shortage of real
24-bit storage, change `BCPLMEM` or exercise abnormal termination. The
CO.3 library's post-`CO2INIT` unexpected first-`CHANGECO` result still
lacks demonstrated rollback. True memory exhaustion and dangerous
stack-overflow/abending cases remain separate, design-gated work.

Likewise, while `CO4PROB` observes actual live `STKLIM` and `APLIMIT`,
this test does not reconstruct the unknown historical INUM/overflow
policy, assert equality at a fault boundary, or prove 256-byte
clearance survives a deliberate overflow. The existing safe guard
checks are preserved as distinct CO.4 evidence.

For host-only verification, invoke the runner with `--check`; this
makes **no MVS submission**. `--run` is the sole native submission
entry point and is operator-invoked. All host unit tests are
assistant-operated; the owner only runs the single MVS-facing batch
command. A failing run must be retained, not overwritten.

**Status:** CO.4 remains IN PROGRESS, CO.5 NOT STARTED. No runtime
installation, release, public ABI promotion or qualified closure is
claimed by preparing this batch.

## First operator attempt and report-decoding correction

The first three-case attempt at `bdd1c4716cc0012d0ae314576d35bd489f4765bb`
reported a host UTF-8 decoding failure while processing a printer stream.
It did **not** satisfy the LIMITS native oracle, and ACCOUNT and DENY were
not attempted. That attempt remains a distinct FAIL, with owner-local
receipts preserved. The follow-up correction applies Latin-1 decoding
*only* to the raw `dump-report-for-job` subprocess in this test runner,
matching the project's established DSPAL report handling; accepted
CO.2/CO.3 runners and all native candidate objects remain unchanged.
See [first-run evidence and host verification](../../co4-inspection-batch-printer-decode-failure-20261114.md).
