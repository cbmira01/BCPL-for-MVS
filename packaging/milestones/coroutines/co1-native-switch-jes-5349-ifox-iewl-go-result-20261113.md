# CO.1 — Isolated native context transfer: JOB 5349 IFOX/IEWL/GO PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026
**Execution source revision:** `cd5b4d1e9e9162e83c5be594b783e76ac2ad217c` (required by the owner-executed guarded command)
**Evidence class:** OWNER-REPORTED REAL NATIVE-MVS-TESTED **ISOLATED TEST-ONLY CONTEXT TRANSFER**; saved JES/GO logs not independently examined here
**Disposition:** JOB 5349 PASS, native smoke runner RC=0
**Milestone status:** CO.1 IN PROGRESS, owner design gate OPEN; CO.2–CO.5 NOT STARTED

## Actual owner-reported execution

The owner ran the guarded command previously supplied for `tools/coroutines/run-co1-native-smoke.py --run`. It required a successful fast-forward pull and a local Git HEAD equal to `cd5b4d1e9e9162e83c5be594b783e76ac2ad217c` before executing the runner. The owner supplied:

```text
CO.1 NATIVE PASS: JOB 5349, IFOX 2, IEWL 1, GO 1; A1 B1 A2 B2 PASS
CO.1 NATIVE evidence: workarea/co1-native-switch/20261113T150704Z-57vfyna4
CO.1 native IFOX/IEWL/GO RC=0
```

**Preserved operator-host evidence:** `workarea/co1-native-switch/20261113T150704Z-57vfyna4/`. The versioned runner retains `candidate.jcl`, `submission.log`, `printer.cursor`, `job-summary.log`, `job-report.log`, and `result.json`. These local receipts were **not uploaded or independently inspected** during this checkpoint. The successful runner output is the evidence basis; no further JES submission or installed-dataset operation was performed here.

## Acceptance basis and demonstrated mechanism

The [isolated candidate implementation and test plan](co1-native-switch-candidate-20261113.md) records two separate IFOX control sections, `CO1SW` (register-context transfer) and `CO1ROOT` (root/A/B test driver). The runner builds and submits exactly one temporary-dataset-only job `CO1NAT`, then requires:

1. Job identity `JOB 5349 CO1NAT`, completed JES success and **highest RC 0000**.
2. Exactly four named executed steps `ASMSW`, `ASMTST`, `LKED`, `GO`, **each RC 0000**. The assembler steps are IFOX00, and the link-edit step is IEWL.
3. The exact five ordered GO output records: `CO1STAGE A1`, `CO1STAGE B1`, `CO1STAGE A2`, `CO1STAGE B2`, `CO1STAGE PASS`; no extra `CO1STAGE` records.

The observed `CO.1 NATIVE PASS` output is produced only after these source-defined acceptance checks return normally; the wrapper then exits RC=0. Thus JOB 5349 is **native execution evidence**, not a compiler-only structural oracle.

The candidate `CO1SW` saves outgoing R0–R15 into the outgoing context's 16-word register image, stores a transferred value in the incoming context's R7 slot, restores the incoming R0–R15, and transfers control through the restored R6. The driver first enters separate A/B continuations and subsequently resumes them, checking each private R5 frame pointer, frame-local word, and transferred value before printing PASS. This is direct machine-code evidence of **cooperative context suspension/resumption across two test contexts and return to root**.

## Scope restriction and design transfer

This is a **test-only isolated machine-code switch**, *not* the approved, BCPL-callable `CHANGECO` Core Runtime interface. Its test convention uses R2 = outgoing context image, R1 = incoming image and R0 = transfer value; those are **not** approved public ABI assignments. The driver is assembler-only and uses statically allocated private frame/workspace regions. It does not run a generated BCPL coroutine, establish independent checked BCPL stacks or validate the synthetic BCPL caller frame and `RETIMPL` worker-exit path.

No production `STKLIM` / `BCPLAPT APLIMIT` transitions, PSW/condition-code preservation, descriptor validation, lifecycle semantics, public global-number registration, native library import, stack reclamation, or complete regression were tested. No accepted `BOOT_OBJ` or other resident MVS object was replaced. These remain CO.1 design and later-march verification obligations.

**Engineering direction after this result:** stop adding compiler-only microprobes. Review a minimal BCPL-callable switch interface and first-activation/exit frame, select the owner-gated S1 stack-bound transition and registration contract, then implement/test an isolated native BCPL plus IFOX/IEWL/GO candidate. Record owner design approval before declaring CO.1 CLOSED or beginning accepted CO.2 implementation.

**CO.1 IN PROGRESS; owner design gate OPEN; CO.2–CO.5 NOT STARTED.**
