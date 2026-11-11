# CO.0 — Historical source audit and provisional coroutine behavior

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**March:** CO.0 — Historical Research and Behavioral Contract  
**Recorded:** 10 November 2026  
**Status:** SOURCE AUDIT RECORDED; **CO.0 IN PROGRESS**, not accepted/closed  
**Scope:** GitHub historical and reconstructed source inspection; no JES execution, runtime modification, MVS dataset changes, or new test acceptance

## 1. Major archival discovery: historical KM10 coroutine variant

The preserved [transport-tape INDEX](../../../richards-bcpltape/INDEX) explicitly labels an area **"Coroutine library"** and lists:

| Tape entry | Historical name | Preserved Git path / status |
| --- | --- | --- |
| f34 | `KM10.COMAIN` | `-` (not present in preserved archive) |
| f35 | `KM10.COMACRO` | `richards-bcpltape/km10/comacro` |
| f36 | `KM10.COBLIB(CORTN)` | `richards-bcpltape/km10/coblib/cortn` |
| f37 | `KM10.COBLIB(STANDARD)` | `richards-bcpltape/km10/coblib/standard` |
| f38 | `KM10.J(COLIB)` | `richards-bcpltape/km10/j/colib` |

This is direct **historical System/370-family coroutine evidence** from the source archive, distinct from the reconstructed MR10 INTCODE coroutine layer. It **does not** establish that the missing `KM10.COMAIN` implementation can be reconstructed mechanically, nor that its full API is already present in the ordinary historical `SYS3.BCPL.LIBHDR` / `BCPLIB.BCPL(BLIB)`.

### Historical COBASE macro (SOURCE-OBSERVED)

`KM10.COMACRO`'s `COBASE` DSECT describes:

| Field(s) | Source comment / meaning |
| --- | --- |
| `COLINK` | Coroutine chain |
| `COFATHER` | Activator or 0 if inactive |
| `COPSAVE` | Saved stack pointer |
| `COLBASE`, `COLEND` | Local stack base and limit in **BCPL word addresses** |
| `COSTKLIM` | Local stack limit in **byte address** representation |
| `COSTACK`, `COENTRY` | Start of coroutine stack and main entry point |
| `COBSEPTR`, `COEXIT`, `CORTNARG` | Base-of-stack, exit address, argument word |
| `COHOLD`, `COLDPTR`, `COSTART` | Initial wait state, old stack pointer, startup routine |
| `COXTEND`, `COMIN` | Stack alignment/initialization and minimum stack size |

The macro deliberately aligns the area before the initial stack. Do not invent a hard-coded offset for aligned `COSTACK` or treat these native fields as the MR10 interpreted descriptor.

The same historical macro library defines `CODELETE EQU 102` and a user-save-area group `COLIST`, `USACBASE`, `MAINBASE`, `SAVEBASE`. Its comments state that the root coroutine stack is used for error processing, with the active coroutine saved on error. These are **historical clues about runtime ownership**, not a recovered full context-switch implementation.

### Coroutine-aware historical library and linkage

`KM10.COBLIB(CORTN)` is a `SECTION "BLIB"` source variant with `CSTKBASE:107`, `CSTKEND:108`, `CSTKHWM:109`. Its `BACKTRACE` uses private `SAVEAREA` offsets `COLIST=68`, `COLIVE=69`, `COMAIN=70`, `COSAVE=71` and descriptor fields `CONEXT=0`, `COFATHER=1`, `COPSAVE=2`, `COENTRY=6`, `COLIM=5`. It walks active parent chains, inactive coroutines, and per-coroutine stack usage. The descriptions imply a mix of stored **byte pointers** and **word pointers** with explicit conversions; verify each independently.

`KM10.J(COLIB)` includes `BLIB(CORTN)` as `$CORTN$` and `BLIB(STANDARD)` as `BLIB` while also linking `BCPLMAIN` and other components. The script demonstrates a **separate coroutine-aware component in the historical link construction**, rather than proof that an ordinary `LIBHDR` declaration by itself installs coroutine routines.

**Evidence boundary:** the conventional preserved `richards-bcpltape/sys3/bcpl/libhdr` and `richards-bcpltape/bcplib/bcpl/blib` do not declare/define the project's named `CHANGECO`, `CURRCO`, `COLIST`, `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO` interface. However the KM10 material establishes that **a historical native coroutine variant did exist**. The missing `KM10.COMAIN` means the complete original machine-code primitive remains unrecovered.

## 2. Reconstructed MR10 interpreted switching (SOURCE-OBSERVED)

Sources: `mr10-kit-compiler/source/iclib.int`, `mr10-kit-compiler/asm/icintv19.asm`, original `richards-bcpltape/mr10/bcplkit/icint`.

The project-created `ICLIB` global-6 entry reads:

```text
6 LIP2 SG9 LIP1 SG10 LIP0 SIG7 LIP3 SG7 LL498 LIG7 X1 X32
498 LIG9 JIG10 G6L6
```

Decoding under the historical interpreter's operation table (source observations, not executed evidence):

1. `LIP2 SG9`: place outgoing `CHANGECO` argument VALUE in scratch `G!9`.
2. `LIP1 SG10`: place the `CHANGECO` frame's saved return continuation in scratch `G!10`.
3. `LIP0 SIG7`: write the outgoing caller frame pointer `P!0` through `G!7` (current descriptor's saved-P word).
4. `LIP3 SG7`: make the incoming descriptor the current one by replacing `G!7`.
5. `LL498 LIG7 X1 X32`: load the incoming saved P (`!G!7`) into A and trampoline label 498 into B, then `X32` installs interpreted `P=A`, `C=B`.
6. At label 498, `LIG9 JIG10` loads the transferred value and branches via `G!10`.

The original MR10 interpreter defines `X32` as `P,C := A,B` for `LONGJUMP(P,L)`; `ICINT19` implements the same P/C assignment. Thus **no new INTCODE opcode is present** in this bridge. `G!9`/`G!10` are scratch values used by this mechanism, not native Cambridge global assignments.

**Priority verification question:** the bridge stores the outgoing frame pointer in the descriptor but uses shared scratch `G!10` for the return continuation. Determine, from actual interpreted execution and a full control-flow trace, exactly how different `CHANGECO` call sites are resumed and whether this implementation preserves arbitrary continuations. Do not promote an inferred general correctness claim from the single accepted basic regression.

## 3. Reconstructed MR10 BCPL coroutine semantics (SOURCE-OBSERVED)

Source: `mr10-kit-compiler/library/coroutines.bcpl`. This is project reconstruction, **not** the missing historical KM10 coroutine implementation.

| Operation | Direct source behavior | Limit / question |
| --- | --- | --- |
| `CALLCO(C,A)` | Returns `-999` when `C!1 != 0`; otherwise stores current coroutine in `C!1` and calls `CHANGECO(A,C)`. | Requires valid C before first dereference. |
| `COWAIT(A)` | Gets `CURRCO!1` as parent, clears `CURRCO!1`, calls `CHANGECO(A,parent)`. | No explicit null-parent guard; wait value is intended for caller. |
| `RESUMECO(C,A)` | Saves own parent, sets own parent to 0, checks target `C!1`; returns `-998` if occupied; otherwise assigns target parent and switches. | **Ordering hazard:** on busy-target error, the current parent has already been cleared. Must verify and design failure invariants. |
| `CREATECO(FN,SIZE)` | `GETVEC(SIZE+9)`; returns 0 on allocator refusal; descriptor `C!0=P=C+3`, `C!1=CURRCO`, `C!2=COLIST`; initializes `P!0..P!4`, links descriptor and switches. | Size is in BCPL words at source level; initial synthetic frame is MR10-specific. |
| Coroutine body | Following initial switch, repeats `C := FN(COWAIT(C))`. | A natural `FN` return loops into another `COWAIT`/invocation; no explicit terminal state. Do not claim automatic termination. |
| `DELETECO(C)` | Rejects zero/current/active-parent descriptors; searches `COLIST`, unlinks and `FREEVEC(C)` only if found; returns TRUE/FALSE. | It **dereferences `C!1` before proving membership**; stale/invalid pointers are not safe. No explicit double-delete protection. |

Descriptor below the synthetic frame: `C!0` saved P, `C!1` parent, `C!2` list link; `P=C+3`, `P!2=FN`, `P!3=SIZE`, `P!4=C`. This is backed by `mr10-kit-compiler/tests/10-coroutines/evidence/` compiler OCODE/INTCODE and the kit's call-frame rules. **The native System/370 descriptor has not been selected.**

## 4. Regression/evidence state

- `mr10-kit-compiler/tests/00-regression-panel/coroutines/basic-coroutine.bcpl` tests a worker yielding `ARG+7` and deletion. Its golden fixture is `RP: COROUTINE 77 1`, and it participates in the separately accepted 12-case MR10 panel. This does **not** cover general lifecycle or native switching.
- All five `mr10-kit-compiler/tests/10-coroutines/` development probes are `UNVERIFIED` in `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. Saved OCODE/INTCODE for the two compiler probes exist; these fixtures are **archived artifact evidence**, not a fresh compiler run.
- `compiler-probe` shows ordinary two-argument `CHANGECO(VALUE,CPTR)` call generation; `frame-layout-probe` records a synthetic MR10 frame. Neither executes `CHANGECO` from its `START` procedure.
- `fixed-stack-producer-consumer` is intended to exchange values 1–5; `resumeco-chain` exercises parent-chain transfers; `create-delete-static-pool` exercises allocation/reclamation. These are **test intents**, not accepted run outcomes.
- **No JES jobs executed in this CO.0 audit.** Do not mark the five probes accepted or claim a native regression PASS.

## 5. Outstanding CO.0 tasks before owner acceptance

1. With separate JES authorization, run all five historical `10-coroutines/` development probes using the current supported runner and correct module bindings; retain actual interpreted phase completion, JES steps, exact output, and compiler artifacts.
2. Produce independently checked call-site/return-continuation traces for `ICLIB` `G!9/G!10`, `X32` and `JIG10` under multiple coroutine call sites. Investigate anomalies rather than merely matching expected high-level prints.
3. Extract candidate expected outputs for all three executable probes; review and accept independent golden oracles **only after** actual execution.
4. Search additional period manuals, historical tape comments and source provenance for the missing `KM10.COMAIN` coroutine routines, global numbers, initialization and disposal semantics. Treat macro/layout clues as incomplete.
5. Build an explicit interpreted-versus-native **observable** behavior table: entry argument, yield/resume value, parent ownership, root context, invalid target, function return, reuse and cleanup. Separate inherited behavior from new native safety decisions.
6. Resolve what CO.0 can normatively require when the reconstructed MR10 implementation exposes the side effects and continuation questions above. Preserve divergences and explicit limitations instead of declaring historical identity.

CO.0 remains **IN PROGRESS** until the evidence and contract pass separate owner review. CO.1–CO.5 remain NOT STARTED. No runtime implementation, global-number allocation, regression manifest edit, new JCL or MVS operation is authorized by this audit.
