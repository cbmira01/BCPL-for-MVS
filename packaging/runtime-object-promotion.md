# BCPLMAIN / BCPLMEM paired object promotion

Status: **Gates A (9337), A2 (9340), C (9342) accepted; not installed**, 12 October 2026.

## Accepted basis and scope

The operator's full `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 tools/run-native-regression` panel completed 124/124 PASS. This establishes a source-mode independently linked BCPLMEM architecture, including MEMBIND automatic G6!48 publication and regression 083's source-only counter instrumentation. It is **not** an installed-object acceptance result.

Production OBJ is `HERC02.BCPL.OBJ`, FB/80, BLKSIZE=800, a relocatable deck PDS. It is explicitly excluded from `dspal populate` (`config/dspal.yaml`: `content_type: object`, `populate: false`). Do **not** pass assembler decks through `dspal put` or CP037 text processing. Existing BLIB precedent: `jcl/build-blib-object.jcl` assembles a temporary FB80 object and conditionally writes `OBJ(BLIB)` using IEBGENER. The regression installed-PDS linker includes `BCPLMAIN`, `BCPLBYTE`, `BCPLAPT`, `BCPLMEM`, and `BLIB`.

The canonical `asm/bcplmain-wip.asm` still contains inline GETVEC/FREEVEC and vector-drain state. The **accepted BCPLMEM-enabled implementation** is obtained by applying `tools/checks/externalize-bcplmem.py` to a disposable copy; install that transformed BCPLMAIN, not the unmodified monolith. BCPLMEM comes from `asm/bcplmem.asm` and exports GETVEC/FREEVEC/MEMDRAIN/MEMBIND. The source transformation also maintains BCPLMAIN startup/exit MEMBIND calls.

## Gate A: non-installing candidate assembly

A host tool generates a fresh transformed BCPLMAIN and temporary IFOX job:

```sh
python3 tools/checks/prepare-runtime-object-candidates.py
# Inspect both:
#   workarea/runtime-object-candidates/bcplmain-external-mem.asm
#   workarea/runtime-object-candidates/assemble-candidates.jcl
# Then, only if the deck looks correct:
bash tools/submit-jcl workarea/runtime-object-candidates/assemble-candidates.jcl
tools/job-summary JOBNUMBER
tools/dump-report-for-job JOBNUMBER
```

The candidate job assembles BCPLMAIN and BCPLMEM in independent IFOX steps. It creates **only temporary sequential FB80 decks** and has **no OBJ PDS DD**. Require zero assembler severity, zero flagged cards and expected ESD export/import declarations. A zero return code here does **not** prove that the pair links with applications or that a PDS member can be restored.

**Gate A evidence — JOB 9337 (12 October 2026):** Operator ran the generated BCOBCAND job on TK5. ASMMMAIN IFOX00 RC=0000; ASMMMEM IFOX00 RC=0000; VERIFY IEFBR14 RC=0000; highest RC=0000; 0 flagged assembler statements and highest severity 0. Both independently assembled candidate sources passed. The temporary FB80 object datasets were not installed in OBJ. This is **assembly acceptance**, not external-symbol resolution or execution acceptance.

## Gate A2: non-installing cross-object link check (staged, awaiting TK5)\n\nAfter Gate A, run `python3 tools/checks/prepare-runtime-object-link-probe.py`, inspect `workarea/runtime-object-candidates/link-candidates.jcl`, and submit it. This job assembles a minimal external BCPLMAIN reference, the freshly transformed BCPLMAIN and canonical BCPLMEM in three separate IFOX steps, then link-edits with the existing installed OBJ(BCPLBYTE), OBJ(BCPLAPT) and OBJ(BLIB). The production OBJ is opened `DISP=SHR` for reading only. Require all assembler steps and LKED RC=0000, verify that MEMBIND and other external references resolve from the *new* BCPLMEM CSECT, and inspect ESD/XREF. There is **no GO** and this test cannot establish functional runtime behavior; a representative running probe is still required before installation.\n\n## Gate B: lightweight reproducibility and recovery check (NOT YET ACCEPTED)

**Policy decision (12 October 2026):** A separate binary backup PDS, IEBCOPY procedure, and rehearsal of an object-member restoration are **not** prerequisites. Git-tracked source/build tooling is the authority; the MVS OBJ PDS is a derived deployment artifact. This choice deliberately accepts a longer recovery interval if deployment fails.

**Before writing anything**, record the Git commit used, clean/dirty working-tree status, generated candidate hashes, and effective PDS inventory:

```sh
git rev-parse HEAD
git status --short
sha256sum asm/bcplmain-wip.asm asm/bcplmem.asm \
  tools/checks/externalize-bcplmem.py \
  tools/checks/prepare-runtime-object-candidates.py \
  tools/checks/prepare-runtime-object-execution-probe.py \
  workarea/runtime-object-candidates/bcplmain-link-export.asm
tools/dspal stat OBJ
tools/dspal ls OBJ
```

Inspect the generated candidate and make its provenance explicit:

- **BCPLMAIN source for installation must be the externalized candidate with `ENTRY STKOVFL`**, exactly as accepted by JOB 9342. The Gate A `bcplmain-external-mem.asm` by itself lacks that extra export; installing that unmodified would regress separate BCPLAPT linkage.
- **BCPLMEM source for installation is `asm/bcplmem.asm`**. Both members must be assembled and deployed from the *same recorded candidate build*, without intervening source or transform changes. The disposable job streams assembled in previous jobs are not available for installation; the installer must assemble fresh FB80 object streams.
- The current *incumbent* `OBJ(BCPLMAIN)` and `OBJ(BCPLMEM)` must not be described as reproducible until their originating Git revision and original assembly/deployment recipe have been identified. If provenance cannot be established, record that explicitly. Recovery by *rebuilding the last known-good source revision* is a policy choice, **not proof that incumbent object bytes can be recovered**.
- Keep the source-mode baseline `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1` (124/124 PASS), plus JOBs 9337, 9340 and 9342, as known-good candidate evidence; these do not identify the prior installed object revision.

**Recovery plan (no dedicated binary archive):** Freeze further PDS member updates if either install step or installed-mode acceptance fails. Determine the last known-good reproducible revision from the recorded provenance; check out that revision in a separate worktree, build **both** runtime members through the same validated assembler/installation path, reinstall both, then rerun selected installed-mode tests. Avoid mixing members from different revisions. If the incumbent provenance is unavailable, this is a forward-repair/redeployment strategy and exact rollback is **not guaranteed**. Rebuild/reinstallation is a deliberate operator action, not automatic restoration.

The outcome of this checklist, and the decision to accept any missing incumbent provenance, must be recorded **before** the Gate D write job is submitted.

## Gate C: pre-installation executable integration (ACCEPTED, JOB 9342)

The non-installing candidate pair successfully assembled, link-edited with BCPLBYTE/BCPLAPT/BLIB from the installed OBJ PDS, and executed native regression 28 with output `42` and all five steps RC=0000. The ESD/XREF showed candidate BCPLMAIN and BCPLMEM, GETVEC/FREEVEC/MEMDRAIN/MEMBIND, and STKOVFL resolution. Detailed evidence is retained below. This does **not** prove installed PDS behavior.

## Gate D: paired replacement (NOT YET IMPLEMENTED)

Only after Gates A, A2, C and the lightweight Gate B **readiness check**: assemble both approved sources into temporary FB80 object decks; conditionally use the binary-safe IEBGENER pattern already established by `jcl/build-blib-object.jcl` to replace exactly `HERC02.BCPL.OBJ(BCPLMAIN)` and `(BCPLMEM)`. Verify the two objects have the expected ESD interface, including the explicit `STKOVFL` export in BCPLMAIN. Record both write step codes and post-install library inventory. Neither writing step is atomic with the other; do not claim transactional deployment. No changes to BCPLBYTE, BCPLAPT, BLIB, or unrelated PDSs.

On any failure, stop and follow the Gate B rebuild/redeploy recovery plan or repair the candidate and reinstall both; do not assume a preserved binary backup exists.

## Gate E: installed-runtime acceptance (NOT YET IMPLEMENTED)

Run focused installed-object regressions followed by the applicable full panel:

```sh
BCPL_RUNTIME_PDS=1 tools/run-native-regression 00 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 27 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 122 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 123 --show-output
```

`BCPL_RUNTIME_PDS=1` explicitly **excludes 083**: compiled object members lack its private FREEMAIN counters. The other 123 regressions are eligible; the normal whole-panel command encounters an intentional 083 failure rather than silently skipping it. Use a recorded explicit 083 exclusion in the installed-mode validation report (or improve the runner with a clear opt-in skip facility after review). Preserve separate 083 source-only 124/124 evidence. If installed-object acceptance fails, stop promotion and follow Gate B's documented rebuild/redeploy or forward-repair recovery path; then retest. Exact incumbent binary restoration is not guaranteed.

## Non-goals of this checkpoint

No deployment to OBJ, no change to `dspal populate`, no source alteration in BCPLMAIN/BCPLMEM/BLIB, no renaming of historical members, no change to regression acceptance logic, and no assertion of historical Cambridge MEMBIND semantics. Observability/PM design remains a separate research topic.

### Gate A2 JOB 9338 diagnostic (12 October 2026)

JOB 9338: ASMMMAIN, ASMMMEM, ASMPROBE each IFOX RC=0000; LKED IEWL RC=0008. Complete user-supplied listing diagnoses `IEC130I SYSLIB DD STATEMENT MISSING`, `IEW0432 SYSLIB`, and `IEW0132 STKOVFL` unresolved external. Generator previously used `//OBJ DD` rather than IEWL's `//SYSLIB DD`, and candidate BCPLMAIN did not publish local STKOVFL needed by separately assembled BCPLAPT. Revised link probe uses `//SYSLIB DD DSN=HERC02.BCPL.OBJ,DISP=SHR` and inserts `ENTRY STKOVFL` into a **disposable copy** of the candidate BCPLMAIN for the probe. Neither canonical source nor installed members were modified. Re-run A2; **no A2 acceptance yet**. For eventual production promotion, confirm the installed BCPLMAIN also exports STKOVFL or handle its dependency explicitly.

### Gate A2 JOB 9339 diagnostic (12 October 2026)

JOB 9339: ASMMMAIN, ASMMMEM, ASMPROBE RC=0000; LKED RC=0008. The ESD now confirms `STKOVFL` exported as LD, so that amendment assembles. The linker attempted `INCLUDE OBJ(BCPLBYTE)`, `INCLUDE OBJ(BCPLAPT)`, `INCLUDE OBJ(BLIB)` but generated JCL provided only `SYSLIB`, yielding three `IEC130I OBJ DD STATEMENT MISSING` and `IEW0432 OBJ` errors. The link-probe generator now allocates **both** `//SYSLIB` and `//OBJ` to the same existing object PDS using `DISP=SHR`. This preserves explicit INCLUDE DD semantics and does not modify OBJ. Gate A2 awaits another live link run; no link or executable acceptance is claimed.

### Gate A2 accepted — JOB 9340 (12 October 2026)

Operator-submitted corrected non-installing `BCOLINK` job 9340 completed: ASMMMAIN IFOX00 RC=0000, ASMMMEM IFOX00 RC=0000, ASMPROBE IFOX00 RC=0000, LKED IEWL RC=0000. IEWL cross-reference includes candidate BCPLMAIN length X'15B0', candidate BCPLMEM X'214', BCPLBYTE X'26', BCPLAPT X'6C', BLIB X'1BB0', plus four-byte BCOLINK caller. GETVEC/FREEVEC/MEMDRAIN/MEMBIND are resolved to BCPLMEM; STKOVFL is exported from disposable candidate BCPLMAIN and resolves for BCPLAPT. Total linked image X'3418'. Source is the operator's 9340 report. `HERC02.BCPL.OBJ` was read with DISP=SHR; no member was installed or replaced. **Assembly and cross-object linkage accepted. Execution was subsequently accepted by JOB 9342; the lightweight deployment-readiness check remains outstanding.** The production object installer must retain the STKOVFL export used in this successful probe.

### Gate C executable candidate probe (staged; awaiting TK5 execution)

Run `python3 tools/checks/prepare-runtime-object-execution-probe.py` after candidate preparation and an existing successful regression-28 Cambridge compilation. It reuses the project-proven `prepare-runtime-pds-regression.py` to construct a genuine test-28 BCPL application assembler, then substitutes temporary freshly assembled **externalized** BCPLMAIN (including exported STKOVFL) and BCPLMEM objects for the `INCLUDE OBJ(BCPLMAIN)` and `INCLUDE OBJ(BCPLMEM)` library members. Other installed members BCPLBYTE/BCPLAPT/BLIB remain `DISP=SHR` inputs. The resulting `BCOEX28` job executes a real GO step; require ASMAP, ASMMMAIN, ASMMMEM, LKED and GO all RC=0000, and BCPL output exactly `42`. Cross-check link-editor XREF to ensure the candidate pair and STKOVFL resolved rather than installed old members. No production PDS writes; no execution acceptance is claimed until job result and output are examined. The earlier Gate A2 `BCOLINK` success (JOB 9340) established link closure but not behavior.

### Gate C JOB 9341 diagnostic — loader S806-04 (12 October 2026)

Operator ran BCOEX28 job 9341: ASMAP, ASMMMAIN, ASMMMEM IFOX RC=0000, LKED IEWL RC=0000. GO abended S806-04 before executing the BCPL application: `IEA703I 806- 4 ... MODULE ACCESSED RG028OBJ`. Cause was generator mismatch between IEWL `NAME BCOEX28(R)` and `//SYSLMOD DD DSN=&&GOSET(RG028OBJ)`; the loader sought the old member name. The candidate execution generator now changes both to BCOEX28. **No runtime behavior is demonstrated by JOB 9341; Gate C remains pending.** Existing OBJ members untouched.

### Gate C accepted — JOB 9342 (12 October 2026)

Operator submitted BCOEX28 JOB 9342 from corrected non-installing execution probe. ASMAP IFOX00 RC=0000, ASMMMAIN IFOX00 RC=0000, ASMMMEM IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; BCPL SYSPRINT output is exactly `42`. IEWL cross-reference: BCRG0028 X'0000'/X'00D8', **candidate** BCPLMAIN X'00D8'/X'15B0', **candidate** BCPLMEM X'1688'/X'0214', installed BCPLBYTE X'18A0'/X'0026', installed BCPLAPT X'18C8'/X'006C', installed BLIB X'1938'/X'1BB0'; total X'34E8'. References: BCPLMAIN to GETVEC/FREEVEC/MEMDRAIN/MEMBIND resolve in BCPLMEM, and BCPLAPT to STKOVFL resolves in BCPLMAIN. The 28-freevec program exercises two allocations with explicit release and emits `42`. No object PDS members were modified. **Gate C executable acceptance achieved**. Lightweight reproducibility/recovery readiness and controlled paired promotion are the remaining gates; this is not yet installed-PDS acceptance.

### Gate B inventory and staged deployment generator — 12 October 2026

Operator's `tools/dspal stat OBJ` ran as JOB 9343: `HERC02.BCPL.OBJ` on volume `TSO003`, `DSORG=PO`, `RECFM=FB`, `LRECL=80`, `BLKSIZE=800`. `tools/dspal ls OBJ` listed exactly `BCPLAPT`, `BCPLBYTE`, `BCPLMAIN`, `BCPLMEM`, `BLIB`. **Inventory accepted; incumbent BCPLMAIN/BCPLMEM Git provenance remains unproven.** The operator deliberately selected Git-based rebuild/redeploy, rather than IEBCOPY backup.

The new `tools/checks/prepare-runtime-object-install.py` **stages, but never submits**, `workarea/runtime-object-candidates/install-runtime-objects.jcl` and a Git SHA256 source manifest. It regenerates the externalized BCPLMAIN from canonical source and adds `ENTRY STKOVFL` to the disposable installation source; its two IFOX object decks feed sequential conditional IEBGENER writes to `OBJ(BCPLMAIN)` and `OBJ(BCPLMEM)`. The JCL uses the established `build-blib-object.jcl` FB80 copying pattern, but **the installation JCL has not been tested or submitted**. Do not submit until operator has reviewed the JCL/manifest, accepted lack of exact incumbent rollback, and captured commit/source hashes. **The member pair is not atomic.** Verify both writes and installed-PDS regressions after submission.
