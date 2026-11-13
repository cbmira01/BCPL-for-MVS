# CO.1 — CK-C compile-only result: JOB 5342

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026 (Louisville); evidence directory dated 13 November UTC
**Execution revision:** `2aa2058e50eb26b79f2a0f173f2e9669f8ed624c`, guarded by the owner's WSL command
**Evidence class:** OWNER-REPORTED REAL MVS COMPILER-ONLY PROBE; local compiler/JES logs not independently inspected
**Disposition:** CK-C PASS at reported-probe level; CO.1 IN PROGRESS, design gate OPEN; CO.2–CO.5 NOT STARTED

## Exact reported result

The owner executed the CK-C command from [probe preparation](co1-ck-c-compile-only-probe-preparation-20261112.md) after a guarded quiet GitHub pull; the shell only invoked the probe if HEAD equaled `2aa2058e50eb26b79f2a0f173f2e9669f8ed624c`. The supplied console transcript records:

```text
CK-C PASS: JOB 5342, +80 entries 2; compile-only
CK-C evidence: workarea/co1-ckc/20261113T013333Z-yv1f65e9
CK-C MVS probe RC=0
```

Evidence directory: `workarea/co1-ckc/20261113T013333Z-yv1f65e9/` on the owner's WSL host. The probe writes `compiler.log`, `generated.s370.asm` and `summary.json`. Their contents have **not been uploaded or independently examined**. This record relies on the operator console result plus the GitHub-tracked probe's implementation.

## Source-backed result interpretation

The checked-in `tools/bootstrap/probe-co1-ckc.py` invokes `tools/bootstrap/compile-mvs` with the unchanged native Bootstrap 51 BCPL source, compiler image `CAMBCOMP` and isolated `/CKN` option fixture. The compiler driver submits the `ICINT19` job with `max_rc=0`, requires interpreted compiler CODE=0, and recovers textual System/370 assembler. The probe accepts only driver RC=0, one recognized JES job identifier, and a successful assembler-text verification.

Its verification requires at least two **complete** `BAL 14,80(11)` entries. Each must be immediately followed by `DC F'0'` and `DC A(Lnnn) STACK FRAME SIZE`, with exactly one positive, four-byte-aligned frame-size `EQU` per referenced label. A `BALR 6,4` must occur, and the generated code must contain no +60 checked-only entry. **JOB 5342, two +80 entries and RC=0** are the owner-reported results for those checks. The individual frame-size values, stored `summary.json.git_head`, and detailed JES step RCs are **not independently verified** in this record; no claim of such verification is made.

## Critical limitation and next gate

This is **compiler-emission evidence only**. CK-C does **not** run IFOX, IEWL, native GO, coroutine `CHANGECO`, independent worker stacks, or the current defective `S.STKCKCOUNT` +80 entry service. As established in the [CG370 option matrix](co1-cg370-checked-entry-option-matrix-20261112.md), the current `STKCIMP` does not set R5, does not enforce `STKLIM`, and skips only one of the two inline fullwords. CK-C PASS therefore does not demonstrate correct runtime behavior.

Next, obtain owner-reviewed CO.1 design decisions on support for historical `/CK`, ownership of the +80 service, counter semantics, complete frame/continuation preservation, and S1 stack-limit integration. Only an separately approved candidate correction may proceed to IFOX/IEWL/GO under MVS; no execution of the present +80 stub is authorized by this result.

No code, suite manifests, permanent datasets, or installed objects are changed in this evidence-only checkpoint.
