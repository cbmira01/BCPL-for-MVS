# CO.3 — Coroutine Library and Lifecycle: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle  
**Owner decision:** **CLOSED (qualified)**  
**Decision date:** 14 November 2026 (Louisville local time)  
**Source reviewed:** GitHub `main` at `a2c54bc41a7dcc74ac8aec2b2c42be45d8ec10a8`  
**Next march:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)

## Explicit owner authorization and acceptance review

The owner directed: **“Review CO.3 for acceptance and closure. Proceed to CO.4 as soon as possible. Give me a handoff prompt for CO.4.”**

Following review of the official CO.3 acceptance gate and the three
separate, source-verified, owner-reported MVS PASS receipts, this direction
is taken as authorization for **qualified CO.3 closure** and immediate
opening of CO.4. Qualified closure accepts the **bounded native lifecycle
implementation gate**, not an unrestricted production-safe public
coroutine API. CO.5 remains NOT STARTED.

The milestone's precise CO.3 gate is **independent BCPL module linkage
and deterministic MVS behavioral tests**. Its targeted functions are
creation, parent-chain calls, waiting, resumption, ordinary return,
deletion, and supported storage reuse. The sources and reported outcomes
meet that scoped gate.

## Accepted native MVS evidence

| Candidate | Cambridge compiler JOBS | Native JOB | IFOX / IEWL / GO | Ordered BCPL oracle | Result |
| --- | --- | --- | --- | --- | --- |
| [First lifecycle](candidates/co3-first-lifecycle/README.md) | 5384, 5385 | 5386 | 4 / 1 / 1 | 8 records, `MADE … PASS` | RC=0 |
| [Nested parent chain](co3-parent-chain-jes-5390-5392-pass-20261114.md) | 5390, 5391 | 5392 | 4 / 1 / 1 | 13 records, `MADE … PASS` | RC=0 |
| [Deletion and reuse](co3-delete-reuse-jes-5395-5397-pass-20261114.md) | 5395, 5396 | 5397 | 4 / 1 / 1 | 21 records, `MADE … PASS` | RC=0 |

The strict runners require all four IFOX steps, IEWL and GO to
complete at RC=0000, JES SUCCESS/highest RC=0000 and exact ordered,
complete `CO3BCPL` records. They use separate Cambridge-compiled
application and library translation units; `C3INIT`, `C3CREATE`,
`C3DELETE`, `C3CALL`, `C3WAIT`, and `C3RESUME` linker aliases
are registered through the application's global trailer, rather than
assuming IEWL automatically registers BCPL procedures.

**Evidence classification:** OWNER-REPORTED NATIVE-MVS-TESTED, based
on the operator's runner PASS output and reviewed GitHub runner and
candidate source. Raw operator-local compiler listings, JCL and JES
reports were not supplied for independent inspection:

- `workarea/co3-first-lifecycle/20261114T185702Z-1sa3c7r0`
- `workarea/co3-first-lifecycle/20261114T232638Z-skwqfecr`
- `workarea/co3-delete-reuse/20261115T000019Z-nc9zruc0`

The three passing runs used distinct source revisions; the latest
deletion/reuse PASS was tested at
`1875b26110dae6b19be05cf77a150cb54a1bb392`, then documented
at `a2c54bc41a7dcc74ac8aec2b2c42be45d8ec10a8` without changing the native candidate.

## Native behavior accepted, with explicit bounds

The independently compiled BCPL library exercises
`CO3INIT`, `CREATECO`, `CALLCO`, `COWAIT`, `RESUMECO`,
`DELETECO`, and ordinary worker return through `CO3BOOT`.
The tests establish a root and up to two live independent workers;
nested worker-to-worker calls and parent-chain transfers;
refusal to resume a busy target without damaging the current parent;
preserved frame locals and returned values; worker return followed
by waiting/re-entry; and restoration of root G54/G55 stack metadata.

`DELETECO` is tested with root-owned, known-live, inactive,
parent-free workers. Candidate-only IFOX `CO3DROP` checks registry
admission before descriptor dereference, marks a descriptor revoked
and removes the registry address **before** BCPL unlinks the worker
and invokes `BCPLMEM FREEVEC` for the stack and descriptor.
The native test exercises capacity refusal, survivor continuation,
deletion and repeated *registry-slot* reuse. It does not assert
identical physical allocation-address reuse.

## Preserved failures

Original failures are not reclassified as PASS:

- Initial `DC A(0+L<n>)` alias parsing rejection (before native GO).
- Incorrect submit script suffix `submit-jcl.sh` (before native GO).
- Parent-chain JOB **5389**: four IFOX and IEWL RC=0000, GO
  RC=0012, output truncated at the 132-byte buffer boundary.
  The fixture's `NEWLINE()` was replaced by native `WRCH(10)`
  for the later JOB 5392 PASS; the newline discrepancy remains
  separately open.
- First deletion/reuse adapter failure at
  `4565e9f6aca065fc3193ec7e044dc06055531a08`: a mismatched
  literal `EXTRN` / `ENTRY` list prevented native job submission.
  The six-symbol adapter repair passed with JOB 5397.

## Qualifications and CO.4 transfer

**Not accepted:** production/public ABI or global-number ownership;
a production descriptor layout; general stale-pointer or use-after-free
safety; true ABA-safe identity when MVS reissues a freed descriptor
address; arbitrary-pointer dereference recovery; stack-size variation;
exhaustion/recovery guarantees; audited recursion and boundary handling;
long/repeated transfer stress; comprehensive exceptional cleanup;
PSW/condition-code guarantees; subtask reentrancy or concurrency;
installed `BOOT_OBJ` promotion; release readiness or full historical
fidelity. The accepted design remains Approach A (known-live
descriptors) and S1 (independent checked stacks), with two live workers,
fixed 1024-word working stacks and 256-byte clearance. G!289–300 are
**test-local only**, not public Global Number Registry allocations.

Natural worker return in the CO.3 `CO3BOOT` loop means **wait and
re-entry**, not automatic termination-and-freeing; no stronger
termination semantics are accepted.

The owner explicitly directed immediate CO.4 transition.
[CO.4 kickoff](co4-robustness-and-edge-case-verification-kickoff-20261114.md)
defines the next test/evidence gate, holding the accepted source
baseline unchanged. Any change to the public ABI, opaque handles,
globals, coroutine resource ownership or exceptional behavior requires
a separate owner design decision before implementation.

## Disposition

- CO.0 — Historical Research and Behavioral Contract: CLOSED (qualified).
- CO.1 — Native ABI and Stack Architecture: CLOSED (qualified).
- CO.2 — Native CHANGECO Implementation: CLOSED (qualified).
- **CO.3 — Coroutine Library and Lifecycle: CLOSED (qualified, owner-directed).**
- **CO.4 — Robustness and Edge-Case Verification: IN PROGRESS.**
- CO.5 — Integration, Regression, and Release: NOT STARTED.

This closure and transition record makes **no MVS submission**, does not
alter `BOOT_OBJ`, add permanent globals, install a candidate or
publish a release. Source, tests and historical failure receipts remain
unchanged.
