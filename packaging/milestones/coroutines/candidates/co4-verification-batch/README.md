# CO.4 — Consolidated safe native verification batch

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Source authority:** GitHub `main`; accepted CO.3 candidate and runtime  
**Evidence classification:** HOST-CHECKED / NATIVE MVS PENDING

## Three independent native cases, one operator invocation

| Case | BCPL source | Strict output oracle | Coverage |
| --- | --- | --- | --- |
| `stack` | `stack-source.bcpl` | Six `CO4STK` records | Private worker/root extent, guard word, HWM metadata, descriptor safe-limit arithmetic, five checked recursive ancestor frames, suspend/resume and root restoration |
| `churn` | `churn-source.bcpl` | Seven `CO4CHURN` records | Sixteen complete two-worker create/yield/resume/delete cycles, third-worker capacity refusal each cycle, sequential registry reclamation, root survival |
| `busy` | `busy-source.bcpl` | Ten `CO4BUSY` records | Nested A->B call: B refuses CALLCO into busy parent, RESUMECO to busy parent/self/root; then B and A resume to root and both delete cleanly |

All applications are compiled independently of the *unchanged* accepted
CO.3 `library.bcpl`, using the accepted `/CN` checked-entry compiler
parameter, private `CO3DROP` IFOX extension and real MVS runtime objects.
The inherited CO.3 runner performs two real Cambridge compilation jobs,
four IFOX steps, IEWL and GO **for each case**, with exact ordered
per-case marker validation and JES SUCCESS / highest RC=0000 / all six
native steps RC=0000. It does not install or overwrite `BOOT_OBJ`.

`tools/coroutines/run-co4-verification-batch.py --run` executes `stack`,
`churn`, then `busy`, stopping at the first non-PASS. Individual raw
`result.json`, compiler logs, JCL, JES summary, JES report, and the
batch's `co4-case-result.json` receipts are retained separately under
`workarea/co4-verification-batch/<session>/<case>/<native-run>/`.
The top-level `batch-result.json` records attempted cases, source hashes,
and all machine job numbers from inherited evidence. Operator stdout is
limited to per-case PASS/FAIL and one batch receipt path. No extra
untracked files are opened in the repository's tracked directories;
only existing ignored `workarea/` is used for results.

The companion `--check` performs read-only source, exact marker, card
width and accepted CO.3 blob-identity validation; it does not submit
any MVS work. The host-only unit tests exercise both success and
fail-fast synthetic evidence, but synthetic receipts are not native
MVS results.

## Safety and proof limits

The stack case confirms the current candidate's **published metadata**:
`STACKEND-STACKBASE` is 16448 words for root and 1088 words for
workers (1024 safe plus 64 clearance); a guard at `STACKEND-2` matches
an unused painted safe word; and `STACKEND-1` points to the final even
safe marker. The private worker descriptor's `C!5` is the expected
safe **byte** limit, with `C!4`/`C!6` the word extents.
This does **not** directly read live `STKLIM` or `APLIMIT` in the
assembler, check the exact overflow equality boundary, or guarantee
that the guard remains untouched if a past overrun was later repaired.
Those require a separately reviewed read-only IFOX probe and, for an
actual overflow, a terminal diagnostic test with explicit ABEND/RC
policy. No over-limit frames are deliberately executed here.

The churn case demonstrates repeated successful `GETVEC`/`FREEVEC`
lifecycle behavior, registry reuse and absence of observed functional
degradation. It does **not** independently measure allocator live bytes,
prove no leaks, or inject GETMAIN refusal; the private `MEMSTAT` entry
remains available for a subsequent instrumented allocation candidate.

The busy case passes only known-live root and worker descriptors to
coroutine calls. No stale/freed pointer, arbitrary raw address,
ABA identity, forced termination or unsafe cancellation is tested.
The owner-approved Approach A, S1 and two-worker cap remain unchanged.
No permanent global allocations or new Core Runtime assembler ABI are
introduced; CO.5 remains NOT STARTED.

## Verification gate

Each native PASS requires the exact separate output oracle and the
inherited independently compiled Cambridge, IFOX, IEWL, GO and JES
receipts. A failing early case blocks later cases without rewriting
prior evidence. Failed attempts remain failures even if later reruns
succeed. These cases **do not by themselves close CO.4**.
