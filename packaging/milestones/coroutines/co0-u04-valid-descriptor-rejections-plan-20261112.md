# CO.0 — U04 valid-descriptor rejection candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Baseline:** GitHub `main` at `b6f88b3cdd3b3e634a941b128694122b818fe49d`  
**Status:** SOURCE-OBSERVED; MVS candidate NOT EXECUTED

## Safety boundary

This is a bounded **valid/live descriptor and null-delete** probe.
It does not supply a stale, freed, unmapped, malformed or arbitrary
nonzero pointer to `CALLCO`, `RESUMECO` or `DELETECO`.
These paths dereference descriptors without proving liveness;
no assumption of safe validation of arbitrary addresses is made.

Source-derived guard behavior in canonical
`mr10-kit-compiler/library/coroutines.bcpl`:

- `DELETECO(0)` and `DELETECO(CURRCO)` return FALSE.
- `CALLCO(CPTR,A)` returns -999 if `CPTR!1 != 0`.
- `RESUMECO(CPTR,A)` returns -998 if `CPTR!1 != 0`,
  before clearing the current parent (the U03 repair).

The candidate root is a valid local vector, registers itself
as `CURRCO` and `COLIST`, and sets `ROOT!1=-1`.
After the rejected calls it checks unchanged parent state and
then exercises ordinary `CREATECO`, `CALLCO`, `DELETECO`
against a separately allocated live worker.

**Predicted exact output (hypothesis, NOT a golden):**

    DELETE NULL 0
    DELETE CURRENT 0
    CALL BUSY ROOT -999
    RESUME BUSY ROOT -998
    ROOT PARENT -1
    WORKER RESULT 11
    DELETE WORKER -1

## Gate

Compile the standalone
`mr10-kit-compiler/tests/10-coroutines/co0-valid-descriptor-rejections-candidate.bcpl`
with canonical ICINT19/ICLIB and the separately compiled
`getvec-freevec.bcpl` and `coroutines.bcpl` modules.
A passing observation requires all seven ordered lines,
seven interpreted compiler/code-generator/run phases CODE=0,
runner RC=0 and 14/14 JES steps RC=0000. Capture independent
`job-summary` after the job. These are expectations only:
the new candidate has not yet been run under MVS.

No permanent dataset staging, canonical runtime edit, accepted
manifest change, native-global assignment or CO.1 design decision.
