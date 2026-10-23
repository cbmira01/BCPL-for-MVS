# Milestone Runtime Extensions — R.5 — Optional Extension Packaging and Regression

**Owner authorization:** 23 October 2026 — "Approve, proceed" to the nine stated R.5 goals.
**Status:** R.5 IN PROGRESS; no MVS R.5 acceptance yet.
**R.4:** JOB 3720 macro/PUNCH/IEWL and JOB 3722 integrated startup passed. Formal R.4 closure is **not** assumed or changed.

## Objective

Deliver **BCPLDEMO** as a fully packaged, documented and regression-tested
optional extension: one IFOX assembler source/object containing the
BCEX descriptor and dispatcher CSECTs; BCPL header; MVS-native selection
macros; install/rebuild/recovery JCL; user documentation; independent
numbered native BCPL regressions 146–158; and clean-room reproduction.

## Owner-approved goals

1. Consolidate BCPLDEMO into a single assembler source with both CSECTs.
2. Specify and verify installation of the optional object in an agreed PDS.
3. Package MVS-native BCXSEL, BCXREQ and a known-package catalog.
4. Document public API, headers, globals, builds, links and usage.
5. Add native numbered regression cases **146 through 158**, one BCPL source per case.
6. Integrate those cases into the existing individual/range/full runners;
   preserve existing tests **00–145**.
7. Repeat relevant tests against the installed member, not only
   temporary development objects.
8. Rebuild from a clean Git checkout with MVS tools and retained evidence.
9. Require JES, IFOX, IEWL MAP/XREF, GO and regression gate evidence.

## Design decisions

- **Two CSECTs, one IFOX assembly:** DMODESC carries BCEX v1,
  DMODISP carries the G!203 dispatcher. One END, no artificial
  EXTRN between CSECTs in the same assembly.
- Retain the separate descriptor.asm and dispatcher.asm as historical
  R.2/R.3 regression inputs until their consumers are adapted and
  revalidated. Their semantics must remain equivalent to bcpldemo.asm.
- Test paths compile source **on MVS** with the resident **demoted
  Cambridge compiler**, assemble via IFOX and link via IEWL;
  no host compilation or host registration generation.
  Local runner orchestration may submit JCL and verify reports,
  as in the established 00–145 test system.
- Application source declarations, IEWL object inclusion, and
  BCPLRGS startup registration remain three independent obligations.
- Maintain BCEX/BCRG v1 and accepted BCPLMAIN/BCPLRGS;
  no changes to the compiler or shared ABI.
- No migration of compiler, runtime, or package binaries into a
  PDS merely by copying prebuilt material.

## Numbered regression obligations

| Case | Contract |
| --- | --- |
| 146 | Zero optional packages, empty BCRG, normal START/FINISH |
| 147 | BCPLDEMO QUERY size inquiry |
| 148 | Six-word QUERY descriptor content |
| 149 | Short QUERY capacity, unchanged buffer |
| 150 | Invalid QUERY arguments, no writes |
| 151 | GETVALUES returns 10,20,30 |
| 152 | Short GETVALUES buffer unchanged |
| 153 | Invalid GETVALUES arguments |
| 154 | Unsupported opcode returns -2 |
| 155 | Repeat dispatcher calls without state corruption |
| 156 | BCXSEL selects/registers without direct required ID |
| 157 | BCXSEL upgraded by BCXREQ, only one INCLUDE/descriptor |
| 158 | Excluded BCPLDEMO absent from linked module |

Each has source.bcpl, expected.txt, README.md and an extension-selection
fixture. A single regression number must be runnable independently,
with numbered RUN/GO jobs, reliable PASS/FAIL diagnostics and saved
operator-local evidence. Extension-selection fixtures are consumed by
IFOX on MVS; they are not BCPL code.

## Two build/acceptance modes

- **Source mode:** compile BCPL and assemble the consolidated BCPLDEMO
  from Git-controlled sources to **temporary MVS datasets**.
- **Installed mode:** link the same compiled BCPL clients against the
  explicitly installed BCPLDEMO object PDS member, using a
  member-qualified IEWL INCLUDE and MVS-resident BCX catalog.

An installed-mode success is required for R.5 acceptance.
A passing source-mode test is useful developmental evidence only.

## Persistent-data safety gate

Candidate objects belong only in a **separately approved** optional
extension destination; do not silently overwrite BOOT_OBJ or BOOT_DEVOBJ.
Before the first persistent write, present the exact manifest-managed
target, initial membership, install/replace authority, read-back
validation, backup and rollback steps, and obtain an explicit decision
from the owner. Preparing an installation procedure is not authority
to execute it.

## R.5 exit

Document successful individual and contiguous 146–158 MVS runs,
preservation of 00–145 (including expected 083 skip), installed
member MAP/XREF proof, no regression, fresh Git-based rebuild and
operator-approved recovery procedure. Mark R.5 CLOSED only on an
explicit owner disposition. Until then preserve failures and
unverified status honestly.

## Implementation status (23 October 2026)

**GitHub main sources prepared; R.5 is not accepted.**

- The combined bcpldemo.asm candidate contains DMODESC and DMODISP.
- Numbered cases 146-158 now have source.bcpl, expected.txt,
  extension-selection.asm and README files.
- The existing numbered runner selects test-only MVS IFOX/IEWL/GO
  construction only for these marked cases; 00-145 retain their path.
- Source mode assembles BCPLDEMO into temporary MVS objects.
- Installed mode links a read-only EXTLIB(BCPLDEMO) PDS member,
  but **no destination PDS or member installation is approved**.
- JCL preparation and IEWL MAP verifier have host-only unit tests.

**Not yet performed:** execute the new offline tests on the operator's
checkout; MVS source-mode job results; member-qualified IEWL PUNCH
confirmation; physical object-PDS installation/read-back/recovery;
full native regression; clean-room R.5 package acceptance.

### First verification commands (from repository root)

```sh
git pull --ff-only
python3 -B -m unittest discover -s tools/checks -p 'test_r5*.py' -v
python3 -B tools/checks/prepare-r5-extension-regression.py --check
bash -n bootstrap-toolchain/regression/run-test.sh
tools/bootstrap/run-regression --check-numbering
# Only after all preparation checks PASS:
tools/bootstrap/run-regression 146 147 --show-output
```

The first MVS run should establish no-extension startup (146) and the
combined source plus BCXREQ selection (147). If either fails, preserve
its JES/IFOX/IEWL report before attempting all 146-158 cases. Tests
compile through the resident demoted Cambridge compiler under MVS;
no R.5 PASS may be asserted from host preflight alone.

## First live R.5 regression attempt, 23 October 2026

The owner ran the original six host unit tests (all PASS), generated
synthetic JCL for all thirteen cases, checked numbering and Bash
syntax, then executed R.5 regression 146 and 147 on MVS:

| Case | Compile job | Native job | Executed results |
| --- | --- | --- | --- |
| 146 | 3723 | 3724 | IFOX/IEWL/GO RC=0000; `R5 EXT 146 PASS` printed |
| 147 | 3725 | 3726 | IFOX/IEWL/GO RC=0000; `R5 EXT 147 PASS` printed |

**The runner nevertheless reported FAIL for both cases**, solely
because its R.5 IEWL MAP verifier reported `entry address was not zero`.
Code review found that the verifier sought the entry-address field
only inside a truncated cross-reference-table slice. It now searches
the complete JES report for exactly one zero-valued IEWL entry, and
retains the existing CSECT/BCPLREG size and package inclusion checks.
Two additional offline tests cover alternative entry-field positions,
missing entries, duplicates and nonzero entries.

The actual full IEWL MAP was not included in the operator's pasted
console report. **Neither 146 nor 147 is yet formally accepted.**
Confirm the correction against the saved real reports without
resubmitting jobs:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_r5*.py' -v
python3 -B tools/checks/check-r5-extension-report.py \
  workarea/native-regression/146-optional-empty/job-report.txt \
  --test-number 146
python3 -B tools/checks/check-r5-extension-report.py \
  workarea/native-regression/147-bcpldemo-query-size/job-report.txt \
  --test-number 147
```

If a report still fails, inspect the true IEWL `ENTRY ADDRESS`
line rather than assuming zero. Preserve the original failed-run
results in the evidence record.
