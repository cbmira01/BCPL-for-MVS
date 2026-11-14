# CO.2 — Native CHANGECO isolated implementation candidate

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation (IN PROGRESS)  
**Source:** `bootstrap-toolchain/asm/bcplco.asm`  
**Compiler options:** `/CN` (native checked System/370 entry)  
**Status:** candidate-only; real MVS IFOX/IEWL/GO evidence PENDING

This is the first separate **Core Runtime** implementation candidate after
qualified CO.1 acceptance. It extracts CO.1's tested machine-context
mechanism without the experimental generation-token facade or CO.3 lifecycle
library. The public interface, layout and error numbers are **not frozen**.

## Internal candidate contract

- `CO2INIT(root, worker, stack, procedure)`: initialize at most two
  independently stacked workers under one root. Inputs are **valid, distinct,
  live BCPL word pointers** to 24-word descriptors and 1088-word worker
  stack vectors. Return 0 on success and a test-local refusal otherwise.
  Calls originate in the active root. Storage ownership stays with BCPL.
- `CHANGECO(value, target)`: cooperatively switch from the current
  context to a registered inactive root/worker context, passing the value
  through R7. Known active, null, unregistered and terminated targets return
  a private negative value without transferring.
- The *24-word layout, state codes and G!295–299* exist only for this
  isolated native test. The small private registry is not a handle
  manager. Freed/reused or arbitrary pointers are outside this contract.

The module saves R0–R15 and the caller's frame/continuation. A first-run
worker starts via an ordinary CG370 procedure entry using a synthetic
caller frame. Its normal `RESULTIS` return follows `RETIMPL`, marks
the worker terminated, and switches to the root. Both workers have
separate safe stack limits and checked frames. Each switch installs
`STKLIM`, `APLIMIT`, G54 (`STACKBASE`) and G55 (`STACKEND`).
The host tool assembles a temporary copy of `BCPLMAIN` exporting
`STKLIM`; **the accepted object library is never rewritten**.

## Reproducible candidate execution

Run after updating to the recorded GitHub commit, from the project root:

```bash
python3 -B -m unittest tools.checks.test_co2_native_changeco -v
python3 -B tools/coroutines/run-co2-native-changeco.py --run
```

The runner compiles `source.bcpl` with the existing Cambridge compiler,
generates and retains the complete actual JCL at
`workarea/co2-native-changeco/<run>/candidate.jcl`, assembles three
independent IFOX objects, links with IEWL and executes the temporary
load module under MVS. It authenticates the job card through `dspal`,
uses installed `BOOT_OBJ` as **DISP=SHR read-only**, and requires five
specific zero-RC JES steps. Full printer receipts and machine-readable
results remain in the same evidence directory.

Expected ordered native BCPL output (the oracle checks exact order and
rejects any extra failure marker):

```text
CO2BCPL A1
CO2BCPL B1
CO2BCPL A2
CO2BCPL R1
CO2BCPL B2
CO2BCPL R2
CO2BCPL PASS
```

This exercises first activation, two live worker contexts, direct
worker-to-worker switching, recursively nested locals on both stacks,
resume values, natural worker returns, terminated re-entry rejection
at live addresses and restoration of root stack bounds. The source
checks the worker's published G54/G55 boundaries during execution.

**Evidence classification:** offline source checks, fake-driver tests and
synthetic JES samples never establish a real MVS PASS. Do not mark
CO.2 CLOSED, assign permanent globals, promote candidate objects,
or claim broader CO.3/CO.4/CO.5 acceptance without a separate owner
decision. `/CPN` combined counting/check behavior, PSW/condition-code
preservation, unsafe pointers, deletion and concurrent execution
remain outside this acceptance candidate.
