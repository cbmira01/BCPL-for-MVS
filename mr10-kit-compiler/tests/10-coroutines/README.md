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
