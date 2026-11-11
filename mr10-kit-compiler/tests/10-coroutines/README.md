# Coroutine tests

These probes show how the historical MR10 compiler lays out calls and how the reconstructed coroutine library saves and resumes work.

| Source | Check |
| --- | --- |
| `compiler-probe.bcpl` | CHANGECO argument order in generated INTCODE |
| `frame-layout-probe.bcpl` | Synthetic coroutine call-frame slots |
| `fixed-stack-producer-consumer.bcpl` | Switching between two fixed stacks |
| `resumeco-chain.bcpl` | Passing control through a coroutine parent chain |
| `create-delete-static-pool.bcpl` | Creating, deleting, and reusing coroutine storage |

## Important frame layout

The compiler probes establish these slots for `CREATEFRAME(FN,SIZE,C)`:

```text
P!2 = FN
P!3 = SIZE
P!4 = C
```

The persistent coroutine descriptor must sit **below** this frame. Nested calls would overwrite a descriptor placed above it:

```text
C!0 = saved P
C!1 = parent
C!2 = COLIST link
P = C+3
```

The call probes also show that `CHANGECO(VALUE, CPTR)` uses the two argument slots `P!2` and `P!3`. These observations come from saved OCODE/INTCODE in `evidence/`; keep those files.

## Run and check

Use `tools/mr10/compile-and-run --results` with `"$(tools/mr10/current-icint)"` and the chosen BCPL source. The create/delete test also needs `+mr10-kit-compiler/library/getvec-freevec.bcpl` and `+mr10-kit-compiler/library/coroutines.bcpl`. A successful run returns interpreted `CODE=0`.

| Runtime result | What it proves |
| --- | --- |
| Producer and consumer exchange 1 through 5 | Suspended loop state survives |
| RESUMECO passes the result to the root | Parent-chain switching works |
| New coroutine works after older ones are deleted | Freed storage can be reused |

The portable BCPL modules provide the allocator and coroutine calls. The machine-dependent `CHANGECO` for this interpreted bootstrap is in `source/iclib.int`. A native System/370 runtime will need its own switching routine.

## Accepted MR10 development probes — 11 November 2026

All five identities in this directory are **ACCEPTED** as interpreted-MR10 development probes with exact `.expected` files. The [owner-approved acceptance record](acceptance-20261111.md) documents JES jobs 5223–5227, 62 zero-RC JES steps, 23 interpreted CODE=0 phases, exact program traces, and four matching compiler-artifact pairs. These results apply to **ICINT19**, not native System/370 coroutine support or the missing historical `KM10.COMAIN`.

They are included in the coordinator's `mr10-probes` suite alongside the original six accepted development probes. Fresh post-promotion JES execution remains pending separate authorization.

## CO.0 continuation-divergence experiment (not accepted)

The source `continuation-divergence.bcpl` deliberately contrasts ordinary
`COWAIT` with `STAGEDWAIT`, which performs work after `CHANGECO` returns.
Nested `NORMALLEAF` and `STAGEDLEAF` calls exercise differing generated
post-call instruction sequences. This is a **candidate, not a golden test**.
Even a zero interpreted CODE is insufficient: inspect the generated OCODE,
INTCODE, complete output and saved interpreter evidence.

The source is mapped to `MR10_TESTS(T10CDIV)`; its stored JCL body
`mr10-kit-compiler/jcl/co0-continuation-divergence.jcl` is mapped to
`MR10_JCL(CO0TRACE)`. The deck uses installed ICINT19, the existing
`MR10_LIBRARY(GETVEC)` and `MR10_LIBRARY(COROUTIN)` modules, and temporary
sequential data sets. It compiles all three units, generates INTCODE,
prints the main source's OCODE/INTCODE under steps `SVOCMAIN`/`SVINMAIN`,
and runs the result with a 10-second CPU limit.

**Reference hypothesis, not observed:** ordinary A should yield 101 and,
when resumed with 17, compute 118 before yielding 103. The staged B
path would yield 201, resume with 27, compute 228 and yield 203 **only if**
the continuation semantics permit that transition. Divergence, unexpected
return values or an interpreted/MVS error are evidence to investigate, not
an acceptance failure of the established five coroutine probes.

On an explicitly authorized MVS session, first synchronize only these two
new members from Git using `tools/datasets/dspal put MR10_TESTS T10CDIV
mr10-kit-compiler/tests/10-coroutines/continuation-divergence.bcpl` and
`tools/datasets/dspal put MR10_JCL CO0TRACE
mr10-kit-compiler/jcl/co0-continuation-divergence.jcl`; then submit with
`tools/datasets/dspal submit MR10_JCL CO0TRACE`. These are instructions,
**not** a record of executed work. Preserve JES reports and both saved
compiler artifacts; this probe is excluded from all regression manifests
until independently verified and owner accepted.
