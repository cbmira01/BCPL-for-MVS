# CO.1 — Checked worker entry and normal return: JOB 5348 compiler-only result

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026
**Compiler probe source revision:** `26fa545a2ce5f24550ea2be4e07e4a6d3cf1b9ff` (required by the owner's previously supplied guarded command)
**Classification:** OWNER-REPORTED REAL MVS COMPILER-ONLY EMISSION EVIDENCE; no independent inspection of saved assembler or JES/compiler reports
**Result:** Worker-entry source-and-textual-code oracle PASS; JOB 5348, compiler-only RC=0
**March status:** CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED

## Owner-reported MVS outcome

The owner supplied this output after the guarded invocation of `tools/bootstrap/probe-co1-worker-entry.py`:

```text
CO.1 WORKER PASS: JOB 5348, entries 0/1/2, calls 3, checked 3; compile-only
CO.1 WORKER evidence: workarea/co1-worker-entry/20261113T140130Z-ket74q9d
CO.1 worker compile-only RC=0
```

The source-revision guard in the preceding command required local HEAD `26fa545a2ce5f24550ea2be4e07e4a6d3cf1b9ff` after `git pull --ff-only`. The stored owner-host evidence directory is `workarea/co1-worker-entry/20261113T140130Z-ket74q9d/`, containing `compiler.log`, `generated.s370.asm` and `summary.json` according to the tracked runner. Those files were **not supplied to the assistant and were not independently examined**. No additional compiler submission, report fetch, installed MVS modification or local-checkout operation was performed as part of this documentation checkpoint.

## Meaning of the verified probe result

The tracked fixture defines `WORKER(ARG) = ARG+1`, `INVOKE(F,VALUE) = F(VALUE)` and `START()` calling `INVOKE(WORKER,41)`. It uses `CAMBCOMP` through `ICINT19` with an 80-column `/CN` record, which requests checked entries and disables deck output. The wrapper requires an original compiler driver RC=0 and one identified JES job; it does **not** invoke IFOX, IEWL or native GO.

A PASS requires the recovered generated System/370 text to meet these structural checks:

- Exactly one zero-argument `STM 4,6,0(15)`, one one-argument `STM 4,7,0(15)`, and one two-argument `STM 4,8,0(15)` prologue.
- Exactly **three +60** checked entries, each adjacent to its prologue and one inline fullword with a unique defined, positive, word-aligned frame size.
- One normal `BCR 15,11` return in the bounded one-argument worker region; one `BALR 6,4` inside the two-argument `INVOKE` region; and at least three ordinary calls overall.
- No +20/+80 counting-service entries. Independently, the **tracked** `BCPLMAIN` source must contain the expected `RETIMPL` restore sequence `L 6,8(5)` / `L 5,4(5)` / `L 4,0(5)` / `BCR 15,6`, and `STKIMPL LR 5,15`.

The observed output reports all three expected argument-count entries, exactly three checked entries, three calls, JOB 5348 and RC=0. It does **not** provide the individual generated frame lengths or the raw instruction listing. The `RETIMPL` assertion applies to versioned source, **not independently to the resident linked object**.

The fixture's mathematical result would be 42 if executed, but **no native execution of 42 is reported**.

## Boundary and disposition

This upgrades the [previous compiler-only probe preparation checkpoint](co1-checked-worker-entry-and-return-source-probe-20261113.md) from MVS-pending to **owner-reported JOB 5348 compiler-only PASS**. The earlier checkpoint remains the historical preparation record. The recorded output is not acceptance of a synthetic first-activation frame or of a machine-dependent coroutine switch.

Still unapproved: E1/E2 switch-entry choice, first-worker caller-frame layout and exit continuation, full R4–R15 and PSW condition-code preservation, R7 transfer semantics, descriptor ownership, Approach A validity/lifecycle detail, S1 `STKLIM` plus `BCPLAPT APLIMIT` coordination, G54/G55 diagnostics, global assignments, and any candidate native IFOX/IEWL/GO sequence. The governing [CO.1 milestone](milestone-implement-coroutine-support-for-native-compiler.md) requires owner review before CO.2.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
