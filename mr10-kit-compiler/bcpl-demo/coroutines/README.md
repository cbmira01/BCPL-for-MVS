# Coroutine generator demo

The program makes a coroutine that yields values 1 through 5. Its local loop state survives each pause.

| Call | Purpose |
| --- | --- |
| `HEAPINIT` | Prepare the memory arena |
| `CREATECO` | Create the coroutine |
| `CALLCO` | Resume it |
| `COWAIT` | Yield to the caller |
| `DELETECO` | Free its storage |

The demo uses `library/getvec-freevec.bcpl` and `library/coroutines.bcpl`. Run it through `tools/run-mr10kit-demo-suite` or the MVS `MRBCDEMO` suite.
