# Milestone QSAM — Q.4 native regression acceptance evidence (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** **Q.4 — SYSOUT devices**
**Disposition:** **Technical native acceptance PASSED; formal owner closure PENDING.**

## Authority and verified baseline

The owner ran the resident Hercules/TK5 **MVS 3.8J** native regression harness after fast-forwarding GitHub `main` to [`51ed022eeea69af2b8453a766b43769abbdbf826`](https://github.com/cbmira01/BCPL-for-MVS/commit/51ed022eeea69af2b8453a766b43769abbdbf826). Git integrity and native runner Python syntax checks passed (RC=0). Production `BOOT_OBJ` Core Runtime objects were used read-only; optional `BCPLQSAM` was source-selected. No installed BCPLQSAM object was promoted or permanent dataset modified.

The harness uses the resident **demoted Cambridge compiler**, IFOX, IEWL, native BCPL applications and independent IFOX QSAM verification; this is **not** an execution claim about the future self-hosted Cambridge compiler. The operator explicitly enabled `Q4_PUNCH_RESUME=1` for both panels, permitting a single `$S PUN1` console action after case 175 native success if needed. The consolidated output does not establish whether a resume was actually issued on either rerun.

## Fresh owner-run native acceptance results

| Panel | PASS | FAIL | SKIP | TOTAL | Runner RC | Capture RC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Focused `163..176` | **14** | **0** | **0** | **14** | **0** | **0** |
| Full production `00..176` | **176** | **0** | **1** | **177** | **0** | **0** |

The sole expected skip is **083 — instrumented-storage-reclamation**, a source-only instrumentation regression. All QSAM cases 163–176, including 163/170 QUERY carriage capability `QS_CAP_FIXED | QS_CAP_VARIABLE | QS_CAP_CARRIAGE = 7`, individually displayed PASS in both panels. The supported-opcode bitmap remains 31; VBA is not claimed.

- **175 — FB80 SYSOUT punch:** `SYSPUNCH DD SYSOUT=B`, three records, exact independent IFOX temporary-dataset byte/EOF readback and a new 172-byte Hercules ASCII punch image with separator.
- **176 — FBA133 SYSOUT printer:** independent IFOX 133-byte temporary-record and EOF verification; `Q4PRINT DD SYSOUT=A` exhibits ASA blank, 0 and 1 spacing/page-eject presentation.

The full panel additionally passed the established compiler, Core Runtime, BLIB, optional-extension, and earlier F/FB/V/VB QSAM regressions. The final operator output was:

```text
Focused: PASS=14 FAIL=0 SKIP=0 TOTAL=14
Full: PASS=176 FAIL=0 SKIP=1 TOTAL=177
Q.4 FOCUSED AND FULL NATIVE ACCEPTANCE PASSED
Q.4 acceptance workflow RC=0
```

## Real failure and recovery history

The initial case 175 on **JOB 7755** completed native assembly/link, BCPL write and independent IFOX verification successfully, but the Hercules punch capture had not advanced because JES2 `PUNCH1` was `PAUSED` with `P=Y`. That initial focused panel correctly reported 13 PASS, 1 FAIL and skipped the full run. The owner issued `$S PUN1`, after which JES2 reported three cards, purged JOB 7755 and the ASCII capture grew from 172 to 344 bytes; the **new 172 bytes** matched the exact expected card image. See the [JES2 punch incident record](qsam-q4-numbered-punch-incident-20261030.md). The source-controlled opt-in writer-resume behavior preceded the fresh successful panels. The original failure is retained rather than retroactively relabeled.

## Operator-local evidence and limits

The following files are retained locally and not versioned in Git:
- `workarea/bcplqsam-q4/q4-focused-163-176-resume.log` and `q4-focused-resume.rc`.
- `workarea/bcplqsam-q4/q4-full-00-176-resume.log` and `q4-full-resume.rc`.
- Individual compiler/JES/IFOX reports, job IDs, temporary JCL, and device capture under `workarea/native-regression/`.

The owner supplied the complete consolidated panel pass/fail lines and counts, **not** a separate full per-JES listing audit from every test run. The [standalone FB80 punch evidence](qsam-q4-punch-evidence-20261030.md) (JOBs 7725/7726) and [FBA133 evidence](qsam-q4-fba-evidence-20261030.md) (JOBs 7727/7728) remain independent historical verification.

## Gate disposition

**The Q.4 technical verification gate is satisfied.** Generated punch records, ASA carriage-control printer output, byte-exact IFOX verification, QUERY carriage capability, and focused/full native production regressions all passed.

**Q.4 — SYSOUT devices remains formally IN PROGRESS pending the project owner's explicit closure decision.** The future **Q.5 — Hardening & release** retains exceptional OPEN/CLOSE, STOP/finalizer, clean-from-Git rebuild and optional object-promotion obligations. This evidence record does not authorize another march, permanent installation or a new JES submission.
