# CO.1 — Checked four-argument/nested-call ABI: JOB 5345

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026 (Louisville)
**Probe source revision:** `f09bdf8e63b063b934b9b1ffda42a4c3e99b7b4e` (required by the owner's guarded WSL command)
**Evidence class:** OWNER-REPORTED REAL MVS COMPILER-ONLY PROBE; local generated assembler/JES receipts not independently inspected
**Disposition:** Probe PASS; CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED

## Recorded operator evidence

After displaying `git status` and `git branch`, the owner ran the guarded MVS-facing command from [the ABI probe preparation](co1-native-four-argument-nested-call-checked-abi-probe-20261112.md). It submitted the probe only after a successful quiet fast-forward GitHub pull and a HEAD equality check against `f09bdf8e63b063b934b9b1ffda42a4c3e99b7b4e`. The submitted branch produced:

```text
CO.1 ABI PASS: JOB 5345, four-arg entry 1, checked entries 3, calls 3; compile-only
CO.1 ABI evidence: workarea/co1-native-call-abi/20261113T075334Z-aprk7_km
CO.1 ABI compile-only RC=0
```

**Owner WSL evidence location:** `workarea/co1-native-call-abi/20261113T075334Z-aprk7_km/`. The versioned probe writes `compiler.log`, `generated.s370.asm`, and `summary.json`; these files were not supplied and have not been independently read. Detailed frame sizes and individual JES step return codes are therefore not claimed.

## Interpretation of the tracked compiler-only oracle

`tools/bootstrap/probe-co1-native-call-abi.py` invokes `tools/bootstrap/compile-mvs` using `CAMBCOMP`, `ICINT19`, and a private `/CN` option fixture, then verifies recovered textual System/370 assembler. The existing driver requires compiler/JES completion within `max_rc=0` and interpreted completion code zero.

The probe reports PASS only if it finds three or more complete `BAL 14,60(11)` checked entries, each with positive word-aligned inline frame size, exactly one `STM 4,10,0(15)` four-argument save, at least three `BALR 6,4` calls, an `LA 15,n(5)` frame advancement, a `BCR 15,11` return, and no +20 or +80 counting-service entries. The owner's result reports **one four-argument entry, three checked entries, three calls, and RC=0**. This supports compiler **emission structure**, not independently verified execution or register-preservation behavior.

The BCPL fixture's `SUM4/WRAP/START` computation logically yields 42, but **JOB 5345 does not establish an observed native output of 42**. No IFOX assembly, IEWL link-edit, native GO, coroutine `CHANGECO`, stack switch, or current defective +80 `STKCIMP` execution occurred.

## Untracked file, scope, and next gate

Before the run, `git status` showed `main` up to date with `origin/main`, with a root-level **untracked `FETCH_HEAD`**; `git branch` displayed `* main`. This file is **unrelated to the compiled fixture**. No deletion, staging, inspection of its contents, or `.gitignore` edit is performed here.

The [CK-D checked/counting investigation](co1-ck-d-shared-checked-entry-and-counting-investigation-20261112.md), native context-switch save set, first-activation frame, descriptor format, global allocation, S1 safe limit and `BCPLAPT APLIMIT` integration still require owner design review before implementation. The earlier probe-preparation checkpoint's pending state is superseded by this owner-reported PASS, without retroactively altering that record.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.** No runtime code, native suite manifest, historical source, MVS dataset or installed object changed.
