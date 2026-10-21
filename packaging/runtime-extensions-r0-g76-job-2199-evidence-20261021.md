# Milestone Runtime Extensions — R.0 installed G!76 precedence, JOB 2199

**March:** R.0 — Evidence and contract (**open**).
**MVS evidence:** Owner-supplied console transcript of JOB **2199**
(`R0G76`), 21 OCT 26, 01:39:13–01:39:14.
**Tracked probe revision:** `d733410ffd4f5c1eba1c4a0fcc915305c147aef7`.
**Disposition:** **PASS**, specifically for **BLIB-present G!76**
precedence, accepted as R.0 evidence by the owner. **Not** R.0
closure, generic collision checking, or optional-package registration.

## Reproduction and test meaning

The operator used `git pull --ff-only` and ran the
[committed G!76 precedence probe](../bootstrap-toolchain/probes/r0-g76-precedence-probe/README.md):

```sh
bash bootstrap-toolchain/probes/r0-g76-precedence-probe/run.sh
```

All **seven** local Python tests passed. The credential-free synthetic
generator check reported **105 cards**. **JOB 2198**
(`R0G76C`) compiled the test application using the installed
interpreter-hosted **demoted Cambridge compiler**, saving generated
CG370 assembler to `workarea/runtime-extensions-r0-g76/app.s370.asm`.
The generated assembler dry-run produced **150 JCL cards**, then
JOB **2199** was submitted through the JES reader.

The test-only job assembles the native BCPL application and `R0CK76`
verifier separately. Its IEWL input explicitly includes the installed
`BOOT_OBJ(BCPLMAIN)`, `BOOT_OBJ(BLIB)`, and existing core object
members **read-only**. IEWL writes a temporary `&&` load module, not
an installed object. The application is given a temporary G!151
export pointing to `R0CK76`; G!151 is **not allocated** to an
optional package by the Global Number Registry.

The real native BCPL `START` calls `R0CK76`, which reads the
**relocated installed BLIB export trailer**, locates G!76 (WRITEF),
and compares its function address against the initialized
**R12+304 = G!76** global vector entry. A mismatch or missing
entry results in error and STOP(8); equality returns success,
prints the unique marker, and finishes normally.

## Actual JOB 2199 results

| Job step | Program | Observed result |
| --- | --- | --- |
| ASMA | IFOX00 | RC=0000 |
| ASMP | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Temporary native BCPL application | RC=0000 |

**JOB RESULT: SUCCESS**; highest RC **0000**;
zero assembler statements flagged; assembler severity **0**.
**152** cards, **427** SYSOUT records.

The separate report verifier confirmed the following exact
**actual GO output** (not merely a string in the source listing):

```text
R0 G76 INSTALLED BLIB PASS
```

Together with the [JOB 2197 actual export
ledger](runtime-extensions-r0-trailer-job-2197-evidence-20261021.md),
this verifies one narrow historical precedence rule:
**when installed BLIB exports G!76, the installed BCPLMAIN preserves
BLIB's WRITEF address at START** instead of replacing it with the
provisional `WRITEST` fallback.

## Evidence limits / outstanding R.0 work

- The **BLIB-absent** fallback branch was **not tested**. Do not
  conclude that it installs `WRITEST` correctly when G!76 is unset.
- The detailed JOB 2199 IEWL **MAP/XREF was not presented or reviewed**
  in this exchange. Link-edit RC=0000 and runtime address equality
  were observed; no relative CSECT positions are asserted.
- Installed `BOOT_OBJ` **object-build provenance** remains unverified;
  neither this job nor a freshly compiled application identifies the
  precise source revision of previously installed core or BLIB objects.
- The test-local G!151 injection is not an extension-slot assignment.
- This is **not** a test of pre-START optional registration, collision
  rejection or transactional rollback; no R.1 integration occurred.
- Decision G still needs owner-reviewed numeric maxima and stable
  diagnostics. A final R.0 acceptance review also remains.

Owner-local evidence files (ignored, not committed):
`workarea/runtime-extensions-r0-g76/job-2199.txt`,
`r0-g76.jcl`, `app.s370.asm`, `provenance.txt`.
Do not commit credential-bearing generated JCL or raw printer logs.

**Status:** **BLIB-present G!76 precedence test complete. R.0 open.
R.1 — Generic registration foundation not started.**
