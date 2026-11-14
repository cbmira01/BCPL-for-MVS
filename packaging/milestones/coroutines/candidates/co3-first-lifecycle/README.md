# CO.3 — first independently compiled BCPL lifecycle candidate

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Status:** OFFLINE-CHECKED candidate; real Cambridge/IFOX/IEWL/GO results pending

This candidate begins CO.3 with actual BCPL source compiled as a **separate
library translation unit**, rather than copying lifecycle code into the
application. It uses the qualified CO.2 `BCPLCO` IFOX candidate unchanged
and links `BCPLMEM` and other installed `BOOT_OBJ` dependencies read-only.

Files: `library.bcpl` (independent library), `source.bcpl` (application
oracle), `cambridge-parm.txt` (checked native `/CN`), the
`tools/coroutines/run-co3-first-lifecycle.py` MVS runner, and
`tools/checks/test_co3_first_lifecycle.py` offline checks.

## Private initial contract

- `CO3INIT()` allocates a root descriptor. The test application initializes
  private G!295–297 to zero before invoking it.
- `CREATECO(FN,1024)` creates a new worker using `GETVEC(27)` for the
  candidate descriptor and `GETVEC(1087)` for the 4096-byte checked stack
  plus 256-byte clearance. Creation is restricted to root.
- `CO3BOOT` first yields the descriptor; later `CALLCO(C,A)` delivers A.
  `COWAIT(V)` suspends to the parent and returns V. Ordinary return from
  the worker function leads to another wait, allowing function re-entry.
- G!289–299 (including CO.2's G!298–299) are **test-local**; no public
  allocation or header is approved. The 24-word machine descriptor prefix,
  extra private words 24–27, and error returns are **not public ABI**.
- `CO2INIT` currently supports only two registered workers and has no
  unregistration. `DELETECO`, `RESUMECO`, worker-side creation, arbitrary
  stack sizes and address reuse are **not implemented by this first slice**.
  Never `FREEVEC` a registered worker or a running stack.

## Independent compilation and linker evidence gate

The runner submits **two distinct Cambridge compiler jobs** for the application
and the BCPL library. It transforms the library's own generated global
trailer into explicitly exported, linker-visible procedure aliases, and
adds those aliases to the application registration trailer. It then uses
**four separate IFOX object steps** (application, library, test-local
`BCPLMAIN` export copy, and `BCPLCO`), followed by IEWL and native GO.
No BCPL sources or generated object bodies are concatenated.

The exact output oracle is:

    CO3BCPL MADE
    CO3BCPL W1
    CO3BCPL R1
    CO3BCPL W2
    CO3BCPL R2
    CO3BCPL W3
    CO3BCPL R3
    CO3BCPL PASS

The runner fails on missing/nonzero JES steps or any missing, extra,
malformed or misordered BCPL records, retains complete evidence under
`workarea/co3-first-lifecycle/`, and writes only temporary MVS datasets.
Successful host-side checks do **not** constitute MVS verification.

## First MVS execution attempt: CG370 export adapter correction

On 14 November 2026 the owner ran the first candidate from GitHub
`main` at `85d139b55a84791a7f80379e26a683d83ba091bc`.
The driver recovered generated compiler output and failed during
host-side export preparation with:

    CO.3 first lifecycle FAIL: nonlocal CG370 procedure label: '0+L3'

The original validation expected `L3`, but the historical Cambridge
CG370 `GENDCA(L,N)` prints `DC A(N+L<label>)`. In particular,
`GENDCA(label,0)` emits `DC A(0+L3)`, which is a valid relocatable
expression. The export adapter now accepts bare `L<label>` or
`0+L<label>`, verifies the referenced local `EQU` label, and
emits an external `EQU L<label>` alias. Nonzero/unsupported
addends remain rejected.

The failure occurred **before** generating/submitting the native GO job.
No IFOX, IEWL or native GO success is claimed for this attempt.
Operator-local evidence:
`workarea/co3-first-lifecycle/20261114T182604Z-87td7zrv`.
The corrected offline suite contains direct zero-addend cases,
negative relocation cases and an end-to-end temporary-JCL deck test.
The next MVS execution must independently establish IFOX, IEWL and GO.

## Second MVS execution attempt: submit-tool preflight correction

The next owner-run attempt reached the native submission step but failed
before submitting the generated native job:

    [Errno 2] No such file or directory: tools/mvs/submit-jcl.sh

The actual repository tool is the executable `tools/mvs/submit-jcl`
(no .sh suffix), also used by the accepted CO.2 candidate runner. The
CO.3 runner now uses this canonical path and verifies that the submit,
summary, and report tools exist and are executable **before starting**
compiler jobs. It also detects divergence from CO.2's submit path.

The first two Cambridge compilation steps reached completion before the
missing submit-tool path was used; **no native IFOX, IEWL or GO was
submitted by this failed attempt**. Owner-local evidence:
`workarea/co3-first-lifecycle/20261114T183415Z-ksnw0gfk`.

## First native lifecycle PASS: owner-reported JOBS 5384–5386

On 14 November 2026, using GitHub `main` at
`ef78999dd785585b7e9e18e15f128ab4b34a3531`, the owner reported
successful independent Cambridge BCPL compilation of application
JOB **5384** and library JOB **5385**, followed by native JOB **5386**.
The CO.3 runner reported four RC=0000 IFOX steps, one RC=0000 IEWL,
one RC=0000 GO, and its exact eight-record `MADE W1 R1 W2 R2 W3 R3
PASS` application oracle. Runner RC=0.

**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED; the assistant has not
independently inspected the operator-local raw generated assembly or JES.
Evidence directory:
`workarea/co3-first-lifecycle/20261114T185702Z-1sa3c7r0`.

This validates the independently compiled and linked first-slice
`CO3INIT`, `CREATECO`, `CALLCO`, `COWAIT` and `CO3BOOT`
positive paths; it does not validate `RESUMECO`, deletion, storage
reuse, installed objects or production ABI status.

## Parent-chain RESUMECO candidate (native MVS evidence pending)

`parent-chain.bcpl` and `library.bcpl` extend the **same candidate**
with private G!294 `RESUMECO`, compiled and linked independently.
Two workers exercise nested ROOT→A→B `CALLCO`, an attempted busy
`RESUMECO` (refused without losing B's parent), A→B
`RESUMECO` that inherits ROOT as parent, two independent waiting
continuations, ordinary worker completion and root G54/G55 restoration.

Select `--scenario parent-chain --run` in the same native runner.
The strict **13-record** target oracle is:

    CO3BCPL MADE
    CO3BCPL A1
    CO3BCPL B1
    CO3BCPL A2
    CO3BCPL B2
    CO3BCPL R1
    CO3BCPL A3
    CO3BCPL R2
    CO3BCPL B3
    CO3BCPL R3
    CO3BCPL A4
    CO3BCPL R4
    CO3BCPL PASS

The original `--scenario first` remains selectable and retains its
original eight-record oracle. Private G!294 and error `-998` do not
create public allocations or contracts. This candidate does not free
registered descriptors or worker stacks, and CO.3 remains IN PROGRESS.

## JOB 5389 parent-chain failure: output-buffer capacity

On 14 November 2026, native JOB **5389** completed all four IFOX
steps and IEWL at RC=0000, but GO returned **RC=0012**. The observed
markers ended in `... A4 R`, with no `PASS`. The 132-byte
`BCPLIO` record boundary is reached exactly after `MADE` through
`A4` and nine characters of `R4` (counting newline characters).
This is a real failed native test, separately documented in
[JOB 5389 output-capacity evidence](../../co3-parent-chain-jes-5389-output-capacity-failure-20261114.md).

The corrected **parent-chain fixture only** now explicitly calls
`WRCH(10)` instead of `NEWLINE()` to request native `IOWRCH`
record flushing. The library, the IFOX switch and the 13-marker
behavioral assertions are unchanged. Native re-verification pending;
the original JOB 5389 remains FAIL.

## Next integration gate

After actual native evidence, add `RESUMECO` and parent-chain verification,
then define and test safe IFOX unregister-before-FREEVEC for `DELETECO` and
a bounded descriptor/stack reuse test. Do not close CO.3 without explicit
owner acceptance; CO.4–CO.5 remain NOT STARTED.
