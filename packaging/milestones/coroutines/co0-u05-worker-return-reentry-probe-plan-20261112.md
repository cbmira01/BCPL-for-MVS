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

## JOB 5323 compiler failure and isolated correction

On 12 November 2026 at baseline
`9d547b2967a8bcabde42505955425aaabb8977ed`,
JOB **5323 (BCCO0WOR)** compiled unit 1 with interpreted
`CODE=8`: `SYNTAX ERROR NEAR LINE 45: ERROR IN COMMAND`
at the candidate source's standalone `ELSE` after an `IF ... DO`.
The wrapper returned **RC=2**. All 14 JES steps returned
RC=0000 and the JES summary reported SUCCESS, but these
do **not** imply that the BCPL source compiled. The
subsequent invalid INTCODE execution is downstream of the
compiler failure; no worker-lifecycle evidence was obtained.

The corrected candidate evaluates `DELETECO(CO)` once,
stores its result in `R`, then uses two independent
`IF ... DO` commands (one for nonzero, one for zero).
This follows syntax exercised by accepted MR10 BCPL tests
and preserves the original positive and negative diagnostic
messages. Source-only validation checks structural consistency,
line widths and supported conditional shape; MVS compilation
and runtime behavior remain **UNVERIFIED** pending rerun.

## JOB 5324 — accepted bounded normal-return/re-entry evidence

On 12 November 2026 with GitHub source revision
`b6f88b3cdd3b3e634a941b128694122b818fe49d`,
the corrected candidate ran under canonical ICINT19/ICLIB and the
separate GETVEC and COROUTIN BCPL modules.

**JOB 5324 (BCCO0WOR)** produced, in order:

    WORKER ENTER 10
    ROOT GOT 110
    WORKER ENTER 20
    ROOT GOT 120
    DELETE TRUE

The final interpreted run reported **3237 cycles, CODE=0**;
`compile-and-run --results` returned RC=0. The separate operator
`tools/mvs/job-summary 5324` returned RC=0,
`JOB RESULT: SUCCESS`, highest RC=0000 and all
**14/14 JES steps RC=0000** (ASM, LKED, STGSYNI, STGTRNI,
STGCGI, STGBLIB, STGICLIB, COMP01, CG01, COMP02, CG02,
COMP03, CG03, RUN).
Local operator log:
`workarea/co0-u05-worker-return/20261112T014222Z.log`.

**Accepted scope: INTERPRETED-MVS-TESTED for this bounded normal
worker-return/re-entry and deletion path.** The repaired candidate
does not become an accepted manifest test. JOB 5323 remains a
failed-compilation historical observation and is not counted as a
behavioral pass. No conclusion is drawn about exceptional worker
termination, out-of-memory handling, stale pointers, stack overflow
or native System/370 lifecycle behavior.
