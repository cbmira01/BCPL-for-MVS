# CO.1 — /CPN counting-site compiler emission: JOB 5343

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026 (Louisville local date); run path dated 13 November UTC
**Execution revision:** `89e19b2a160ddc5914bf87f02895b9fd34c8544b` (guarded by owner-pasted WSL command)
**Evidence:** OWNER-REPORTED MVS COMPILER-ONLY PROBE; local JES/compiler report not independently inspected
**Disposition:** /CPN counting-site oracle PASS at probe level; CK-D design gate OPEN; CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED

## Owner-reported run and retained evidence

The owner executed the guarded command supplied after [CK-D source investigation](co1-ck-d-shared-checked-entry-and-counting-investigation-20261112.md), which first pulled GitHub `main` quietly and required HEAD `89e19b2a160ddc5914bf87f02895b9fd34c8544b` before invoking `tools/bootstrap/probe-co1-counting.py`. The pasted output from the executed branch was:

```text
CO.1 COUNT-P PASS: JOB 5343, +80=2, +20=5; compile-only
CO.1 COUNT-P evidence: workarea/co1-counting/20261113T015924Z-jv4onj2p
CO.1 /CPN MVS compile-only RC=0
```

The retained WSL evidence location is `workarea/co1-counting/20261113T015924Z-jv4onj2p/`. Per the versioned probe, it contains `compiler.log`, `generated.s370.asm`, and `summary.json`; these files were **not uploaded or independently reviewed**. The console transcript does not contain the individual `summary.json` fields, generated frame sizes, or full JES step receipts.

## Scope of this compiler-side result

The checked-in `tools/bootstrap/probe-co1-counting.py` uses the unchanged `tests/bootstrap/51-checked-recursion/source.bcpl`, private 80-column `/CPN` options, and `tools/bootstrap/compile-mvs` with the resident `CAMBCOMP` compiler image. This invokes an `ICINT19` compiler job and recovers textual System/370 assembler. The compile driver requires JES completion within `max_rc=0` and interpreted CODE=0; the probe requires its driver RC=0, one unambiguous job number, and the source-code oracle.

The probe's **PASS** means its recovered assembler passed these automatic checks: **two complete +80** procedure entries, each followed by zero counter and properly defined, positive word-aligned frame-size metadata; **five complete +20** counted-code sites, each followed by its own zero counter; no +60 checked-only entries; and at least one `BALR 6,4` ordinary call. The **2 and 5 counts** and JOB **5343** are from the operator output, and the checked conditions are traced to the versioned probe implementation—not independently confirmed by reading the retained listing.

The preceding [CK-C JOB 5342](co1-ck-c-jes-5342-compile-only-result-20261112.md) used `/CKN` and demonstrated two +80 procedure entries. This follow-on `/CPN` result supplies the additional source-specific **five +20 counted-code sites** predicted by CG370's `INSERTCOUNT` path. It does not establish a universal count for other BCPL programs.

## Important limits and decision transfer

**Compiler-only:** No IFOX, IEWL, native GO, `CHANGECO`, coroutine first activation, or active-stack switch was run. In particular, the checked-in `CNTIMPL` (+20) and `STKCIMP` (+80) Core Runtime handlers remain **skip-only stubs**, not functional call counters; +80 also fails to establish R5 and enforce the frame limit. This test does not demonstrate full native `/CP` execution or historical counting behavior.

The proposed CK-D `LA 14,4(14)` / `B STKIMPL` bridge remains a **design alternative** to restore +80 checked-entry control flow; it would not increment counters at +20/+80. Owner review is still required to decide whether the initial native target supports stub-level counted options or implements actual counting, as well as module ownership and S1 stack-bound invariants. No runtime patch, global allocation, descriptor layout, MVS dataset modification, promotion of native objects, or CO.1 closure is authorized by this evidence record.

**No further target command is necessary to record the owner-supplied CK-D probe result.**
