# BCPLMAIN / BCPLMEM paired object promotion

Status: **Gate A accepted on TK5 (JOB 9337), not installed**, 12 October 2026.

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

## Gate A2: non-installing cross-object link check (staged, awaiting TK5)\n\nAfter Gate A, run `python3 tools/checks/prepare-runtime-object-link-probe.py`, inspect `workarea/runtime-object-candidates/link-candidates.jcl`, and submit it. This job assembles a minimal external BCPLMAIN reference, the freshly transformed BCPLMAIN and canonical BCPLMEM in three separate IFOX steps, then link-edits with the existing installed OBJ(BCPLBYTE), OBJ(BCPLAPT) and OBJ(BLIB). The production OBJ is opened `DISP=SHR` for reading only. Require all assembler steps and LKED RC=0000, verify that MEMBIND and other external references resolve from the *new* BCPLMEM CSECT, and inspect ESD/XREF. There is **no GO** and this test cannot establish functional runtime behavior; a representative running probe is still required before installation.\n\n## Gate B: preservation and restore proof (NOT YET IMPLEMENTED)

Before any replacement, inventory the effective manifest and member existence:

```sh
tools/dspal stat OBJ
tools/dspal ls OBJ
```

Use a dedicated **binary-preserving MVS utility** (e.g. IEBCOPY to a separate, preallocated backup object PDS with validated attributes) to preserve `OBJ(BCPLMAIN)` and `OBJ(BCPLMEM)` with member identities, then confirm backup member inventory and readback/restore on a disposable library. Do not use `dspal get`, `dspal put`, ordinary host text conversion, or an unverified copy mechanism for object decks. Retain existing `BCPLBYTE`, `BCPLAPT`, `BLIB` untouched. A backup is not validated solely because a copy job returns zero; test linking/restoring from its members on a *non-production* target.

Record source commit IDs, member inventory, MVS job numbers, IFOX results, linker map and restore steps in an acceptance report. A host-side backup of the DASD volume is an additional possible safeguard, not a substitute for validated member restoration.

## Gate C: pre-installation linkage (NOT YET IMPLEMENTED)

Build a *non-installing* application+candidate-runtime link probe, with both freshly assembled candidate objects and the existing supporting member dependencies. Confirm EXTRN GETVEC/FREEVEC/MEMDRAIN/MEMBIND resolve to candidate BCPLMEM, linkage succeeds without unresolved externals, and representative application/BLIB execution matches expected output. The Gate A job does not link; **do not skip Gate C**.

## Gate D: paired replacement (NOT YET IMPLEMENTED)

Only after gates A, B and C have succeeded: controlled copy of the two accepted binary FB80 object decks into `HERC02.BCPL.OBJ(BCPLMAIN)` and `(BCPLMEM)`, with fail-closed return codes, post-write member verification and a ready-to-run validated restore job. Both modules are one logical release even if the underlying PDS operations are sequential. No broad `purgebcpl` and no recreation of unrelated members.

Do not claim this is atomic: mid-copy failures require explicit restoration of both old members. Keep the source/PDS authority model intact.

## Gate E: installed-runtime acceptance (NOT YET IMPLEMENTED)

Run focused installed-object regressions followed by the applicable full panel:

```sh
BCPL_RUNTIME_PDS=1 tools/run-native-regression 00 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 27 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 122 --show-output
BCPL_RUNTIME_PDS=1 tools/run-native-regression 123 --show-output
```

`BCPL_RUNTIME_PDS=1` explicitly **excludes 083**: compiled object members lack its private FREEMAIN counters. The other 123 regressions are eligible; the normal whole-panel command encounters an intentional 083 failure rather than silently skipping it. Use a recorded explicit 083 exclusion in the installed-mode validation report (or improve the runner with a clear opt-in skip facility after review). Preserve separate 083 source-only 124/124 evidence. If any installed-object acceptance fails, restore the preserved BCPLMAIN/BCPLMEM pair and retest.

## Non-goals of this checkpoint

No deployment to OBJ, no change to `dspal populate`, no source alteration in BCPLMAIN/BCPLMEM/BLIB, no renaming of historical members, no change to regression acceptance logic, and no assertion of historical Cambridge MEMBIND semantics. Observability/PM design remains a separate research topic.

### Gate A2 JOB 9338 diagnostic (12 October 2026)

JOB 9338: ASMMMAIN, ASMMMEM, ASMPROBE each IFOX RC=0000; LKED IEWL RC=0008. Complete user-supplied listing diagnoses `IEC130I SYSLIB DD STATEMENT MISSING`, `IEW0432 SYSLIB`, and `IEW0132 STKOVFL` unresolved external. Generator previously used `//OBJ DD` rather than IEWL's `//SYSLIB DD`, and candidate BCPLMAIN did not publish local STKOVFL needed by separately assembled BCPLAPT. Revised link probe uses `//SYSLIB DD DSN=HERC02.BCPL.OBJ,DISP=SHR` and inserts `ENTRY STKOVFL` into a **disposable copy** of the candidate BCPLMAIN for the probe. Neither canonical source nor installed members were modified. Re-run A2; **no A2 acceptance yet**. For eventual production promotion, confirm the installed BCPLMAIN also exports STKOVFL or handle its dependency explicitly.

### Gate A2 JOB 9339 diagnostic (12 October 2026)

JOB 9339: ASMMMAIN, ASMMMEM, ASMPROBE RC=0000; LKED RC=0008. The ESD now confirms `STKOVFL` exported as LD, so that amendment assembles. The linker attempted `INCLUDE OBJ(BCPLBYTE)`, `INCLUDE OBJ(BCPLAPT)`, `INCLUDE OBJ(BLIB)` but generated JCL provided only `SYSLIB`, yielding three `IEC130I OBJ DD STATEMENT MISSING` and `IEW0432 OBJ` errors. The link-probe generator now allocates **both** `//SYSLIB` and `//OBJ` to the same existing object PDS using `DISP=SHR`. This preserves explicit INCLUDE DD semantics and does not modify OBJ. Gate A2 awaits another live link run; no link or executable acceptance is claimed.

### Gate A2 accepted — JOB 9340 (12 October 2026)

Operator-submitted corrected non-installing `BCOLINK` job 9340 completed: ASMMMAIN IFOX00 RC=0000, ASMMMEM IFOX00 RC=0000, ASMPROBE IFOX00 RC=0000, LKED IEWL RC=0000. IEWL cross-reference includes candidate BCPLMAIN length X'15B0', candidate BCPLMEM X'214', BCPLBYTE X'26', BCPLAPT X'6C', BLIB X'1BB0', plus four-byte BCOLINK caller. GETVEC/FREEVEC/MEMDRAIN/MEMBIND are resolved to BCPLMEM; STKOVFL is exported from disposable candidate BCPLMAIN and resolves for BCPLAPT. Total linked image X'3418'. Source is the operator's 9340 report. `HERC02.BCPL.OBJ` was read with DISP=SHR; no member was installed or replaced. **Assembly and cross-object linkage accepted. Execution and backup/restore remain outstanding.** The production object installer must retain the STKOVFL export used in this successful probe.

### Gate C executable candidate probe (staged; awaiting TK5 execution)

Run `python3 tools/checks/prepare-runtime-object-execution-probe.py` after candidate preparation and an existing successful regression-28 Cambridge compilation. It reuses the project-proven `prepare-runtime-pds-regression.py` to construct a genuine test-28 BCPL application assembler, then substitutes temporary freshly assembled **externalized** BCPLMAIN (including exported STKOVFL) and BCPLMEM objects for the `INCLUDE OBJ(BCPLMAIN)` and `INCLUDE OBJ(BCPLMEM)` library members. Other installed members BCPLBYTE/BCPLAPT/BLIB remain `DISP=SHR` inputs. The resulting `BCOEX28` job executes a real GO step; require ASMAP, ASMMMAIN, ASMMMEM, LKED and GO all RC=0000, and BCPL output exactly `42`. Cross-check link-editor XREF to ensure the candidate pair and STKOVFL resolved rather than installed old members. No production PDS writes; no execution acceptance is claimed until job result and output are examined. The earlier Gate A2 `BCOLINK` success (JOB 9340) established link closure but not behavior.

### Gate C JOB 9341 diagnostic — loader S806-04 (12 October 2026)

Operator ran BCOEX28 job 9341: ASMAP, ASMMMAIN, ASMMMEM IFOX RC=0000, LKED IEWL RC=0000. GO abended S806-04 before executing the BCPL application: `IEA703I 806- 4 ... MODULE ACCESSED RG028OBJ`. Cause was generator mismatch between IEWL `NAME BCOEX28(R)` and `//SYSLMOD DD DSN=&&GOSET(RG028OBJ)`; the loader sought the old member name. The candidate execution generator now changes both to BCOEX28. **No runtime behavior is demonstrated by JOB 9341; Gate C remains pending.** Existing OBJ members untouched.
