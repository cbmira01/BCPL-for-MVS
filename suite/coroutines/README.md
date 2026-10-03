# Coroutine generator demo

This demonstration presents the reconstructed BCPL coroutine runtime as a small generator. A dynamically created coroutine owns its own suspended stack and preserves the local state of a `FOR` loop while yielding values back to the root coroutine with `COWAIT`.

The demo uses the packaged runtime modules in `library/` rather than embedding coroutine or allocation support in the program itself.

Run from the repository root:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    suite/coroutines/coroutines.bcpl \
    +library/getvec-freevec.bcpl \
    +library/coroutines.bcpl
```

Expected program output:

```text
COROUTINE GENERATOR DEMO
ROOT CREATED GENERATOR
  GENERATOR YIELDS 1
ROOT RECEIVED 1
  GENERATOR YIELDS 2
ROOT RECEIVED 2
  GENERATOR YIELDS 3
ROOT RECEIVED 3
  GENERATOR YIELDS 4
ROOT RECEIVED 4
  GENERATOR YIELDS 5
ROOT RECEIVED 5
GENERATOR FINISHED
GENERATOR DELETED
```

followed by interpreted `CODE = 0`.

The example demonstrates:

- `HEAPINIT` establishing a fixed BCPL-addressable allocation arena;
- `CREATECO` allocating and initializing a coroutine;
- `CALLCO` resuming it from the root coroutine;
- `COWAIT` yielding values back to the caller;
- preservation of coroutine-local loop state across suspensions; and
- `DELETECO` returning the coroutine storage through `FREEVEC`.

`CHANGECO` remains the machine-dependent primitive supplied by the interpreted runtime; the demo itself uses only the packaged BCPL coroutine interface.
