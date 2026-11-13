# CO.1 — CK-C: isolated checked-plus-counted CG370 compile-only probe

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026 (Louisville); the local smoke directory used 13 November UTC
**Reviewed repository HEAD:** `ee04696b7e2a85e089747ceb27e9f65feb1de043`
**Status:** CK-C probe PREPARED AND LOCALLY TESTED; actual MVS compilation NOT YET OBSERVED
**Evidence classification:** SOURCE-OBSERVED and HOST-ONLY TESTED, not IFOX/IEWL/GO/JES acceptance

## Purpose and existing authority

The [CG370 checked-entry option matrix](co1-cg370-checked-entry-option-matrix-20261112.md) identified the combined `/CK` path at system-vector +80, with two inline metadata words, while current `STKCIMP` consumes only one and omits frame establishment and bounds checking. The owner-reported [CK-B production baseline](co1-ck-b-native-checked-stack-production-baseline-20261112.md) passed four tests (49–52) in the existing **+60 checked-only** path. CK-C isolates **compiler emission only**, without executing the incompatible runtime service. The [milestone](milestone-implement-coroutine-support-for-native-compiler.md) still requires an approved design before native implementation.

## Canonical inputs, execution boundary and provenance

| Asset | Purpose |
| --- | --- |
| `tests/bootstrap/51-checked-recursion/source.bcpl` | Existing, unchanged two-procedure native test source (START and DEPTH, including a recursive call) |
| `packaging/milestones/coroutines/probes/co1-ckc/cambridge-parm.txt` | Single 80-column Cambridge option record: `/CKN` followed by 76 additional slashes |
| `tools/bootstrap/compile-mvs` | Existing MVS-facing resident compiler driver, running pinned `CAMBCOMP` under `ICINT19` and recovering textual System/370 CODE |
| `tools/bootstrap/probe-co1-ckc.py` | Isolated one-job compile-only orchestrator and automatic emitted-code verifier |
| `tools/checks/test_co1_ckc_compile_only.py` | Eleven host-only tests for the generated-code verification conditions |

`/CKN` means `C` stack checking, `K` call counting, and `N` suppress the binary deck in the code-generator option phase. The extra slashes terminate/pad the existing CAMBPARM record consistently with the accepted `/CN` fixtures. The runner uses the existing `compile-mvs` `--cambridge-parm` injection, preserving source data and resident MVS datasets.

**Hard boundary:** The runner invokes only `compile-mvs`. Its job performs `ICINT19` compilation and `IEBGENER` textual CODE recovery, not IFOX, IEWL or native GO. It must **not** feed the generated +80 code into the current runtime. It does not modify compiled source, manifests, tests 00–176, existing run logs or installed MVS objects. The generated assembler is evidence and remains unexecuted.

## Automatic CK-C acceptance oracle

The runner requires a successful Cambridge compiler driver result, one unambiguous JES job number, and a nonempty recovered assembler listing. It then asserts:

1. At least **two** generated `BAL 14,80(11)` entries, each immediately followed by **`DC F'0'`** and **`DC A(Lnnn) STACK FRAME SIZE`**.
2. All +80 entries match that exact two-word structure, and no +60 checked-only entry appears in the candidate.
3. Every referenced `Lnnn EQU positive-number STACK FRAME SIZE` has exactly one definition and a positive four-byte-aligned frame size.
4. At least one normal `BALR 6,4` call remains present.

These are intentionally strict **textual CODE oracles** for the selected historical source and compiler-output shape. Their success establishes the **emitted ABI shape**, not runtime correctness, call-count semantics or continuation state. A format drift or failed MVS compile is FAIL/BLOCKED evidence, not permission to run or patch the +80 service.

## Quiet operator interface and preserved artifacts

A single MVS-facing invocation is sufficient once the GitHub checkout has been updated:

```text
python3 tools/bootstrap/probe-co1-ckc.py
```

The wrapper prints only a concise **CK-C PASS/FAIL**, the compiler JOB number on PASS, and the relative evidence directory. Full generated assembly is **never dumped to the WSL console**.

Each run creates a new `workarea/co1-ckc/<UTC-time>-<unique>/` directory with `compiler.log`, `generated.s370.asm` on successful compilation, and `summary.json`. On failure, existing logs and metadata are retained. `summary.json` records the local checkout HEAD, source and parameter hashes, compiler-driver RC, job ID when available, frame-size findings, and explicitly `assembled:false`, `linked:false`, `native_go:false`. The assembler stream is recovered locally, not promoted or installed on MVS.

## Verification performed before commit

- `python -m unittest discover -s tools/checks -p 'test_co1_ckc_compile_only.py' -v` in the isolated assistant workspace: **11/11 PASS**, including valid two-entry output and rejection of missing/extra frame metadata, invalid sizes, missing calls, missing +80 branches and mixed +60/+80.
- `python -m py_compile` on both Python files: **PASS**.
- **Host-only simulated end-to-end smoke:** a deliberately fake `compile-mvs` wrote two well-formed +80 entries and printed a synthetic JOB 8472; the wrapper reported PASS, saved `summary.json` with two entries, and left `native_go=false`. **JOB 8472 is a test stub, NOT an MVS JOB receipt.**
- The three staged GitHub blobs for the script, tests and parameter fixture were independently checked against the locally tested `git hash-object` values. No production MVS compilation or CK-C result is claimed yet.

The actual target-dependent CK-C result is pending the owner's MVS-facing invocation. After that, inspect the saved `summary.json` and, if needed, the generated assembler **without printing the whole listing**. Preserve the exact execution HEAD and JOB ID before recording any native compilation acceptance.

**CO.1 IN PROGRESS; owner-reviewed design gate OPEN; CO.2–CO.5 NOT STARTED.**
