# How to Operate the BCPL Programming System

*Cambridge BCPL Programming System for MVS 3.8J*

For routine MVS operation of an installed release. Worked examples use RC4; [installation guide](How-to-Install-BCPL-from-Tape.md) and [RC4 companion](../../packaging/distribution/publication/RC4-README.md) establish the prerequisites. This is not a TK5 host management or source reconstruction runbook.

## 1. Identify installed release, profile and available environments

Record release ID, installed namespace, profile, source/manifest identity, and available system resources before submitting jobs. Use the frozen release manifest, not a current development dataset inventory.

| Profile | Routine supported use |
| --- | --- |
| MR10 | Installed ICINT19, MR10 compile/generate/run, demos and regressions |
| COMBINED | Same MR10 workflow; native components available for inventory/source study only under RC4 |
| NATIVE | Inventory and source study; no supported native application compilation or MR10 execution |

The independent native-running Cambridge Compiler and interpreter-hosted CAMBCOMP are absent from RC4. A development installation may have CAMBCOMP, but do not infer that from native object libraries being present.

## 2. Confirm libraries, procedures, datasets and DDs

For MR10-capable profiles the site prefix is exemplified by HERC02.BCPL.R4MR. Under that prefix:

| PDS suffix | Routine purpose |
| --- | --- |
| DIST.INST / DIST.DOCS | Installer and supplied documentation; companion supersedes older draft text |
| MR10KIT.SOURCE | INTCODE phases SYNI/TRNI/CGI/BLIBI/ICLIB |
| MR10KIT.LOAD | Executable ICINT19 (U/6144) |
| MR10KIT.JCL | MRLANGDM, MRBCDEMO, MRREGRES, IC19BLD (build only) |
| MR10KIT.LANGDEMO / BCPLDEMO | Language/application sources and associated input members |
| MR10KIT.LIBRARY | Optional MR10-local BCPL source modules |
| MR10KIT.TESTS | Regression source, support input and independent expected records |
| MR10KIT.ASM / OBJ | Rebuild inputs and relocatable object, not the normal interpreter invocation |

MR10KIT.BCPLDEMO is the MR10 application-demo PDS, not the native BCPLDEMO System Extension. Use [frozen manifest](../../packaging/distribution/manifest/releases/BCPL-0.1.0-rc4.yaml) for exact names. Confirm catalog/volume and expected member availability; keep shipped libraries read-only for normal work.

Important DDs: STEPLIB selects the installed interpreter; INTIN concatenates staged executable INTCODE; SYSIN provides compiler input or application data as appropriate; OCODE and INTCODE are intermediate decks; SYSPRINT carries diagnostics/output. OPTIONS and named GET DDs are compiler inputs when needed. Do not confuse literal DDs with dataset manifest keys.

## 3. Submit and monitor installed jobs

Copy the desired member from the installed JCL PDS to a submission deck. Change HERC02.BCPL.MR10KIT. to your exact installed prefix, including SITE; add a site-authorized JOB card; check names, card columns and all continuations. Keep original JCL intact. Review DD allocations, dispositions and resource limits before submission.

| Member | Staging | C/G steps | R steps | Total |
| --- | ---: | ---: | ---: | ---: |
| MRLANGDM | 5 | 22 | 11 | 38 |
| MRBCDEMO | 5 | 40 | 17 | 62 |
| MRREGRES | 5 | 46 | 12 | 63 |

The three jobs are stored bodies, not directly executable JOB cards. They use installed ICINT19 and do not assemble/link or rebuild the compiler. Cxx compiles BCPL to OCODE; Gxx generates INTCODE; Rxx interprets application and support decks. Multiple modules account for additional C/G steps. Submit through the site's established JES input procedure, record actual JOB name/number and observe completion. Do not assume receipt of a JOB ID is execution success.

Use your site's JES/spool facility to obtain the actual step messages and SYSPRINT data. On the project development host only, [job-summary](../../tools/mvs/job-summary) and [dump-report-for-job](../../tools/mvs/dump-report-for-job) inspect saved/available JES reports; these tools are not part of the MVS recipient requirement.

## 4. Review output, spool routing, codes and diagnostics

| Evidence | Required interpretation |
| --- | --- |
| JES IEF142I and step RC | Expected ordered steps completed, normal suites RC0000 |
| Interpreted CODE | Require CODE=0 for each compiler/generator/application invocation |
| DEMO: | Description and actual output; compare with example behavior |
| TEST: | Correct regression identity, in the intended order |
| EXP: | Fixed expected result printed by source, not independent proof |
| RP: | Evaluated result; compare with independent expected record |
| SYNTAX ERROR / INTCODE ERROR / MAPSTORE | Investigate unexpected diagnostics even with zero JES RC |

The suite JCL uses COND=(4,LT) in compiler/application steps; later execution can still occur despite some nonzero conditions or a nonzero interpreted CODE. Do not accept merely because the last step ran. Treat missing, duplicate, malformed, unexpected or out-of-order records as evidence failures. The acceptance reviewer checks complete ordered records, not a loose search for PASS.

SYSPRINT logical records, JES spool presentation, and Hercules printer or punch capture are different observations. Routine jobs use SYSOUT according to local routing. If output is absent, confirm actual step completion, output class, DD and writer/device state before retrying. Do not start/resume a shared JES device indiscriminately.

## 5. Run health checks and supported smoke tests

Confirm the intended MR10KIT.LOAD(ICINT19) and phase members; run a known unmodified workload after installation or a suspected operational change. The installed MRREGRES member provides the semantic baseline. A small existing case is SCALVEC (C01A/G01A/R01 after phase staging). See the [compile/run guide](How-to-Compile-and-Run-BCPL-Programs.md) for the exact extracted sequence and expected records. For complete verification run all three suites and retain each report.

Compare the full twelve-case MRREGRES output with the supplied MR10KIT.TESTS golden members. Example independent records from SCAVEXP / [scalar-vector.expected](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.expected):


```text
RP: SCALAR 17 42
RP: VECTOR 5 10 15 20
```

The shipped JCL itself does not compare every result with expected members. On a development checkout pinned to compatible goldens, the offline reviewer documented in [distribution tools](../../tools/distribution/README.md) can compare a saved full regression report with TEST, EXP, RP and CODE records. It is optional; no host tool is required on a recipient MVS system. Do not reuse a sealed acceptance report as evidence of a new run.

The [TA.7 record](../../packaging/milestones/tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md) establishes two independent 40-case suites on the existing MVS system; NATIVE-only health verification is inventory only under RC4.

## 6. Manage routine input/output datasets and resource usage

Place new application source and persistent outputs in authorized site/user datasets, not shipped compiler, library or test PDSes. Preserve FB80 source/deck record boundaries and character representation. Stage the five phase decks into temporary sequential FB80 datasets before INTIN concatenation; the supplied JCL deliberately avoids the observed end-of-member issue with PDS members. Each job owns its temporary datasets and passes/deletes them in the established order.

The shipped suites use REGION=1024K for the displayed MR10 compile/run sequence, FB80 intermediate records and FB132 SYSPRINT. These are verified job shapes, not general minimum or maximum resource guarantees. Use sufficient authorized DASD/work space, directory entries and JES output capacity. Avoid persistent outputs with replacing dispositions unless specifically authorized. A PDS's allocated capacity and live member occupancy are different; high-water marks may include dead space. Inspect actual MVS allocation/directory information rather than infer free space from a requested SPACE parameter.

Application data DDs are separate from compiler inputs; preserve exact member names, order and format. Use ordinary character streams for text; the native logical-record extension has a different contract and is not a supported RC4 workflow.

## 7. Respond to failures, preserve evidence and escalate

| Failure | First action |
| --- | --- |
| Missing load/phase member | Verify installed namespace and catalog/member inventory |
| Compiler diagnostic or nonzero CODE | Inspect source dialect, named inputs, options and first failed phase |
| Wrong result with RC0000 | Compare exact TEST/EXP/RP and input data; investigate software or transport |
| Allocation/region failure | Inspect actual JES/MVS diagnostics and resources; do not alter installed objects |
| Missing spool/device output | Inspect job/step/DD and writer routing; preserve pending work |
| Abend or timeout | Determine actual job state before any resubmission |

Save source/member versions, submission JCL (protect credentials), job name/number, date/time, site/profile, complete JES report, expected results and observed outputs. JES job IDs wrap; identify a run with its context. For wrong output, preserve the original failure, not a changed oracle. Escalate reproducible defects with evidence to the project repository or site operator.

## 8. Distinguish routine operation from installation, reconstruction and promotion

Running installed MR10 application jobs is routine. Installing from tape allocates new PDSes. IC19BLD assembles and link-edits ICINT19 and replaces the target object/load member unless carefully retargeted; it is not a health check. TA.4 verified an isolated rebuild, not replacement of the distributed load module. Source reconstruction, manifest purge/populate, runtime/extension promotion, device-control campaigns and new tape production are separate controlled operations.

For product use see [compile/run guide](How-to-Compile-and-Run-BCPL-Programs.md) and [compiler reference](Reference-for-BCPL-Compilers.md). For authorized project reconstruction use the [source rebuild guide](../Rebuild-BCPL-for-MVS-from-source.md), not routine operator instructions. Do not rerun retired trial or one-shot release controllers. No new MVS run is claimed by this manual.
