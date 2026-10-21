# Milestone Runtime Extensions — R.0 actual export-trailer evidence

**March:** R.0 — Evidence and contract (**open**). **Status:** MVS
**PASS** in JOB 2197; the compiler ran in JOB 2196. See the
[recorded evidence and exact 22 exports](../../../packaging/runtime-extensions-r0-trailer-job-2197-evidence-20261021.md).
The new G!76 conditional-precedence check is separate and not yet
MVS-verified.
No R.1 registration, `BCPLMAIN` alteration, package implementation,
or accepted-object change occurs.

This is a **committed test-only evidence tool**, prepared against the
owner-approved R.0 ABI at GitHub commit
`658239382751878f7c91f9194bd927e2be462168`.
It is not an R.0 completion or closure claim.

## Purpose and provenance

Decision **E**, in `packaging/runtime-extensions-r0-owner-abi-decisions.md`,
requires an effective owner ledger based on **actual** exports rather than
`LIBHDR` declarations or source-derived BLIB candidate names.

This probe links:

1. A tiny **native CG370 application** compiled by the installed demoted
   Cambridge compiler through the existing `tools/bootstrap/compile-mvs`.
   Only its unnamed `CSECT` label is changed to `R0APP`, and `ENTRY
   R0APP` is added; its executable code and compiler-generated trailer
   are not rewritten.
2. The real installed **`BOOT_OBJ(BLIB)` relocatable member**, through
   explicit IEWL inclusion. This is **not** a freshly generated substitute
   for that installed BLIB. `BCPLMAIN`, `BCPLIO`, `BCPLMEM`, `BCPLBYTE`,
   and `BCPLAPT` are also included **read-only** from `BOOT_OBJ` so
   the load is fully resolved. Only the separate observer is executed.
3. `trailer-observer.asm`, an isolated IFOX routine that reads the module
   prefixes, finds trailer sentinels, and emits relocated `(4*N,address)`
   values. It **never calls `R0APP`, `BLIB`, or `BCPLMAIN`**.

The first compiler job produces the application assembler source; the
second job assembles two objects, link-edits a **temporary `&&` load
module**, and executes the observer. It writes only ordinary SYSOUT
and ignored host `workarea/` files; it does **not** install any object
or load member or modify a dataset.

## Single-command execution on the project MVS machine

From a clean repository checkout on GitHub `main`, pull the tools.
With TK5 running and the normal `dspal.local.yaml` job credentials
configured, execute:

```sh
git pull --ff-only
bash bootstrap-toolchain/probes/r0-export-trailer-probe/run.sh
```

The script runs offline checks, compiles the baseline application, makes
a credential-bearing JCL file under ignored `workarea/` with mode 0600,
submits it, retrieves the JES report, checks all MVS step return codes,
and extracts `ledger-job-JOBNUMBER.json` and `.tsv`.
Do not commit generated JCL (which may embed job credentials) or raw
JES reports to GitHub.

## Standalone dry run (no MVS required)

```sh
probe=bootstrap-toolchain/probes/r0-export-trailer-probe
python3 -B -m unittest discover -s "$probe" -p test_trailers.py -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

After compiling the application, to create the evidence deck without
submitting it:

```sh
python3 -B "$probe/make-job.py" \
  --generated workarea/runtime-extensions-r0-trailers/app.s370.asm
```

The offline synthetic `--check` input tests structural transforms; it
**does not establish an IFOX PASS**. On a real MVS run, require:

- Compiler `R0TRCMP` successful, with exactly one ICINT completion code 0.
- Evidence job `R0TRAIL`: **ASMT, ASMA, LKED, GO** each RC=0000.
- IEWL MAP/XREF shows `R0TRACE`, `R0APP`, `BLIB` and resolved core
  symbols and **no unresolved external references**.
- **Actual GO/QOUT** records, in this order:
  `R0TR APP BEGIN`, application export pairs, LIMIT/END, then
  `R0TR BLIB BEGIN`, installed BLIB export pairs, LIMIT/END,
  followed by `R0TR PASS APP AND INSTALLED BLIB`.
  Records are 80-byte FB SYSOUT lines, with 8-digit EBCDIC hex
  offset/address fields; `parse-report.py` enforces counts, alignment,
  range and ordering. The hex addresses are **relocated runtime**
  addresses, not portable stable symbol identities.
- The app exports `G!1` (`START`). The BLIB export set is recorded from
  its actual linked member. Record all observed application/BLIB overlaps;
  **do not automatically approve any new waiver**.

## Interpretation and boundaries

`parse-report.py` creates an observed export table and highlights possible
collisions with the **source-derived** native direct writes documented in
`packaging/runtime-extensions-r0-native-global-owner-inventory-20261020.md`.
The latter are **not** themselves measured by this GO program.

`G!76` is a documented **conditional** `BCPLMAIN` fallback. Merely
observing BLIB's G!76 export does not prove FINISH/STOP behavior or test
the historical conditional write; that remains a separate regression.
`G!150` is likewise not declared safely free merely because one test
application omits it. Historical reservations remain governed by the
Global Number Registry.

The observer uses the current compiler module prefix at `+10`,
checks a **positive length below 16 KiB**, and limits pair offsets to
`G!0..699`. These are narrowly bounded observations of trusted,
reproducibly linked inputs. This does **not** establish the accepted
Decision A's general descriptor trusted-extent contract against
arbitrary forged pointers. Nor is it a production collision detector.

**Do not declare R.0 closed yet.** Remaining gates include independently
verifying that the installed BLIB member corresponds to the intended
build, testing historic overlap behavior and optional collision
rejection, choosing Decision G's exact limits/diagnostics, and an R.0
acceptance review. Production `BCPLMAIN` integration belongs to R.1.

## Expected host evidence

- `workarea/runtime-extensions-r0-trailers/app.s370.asm`
- `workarea/runtime-extensions-r0-trailers/r0-trailer.jcl` (private)
- `workarea/runtime-extensions-r0-trailers/source-provenance.txt`
- `workarea/runtime-extensions-r0-trailers/job-NNNN.txt`
- `workarea/runtime-extensions-r0-trailers/ledger-job-NNNN.json`
- `workarea/runtime-extensions-r0-trailers/ledger-job-NNNN.tsv`

The operator should inspect the IEWL output and keep the exact JOB
numbers, return codes and observed GO lines when recording the final
ownership audit; no PASS must be inferred from source literals.
