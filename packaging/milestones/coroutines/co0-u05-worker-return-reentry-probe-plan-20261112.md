# CO.0 — U05 worker return and re-entry probe

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)
**Status:** SOURCE-OBSERVED; new candidate NOT MVS-TESTED
**Source baseline:** `fd1de0fcf549867631dd98b706499c17108b5125`

The canonical BCPL `COBOOT` executes
`C := FN(COWAIT(C)) REPEAT`. This suggests that an ordinary
worker return is passed to its parent through a wait, and
the next call invokes the worker again rather than permanently
terminating the coroutine. This is a research hypothesis,
not a native ABI or exceptional-termination contract.

The standalone candidate source
`mr10-kit-compiler/tests/10-coroutines/co0-worker-return-reentry-candidate.bcpl`
uses an existing 401-word arena, normal `CREATECO`, two
`CALLCO` operations and a final `DELETECO`.
It imports the existing canonical GETVEC and COROUTIN modules.

Predicted ordered output (**NOT an accepted golden**):

    WORKER ENTER 10
    ROOT GOT 110
    WORKER ENTER 20
    ROOT GOT 120
    DELETE TRUE

Execute using `tools/mr10/compile-and-run --results`
with `mr10-kit-compiler/asm/icintv19.asm`, this new source,
and separate `+mr10-kit-compiler/library/getvec-freevec.bcpl`
and `+mr10-kit-compiler/library/coroutines.bcpl` arguments.
The job must compile all three BCPL modules and preserve its
JES report, runner RC, all interpreter CODE values and complete
ordered output. Expect fourteen JES steps and seven interpreted
compilation/codegen/run phases. Do not conflate zero JES return
codes with semantic correctness.

No installation, accepted golden changes, manifest changes,
native global allocation, or milestone closure.
