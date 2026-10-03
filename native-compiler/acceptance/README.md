# Native compiler acceptance sources

These programs are the initial native-code acceptance corpus described in [`../acceptance-plan.md`](../acceptance-plan.md).

They are deliberately smaller than the normal regression suite. Their job is to establish the native compiler and runtime ABI one contract at a time.

## Result mailbox convention

The early cases avoid depending on `WRITEF`, streams, or the full historical runtime.

They reserve the top of the current interpreted GLOBAL capacity:

```text
NATIVECOUNTER:399
NATIVERESULT:400
```

as **test-only globals**.

The spellings deliberately avoid underscores because the MR10 compiler used by the bootstrap does not accept `_` in identifiers.

The general-purpose project library range is 96..159, so these acceptance globals deliberately sit outside that range. They are also within ICINT V17's currently established 0..400 GLOBAL capacity, allowing the same source to be compiled/executed by the interpreted reference path when useful.

A program writes its semantic result to global 400 before `FINISH`. Case A5 also uses global 399 to verify independent GLOBAL load/store state.

These globals are not proposed as part of the production BCPL ABI. They exist only for the native acceptance harness and should disappear once ordinary native output/runtime services are established.

Expected files use notation such as:

```text
GLOBAL 400 = value
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
