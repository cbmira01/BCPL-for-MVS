# M2.1 Gate E — Native Runtime Application Integration

**Status: OPEN — 14 October 2026.** Gate D accepted and closed. Scope: native BCPL **applications**, not native compilation of compiler phases. Resident D7 candidate: `HERC02.BCPL.DEVOBJ(BCPLM7)`. Stable production `HERC02.BCPL.OBJ` MUST NOT be changed.

## Goal

Accept a usable, independently linked application-facing runtime by demonstrating (a) resident Cambridge INTCODE compilation of application source into System/370 assembler, (b) assembly of that application into its own control section, (c) linkage with preassembled, distinct MVS DEVOBJ runtime modules and historical BLIB, and (d) **actual MVS GO output/completion**, without using a combined inlined assembler runtime as substitute.

The existing installed-object regression harness is the acceptance vehicle, not a second application loader.

## Baseline and evidence at entry

- D7 assembler/source `asm/bcplmain-d7-candidate.asm` staged to SOURCE(BCPLM7), assembled/installed by payload JOB 2989 (IFOX00 and IEBGENER RC=0000), integrated link by payload JOB 2992 (IEWL RC=0000).
- Full D7 `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7 tools/native/run-regression` completed **123 PASS / 0 FAIL / 1 expected SKIP 083 / 124 total**. This is accepted Gate B/Gate C/Gate D execution baseline, not a new Gate E run.
- Existing regression 069 establishes independent BLIB object linkage in the historical experimental JOB 2425, and is PASS in the modern full D7 panel. The old `069/README.md` has stage-specific historical assertions including "not yet PASS" that are **stale** for the accepted D7 installed-object path. Treat modern harness execution and MVS JES output as authoritative over that obsolete stage status.
- Existing tests 025 and 026 cover separate BCPL/library and native-through-global calls, with associated limits; 069 and 075 independently exercise historical BLIB. Tests 091–093 cover external BCPLAPT; 094–119 exercise BCPLIO; 121–123 exercise save-area/vector list cooperation.

## Gate E acceptance profile: selected, then complete

Use the **existing** D7 candidate environment consistently. Do not stage a new assembler, install objects, change JCL, compile compiler phases, or promote production OBJ.

Run a small targeted integration panel of independent application concerns:

| Regression | Application integration property asserted | Evidence boundary |
| --- | --- | --- |
| 025 | Separately compiled BCPL library procedure call | Proves tested call/link behavior; may use dedicated fixture mechanism, not automatically proof of production link-library behavior |
| 026 | Separately assembled native function callable through global vector | Proves tested native-to-BCPL dispatch |
| 069 | Historical BLIB linked as an independent object | Inspect actual generated JCL and IEWL map on this run; **do not infer** distinct CSECTs from PASS output alone |
| 075 | Mixed WRITEF through historical BLIB object | Output and BLIB route |
| 091 | APTOVEC across nested calls | Independent BCPLAPT public interface |
| 101 | Two output destinations | Separate BCPLIO QSAM streams |
| 119 | Output flushing on termination | FINISH/STOP stream lifecycle |
| 121 | SAVEAREA / historical BLIB consumers | G6 collaboration at documented limited scope |

Each test must be PASS with assembler and linkage steps normal and expected GO output. In particular, retain the JCL/JES report for test 069 and inspect for **application**, **BCPLMAIN**, **BLIB**, **BCPLIO**, **BCPLMEM**, **BCPLBYTE** and **BCPLAPT** module inclusion or link resolution as indicated by the job's linker listing. Do not presume all seven CSECTs necessarily appear in every test or claim automatic completeness of unused services.

## Suggested operator execution

From repository root:

```sh
git pull --ff-only

for n in 25 26 69 75 91 101 119 121; do
  BCPL_RUNTIME_PDS=1 \
  BCPL_RUNTIME_LIBRARY=DEVOBJ \
  BCPL_RUNTIME_CANDIDATE=1 \
  BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7 \
  tools/native/run-regression "$n" --show-output || break
done
```

On successful focused tests, run the complete unchanged D7 panel (same four environment variables). Expected aggregate: **123 PASS, 0 FAIL, one source-only SKIP 083**.

Test 069 link map and exact GO results are separately important; if the runner prints a job number, use `tools/mvs/job-summary N` and `tools/mvs/dump-report-for-job N` to retain evidence. If no job number appears in the normal output, inspect `workarea/native-regression/logs/069-independent-blib-object.log` or the per-test workarea report.

## Gate E exit criteria

- [x] Existing source/architectural and accepted D7 integration evidence reviewed.
- [x] Explicit distinction between BLIB independent-object link/edit and an inlined compiler source combiner established.
- [x] Executable Gate E integration checks and non-production command path prepared.
- [ ] Owner executes focused D7 candidate application integration panel; record per-case result and job evidence for 069 link map.
- [ ] Owner executes post-check full D7 regression panel, or explicitly determines why earlier identical binary evidence suffices; record which.
- [ ] Correct any reproducible application/linkage regression with separate evidence and permission; no speculative runtime refactoring.
- [ ] Owner accepts and closes Gate E. Transition to Gate F versioned contract, RC register and regression coverage matrix.

**Historical Gate E launch status:** superseded by final acceptance at end of document. No resident DEVOBJ or production objects were changed by this plan.


## Focused D7 Gate E execution — 14 October 2026

Owner synchronized Git through commit 34de425 and ran the eight prescribed focused regressions, each with all four candidate selectors (PDS=1, LIBRARY=DEVOBJ, CANDIDATE=1, MEMBER=BCPLM7). Individual console results: **025 PASS, 026 PASS, 069 PASS, 075 PASS, 091 PASS, 101 PASS, 119 PASS, 121 PASS**. Each one-test panel reported 1 PASS / 0 FAIL / 0 SKIP. Total **8/8 focused PASS**; no source, linker or runtime changes made.

This is post-charter Gate E MVS execution evidence. The console transcript does not contain the IEWL map or exact JES step codes for case 069; retain that as an explicit pending verification, despite the behavioral PASS. Also pending: post-focused complete 00–123 D7 panel. Neither requirement is silently inferred from eight PASS labels.


## Final post-focused D7 run and regression 069 job proof — 14 October 2026

Owner synchronized Git through 9546317 and ran the **entire installed DEVOBJ(BCPLM7) native regression 00–123**, with four explicit candidate selectors. **123 PASS, 0 FAIL, 1 expected SKIP (083), 124 total.** This is a new Gate E panel after the eight successful focused checks, not reused earlier Gate B evidence.

The supplied regression 069 log shows compiler **JOB 3645**, native payload **JOB 3646 RG069R**:
- ASMAP IFOX00 **RC=0000** (zero flagged statements, highest severity 0);
- LKED IEWL **RC=0000**;
- GO **RC=0000**; job result SUCCESS;
- output record logical sequence matched expected `BLIB 42`; regression PASS;
- JES DD attribution not independently verified by the record-check tool.

**Remaining formal linkage map check:** console and per-test log do not include IEWL MAP/XREF CSECT listing. Before formal Gate E closure obtain `tools/mvs/dump-report-for-job 3646` and inspect actual link-edit inclusions/CSECTs and resolution; do not fabricate a map from a successful GO. The expected outcome is separate application CSECT, BCPLMAIN and linked runtime/BLIB sections, as shown in the available listing. If only partial map information is present, identify its limits rather than claiming all objects listed.

No candidate source, assembler, DEVOBJ object, or production OBJ changes were made for these Gate E executions. **Gate E ready for final map inspection, not yet formally closed.**


## Final independent-object IEWL evidence and closure — 14 October 2026

Owner supplied the complete `tools/mvs/dump-report-for-job 3646` JES/IFOX/IEWL/GO report. **JOB 3646 RG069R**: ASMAP IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000; program printed **`BLIB 42`**.

The IEWL `LIST,XREF,MAP` report explicitly includes `OBJ(BCPLM7)`, `OBJ(BCPLIO)`, `OBJ(BCPLBYTE)`, `OBJ(BCPLAPT)`, `OBJ(BCPLMEM)`, and `OBJ(BLIB)` from `HERC02.BCPL.DEVOBJ`, with `ENTRY BCRG0069`.

| CSECT | Origin (hex) | Length (hex) |
| --- | --- | --- |
| BCRG0069 application | 000000 | 000088 |
| BCPLMAIN | 000088 | 000C00 |
| BCPLIO | 000C88 | 000FF8 |
| BCPLBYTE | 001C80 | 000026 |
| BCPLAPT | 001CA8 | 00006C |
| BCPLMEM | 001D18 | 0002AC |
| BLIB | 001FC8 | 001BB0 |
| **Total** | | **003B78** |

The IEWL XREF explicitly identifies application location 00000C referring to BCPLMAIN and resident BCPLMAIN references to GETVEC/FREEVEC in BCPLMEM, GETBYTE/PUTBYTE in BCPLBYTE, APTOVEC/APLIMIT in BCPLAPT, and multiple BCPLIO entries, plus BLIB references to BCPLMAIN. This establishes genuine separate control sections and external linkage, not source-text combination. Source report notes `RG069OBJ DOES NOT EXIST BUT HAS BEEN ADDED TO DATA SET`; link was RC=0000 and GO succeeded, so this is informational, not an unresolved error.

**Gate E ACCEPTED AND CLOSED — 14 October 2026.** Acceptance rests on the eight focused applications passing, the post-focused full D7 panel **123 PASS, 0 FAIL, one expected SKIP 083**, and the independent-object LINK/GO proof in JOB 3646. Owner's provision of requested final map completes the final evidence request; no runtime source or resident object changes were necessary. M2.1 continues to Gate F for consolidated runtime contract, RC registry, coverage matrix and final candidate acceptance. Production OBJ remains unchanged.
