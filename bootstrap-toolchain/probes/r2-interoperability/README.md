# Milestone Runtime Extensions — R.2 interoperability probes

**Status:** **R.2 CLOSED 22 October 2026.** BCPLDEMO G!203 passed
JOB 3075; test-only R2TESTB and the 0/A/B/A+B matrix passed JOB 3080.
The consolidated campaign passed JOBs **3091/3092**. See the
[R.2 acceptance and owner closure](../../../packaging/runtime-extensions-r2-closure-20261022.md).
R.3 — Packaging and acceptance is now ACTIVE.

The first test uses `demo.bcpl` (a separately compiled BCPL caller),
`registry-demo.asm` (real BCRG selection and required-package declaration),
and the [BCPLDEMO maintained example](../../extensions/bcpldemo/README.md).
The single resulting link uses the same R.1 `RGINIT` and temporary
`BCPLMAIN` adaptation proved in the completed R.1 campaign.

To inspect the generated in-memory test deck, run:

```sh
python3 -m unittest discover -s \
  bootstrap-toolchain/probes/r2-interoperability -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/r2-interoperability/make-job.py --check
```

For the end-to-end MVS candidate procedure, expected GO marker, and
resource guarantees, see the BCPLDEMO README. **The first extension-A
MVS job passed (JOB 3075);** see [the reviewed JES/IEWL evidence](../../../packaging/runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md). The second extension
and matrix remain pending. Do not reuse G!203
for the second test extension; it remains BCPLDEMO's permanent assignment.

## Four-link R.2 matrix (actual MVS JOB 3080 PASS)

Extension A is project-maintained `BCPLDEMO` at permanent G!203.
Extension B is **test-only** `R2TESTB` at temporary fixture G!299,
documented in [the extension B notes](../../extensions/r2testb/README.md).
G!299 is not a new permanent global-number assignment.

The generator prepares four separate BCPL applications and corresponding
`BCPLREG` selection tables: zero, A, B and A+B. A single MVS job
assembles one temporary `BCPLMAIN` and one registrar object, then reuses
those exact objects in all four IEWL links and GO steps. Only selected
optional descriptors and dispatchers enter each link.

Credential-free preflight from repository root:

```sh
python3 -m unittest discover \
  -s bootstrap-toolchain/probes/r2-interoperability -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/r2-interoperability/make-matrix.py --check
```

After the bootstrap toolchain is available, compile all four independent
BCPL clients and generate the private MVS candidate deck:

```bash
mkdir -p workarea/runtime-extensions-r2/compiled
for profile in zero a b both; do
  source_file="$profile.bcpl"
  case "$profile" in
    a) source_file=demo.bcpl ;;
    b) source_file=onlyb.bcpl ;;
  esac
  tools/bootstrap/compile-mvs \
    "bootstrap-toolchain/probes/r2-interoperability/$source_file" \
    --job-name "R2C${profile^^}" \
    --output "workarea/runtime-extensions-r2/compiled/$profile.s370.asm" \
    || exit 1
done
python3 bootstrap-toolchain/probes/r2-interoperability/make-matrix.py \
  --generated-dir workarea/runtime-extensions-r2/compiled
bash tools/mvs/submit-jcl workarea/runtime-extensions-r2/r2-matrix.jcl
```

The clients are `zero.bcpl`, `demo.bcpl` (A, already exercised
independently in JOB 3075), `onlyb.bcpl` and `both.bcpl`.
Expected, **not yet observed**, one GO marker per selection:

```text
R2 MATRIX ZERO PASS
R2 BCPLDEMO G203 PASS
R2 MATRIX B PASS
R2 MATRIX AB PASS
```

Verify all fourteen assembler steps, four IEWL steps, four GO return codes,
and each IEWL MAP/XREF; do not infer acceptance from deck generation.
Every candidate object/load dataset is `&&` temporary and `BOOT_OBJ`
is linked read-only. Missing-dependency, collision, malformed descriptor
and absent-module rejection tests remain separate R.2 obligations.
No R.2 closure, object promotion, or R.3 start is implied.

## Consolidated R.2 remaining acceptance checks

The [consolidated runner](ACCEPTANCE.md) provides a single operator
command, `python3 tools/bootstrap/run-r2-acceptance --execute`, for a
fresh positive matrix plus one 21-case negative/dependency batch.
This new campaign is an unverified candidate until actual MVS JES
and IEWL evidence is reviewed. R.2 remains ACTIVE.
