# CO.1 — Isolated native context transfer: first executable candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture (IN PROGRESS)
**Date:** 13 November 2026
**Basis:** GitHub `main` at `0afba0f64e1825439f4738642c77aedcfd74505e`
**Evidence:** SOURCE-OBSERVED plus ASSISTANT HOST-TESTED; MVS IFOX/IEWL/GO PENDING
**Decision status:** Candidate-only isolated native execution experiment; no approved production `CHANGECO` ABI, no CO.2 opening or acceptance.

## Why this candidate, now

After JOBs 5345–5348, further compiler-only probes are not prerequisites to writing native code. The code generator's R4/R5/R6/R7 convention, checked entry, indirect-call loading and return order are sufficiently established to exercise an **actual native register-context transfer**. The next unknown should be resolved by **MVS execution**, not another speculative source oracle.

The [milestone contract](milestone-implement-coroutine-support-for-native-compiler.md) still requires owner approval of the production descriptor, stack safety, globals, lifecycle and API before CO.2. This candidate deliberately avoids those decisions. It is a runnable, disposable **CO.1 native ABI experiment**, not a proposed installed Core Runtime component.

## Working candidate, not a public interface

`candidates/co1-native-switch/co1switch.asm` defines a tiny standalone IFOX `CO1SW` control section. The **test-only** handoff convention is:

| Register | Candidate meaning |
|---|---|
| R2 | Outgoing aligned 64-byte, 16-register image |
| R1 | Incoming aligned 64-byte, 16-register image |
| R0 | New BCPL result to inject into incoming saved R7 |
| R6 | Outgoing continuation established by `BALR 6,4`; incoming saved continuation |
| R5 | Context's own BCPL-style frame pointer, restored from its image |
| R4, R7–R15 | Restored alongside the other general-purpose registers |

Its entire transfer sequence is real System/370 assembler:

```asm
         STM   0,15,0(2)
         ST    0,28(1)
         LM    0,15,0(1)
         BCR   15,6
```

The incoming register image can be seeded with a first-entry R6 and private R5/R15, or can contain the R6 continuation saved during an earlier switch. R7 is deliberately overwritten with the incoming transfer value. This test does **not** establish preservation of condition codes/PSW, handle validity, runtime stack limits, ownership, MVS storage acquisition, or final live-register requirements. Saving all 16 GPRs here simplifies the first machine-code test; the production save set remains a design decision.

`candidates/co1-native-switch/co1native.asm` is a separate MVS program that uses the switch symbol through IEWL external resolution. It initializes **root, A, and B** register images, with distinct A/B frame and workspace storage. The root enters A; A enters B; B resumes A; A resumes B; B resumes root. A and B verify their distinct R5 frame pointers, saved local frame words and transferred R7 values. The GO program prints exactly:

```text
CO1STAGE A1
CO1STAGE B1
CO1STAGE A2
CO1STAGE B2
CO1STAGE PASS
```

Any wrong continuation, result, private frame value, or frame pointer takes the `CO1STAGE FAIL` path and returns nonzero. The A/B image and frames are static **only in this private test**; they are **not** independently bounded BCPL coroutine stacks. The driver shares an MVS save area only while no MVS service is suspended. That pattern is not a production coroutine stack-allocation proposal.

## MVS execution and evidence contract

The versioned `tools/coroutines/run-co1-native-smoke.py --run` generates one **temporary-data-set-only** JCL job named `CO1NAT`:

1. `ASMSW` — assemble `co1switch.asm` with IFOX00;
2. `ASMTST` — assemble `co1native.asm` separately with IFOX00;
3. `LKED` — IEWL links both objects into a temporary load module, resolving `CO1SW`;
4. `GO` — execute the temporary module and write the five records to JES SYSOUT.

The script uses the existing `tools/mvs/submit-jcl`, `tools/mvs/job-summary` and `tools/mvs/dump-report-for-job`, with a fresh printer cursor. It accepts **only** all four JES steps at RC=0000 with overall zero-RC success **and** the exact five ordered GO records. There is no reliance on old JES jobs, raw assembler listing text masquerading as output, or a GO RC alone. It creates a unique `workarea/co1-native-switch/<UTC>/` containing the inlined JCL, submission log, full job summary, full report, printer cursor and machine-readable `result.json`. The operator console prints only a short PASS/FAIL, JOB number if available, and evidence directory.

All object/load-module data sets are `&&` temporaries. `SYS1.MACLIB` is read-only. The test **does not stage, overwrite or install** any `BOOT_OBJ`, `DEVOBJ`, `OBJ`, other resident PDS, or BCPL runtime source. Existing regression manifests, case numbers and accepted baseline stay unchanged.

## Assistant-side verification and next gate

**Host-only:** 25/25 Python unit tests PASS, including two fake end-to-end runs with a **synthetic JOB 8127 (not actual JES)**; Python syntax PASS; assembler cards are ASCII and within column 71; source checks and generated JCL shape/column checks pass. The tests exercise missing and nonzero assembler/link/GO results, duplicate/missing/out-of-order native records, hidden assembler source literals, and retained failure evidence. These checks **do not** assert that IFOX has accepted the new source.

**MVS PENDING:** the owner may run exactly one guarded `CO1NAT` job using the committed runner. The first IFOX/IEWL/GO result must be classified by actual JES evidence. A failure should be addressed from the retained assembler listing/JCL diagnostics—not by starting another round of independent compiler-only probes. A PASS would establish this minimal **test-only context transfer**; it would **not** promote the switch to the production `CHANGECO` ABI.

**After native evidence:** review the public call interface, first-worker synthetic return frame, BCPL/assembler integration, Approach A descriptor ownership, owner-selected S1 stack switching (both `STKLIM` and `BCPLAPT APLIMIT`), global registry and diagnostics. Record explicit owner design approval before entering CO.2.

**CO.1 IN PROGRESS; owner design gate OPEN; CO.2–CO.5 NOT STARTED.**
