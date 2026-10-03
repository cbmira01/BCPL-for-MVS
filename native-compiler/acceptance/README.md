# Native compiler acceptance sources

These programs are the initial native-code acceptance corpus described in [`../acceptance-plan.md`](../acceptance-plan.md).

They are deliberately smaller than the normal regression suite. Their job is to establish the native compiler and runtime ABI one contract at a time.

## Result mailbox convention

The early cases avoid depending on `WRITEF`, streams, or the full historical runtime.

They reserve:

```text
NATIVE_RESULT:150
```

as a **test-only result mailbox**.

A program writes its semantic result to global 150 before `FINISH`. The reconstructed native startup/test shim can inspect that slot after program termination or through the `FINISH` path.

This global is not proposed as part of the production BCPL ABI. It exists only for the native acceptance harness and should disappear once ordinary native output/runtime services are established.

Expected files use the notation:

```text
GLOBAL 150 = value
```

A0 is the exception: it tests startup and termination only.

## Cases

| Case | Purpose |
| --- | --- |
| `a0-finish.bcpl` | startup, START resolution, FINISH |
| `a1-arithmetic.bcpl` | literals and integer arithmetic |
| `a2-loop.bcpl` | locals, comparison, branch, loop |
| `a3-function-call.bcpl` | first BCPL function call and returned value |
| `a4-arguments.bcpl` | four register arguments plus fifth workspace argument |
| `a5-global.bcpl` | ordinary GLOBAL load/store and test mailbox |

## OCODE capture

Before implementing CG370 support for a case, capture its OCODE through the current MR10 path and retain it beside the source as `<case>.ocode`.

Use the exact project tool invocation that exists at the time of capture, and record it in this README or the case-specific evidence if the command changes.

Do not hand-write the `.ocode` files. They are evidence of what the working compiler actually emits.
