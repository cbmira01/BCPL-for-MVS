# CO.1 — JOB 5350/5351 IFOX failure and source correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (IN PROGRESS)  
**Date:** 13 November 2026  
**Status:** Owner-reported real MVS failure; assistant-checked corrective
source committed for a *new* MVS execution. No native PASS claimed.

## Observed MVS evidence

From the owner's retained
`workarea/co1-bcpl-switch/20261113T171044Z-2xgigtbh/`
receipt and JES summary, running GitHub main
`42b8da45e78f254d765057d6156153e96e05af1e`:

- **JOB 5350:** Resident Cambridge compiler driver RC=0; generated
  S/370 source SHA256 `f08f9eb366bdcd0b360cb736859c1b378c483a31028920b5ad4c4b0eae347e3e`.
- **JOB 5351 CO1BGO:** ASMA (compiled BCPL) RC=0000;
  ASMM (private BCPLMAIN) RC=0000;
  **ASMS (CO1CHG) RC=0008**; LKED and GO not executed.
- JES job result FAILURE, highest RC 0008. The secondary
  `IEF221I` referencing a nonexistent GO load step follows the
  bypassed LKED; it does not establish a standalone source-JCL defect.
- The filtered owner excerpt reports IFOX severity 8 and no
  flagged-statements count, but **does not include the specific ASMS
  source diagnostic**. The source-level identification below is therefore
  a compelling hypothesis, **not a verified attribution to a particular
  IFOX message**.

## Corrective source investigation

The separately assembled `co1change.asm` defined
`CO1RETURN` (nine characters) as the resume trampoline label, and
referenced it with `=A(CO1RETURN)`. IFOX System/370 assembler labels
are at most eight characters. That is a concrete source defect.

The candidate correction renames both occurrences to `CO1RET` and
adds a candidate-module-only assembler-label length/alphabet check
to `tools/coroutines/run-co1-bcpl-switch.py` before JCL submission.
A negative host test recreates `CO1RETURN` and requires preflight
rejection, including during `build_deck`.

Assistant-side static source audit found 11 defined labels, all within
eight characters, and no source card beyond column 71. Six focused
Python host tests of the *exact corrected switch source blob* passed,
including the original-label negative case, illegal alphabet, invalid
cards, JCL delimiters, and noncandidate behavior. The checked local
`co1change.asm` Git blob SHA was
`0a677d47d6ab8e5133ddbd109d54f61a064d08f8`.
These checks do **not** constitute IFOX or native runtime verification.

## Next native checkpoint

Run the same isolated
`tools/coroutines/run-co1-bcpl-switch.py --run` job, using the
corrected GitHub commit. Require real RC=0 for ASMA, ASMM, ASMS, LKED
and GO, and the five ordered `CO1BCPL` output records. If ASMS still
fails, preserve its full IFOX listing; if linkage or GO fails, investigate
that new observed result. Never overwrite accepted BOOT_OBJ members.

No MR10-kit changes, no public global-number allocation, no numbered
regression additions, no installed MVS object promotion, and no CO.1
closure are authorized or claimed by this correction.
