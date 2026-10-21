# Milestone Runtime Extensions — R.0 Decision A stage-2 object identity

**March:** **R.0 — Evidence and contract (open)**. **R.1 — Generic registration foundation has not started.**
**Status:** **MVS tests pending.** The owner approved a narrow, read-only
`BCPLMEM` rebuild/compare workflow after stage-1 JOBs 2207–2216 passed.
See [stage-2 design](../../../packaging/runtime-extensions-r0-decision-a-stage2-design-20261021.md).

The probe compares **relocatable FB/80 object records**, not load
modules. `BOOT_OBJ(BCPLMEM)` is **never written**, installed, rebuilt
in place, or removed. The generator uses the canonical `BLDBMAIN`
IFOX options `OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD`; all generated
object records use temporary `&&` datasets. The member build reads
**Git-tracked** `bootstrap-toolchain/asm/bcplmem.asm`, not an MVS
PDS source copy that might differ. The canonical target DSN is
resolved through `config/dspal.yaml` and `dspal-core.py`, not hardcoded.

## First: calibrate IEBCOMPR (no BOOT_OBJ access)

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-object-identity-probe/run.sh calibrate
```

`R0BICAL` has five MVS steps:

| Step | Action | Required RC |
| --- | --- | ---: |
| ASMA | Assemble fixture A to binary `&&OBJA` | 0000 |
| ASMB | Assemble deliberately different fixture B to `&&OBJB` | 0000 |
| COPYA | IEBGENER copies A into temporary `&&COPYA` | 0000 |
| SAME | IEBCOMPR compares A with copied A | 0000 |
| DIFFER | IEBCOMPR compares A with deliberately different B | **0008** |

`DIFFER` returning RC=0008 is **expected**, so the JES **highest RC
will be 0008**, not 0000. A mismatch in these **exact** return codes,
missing/empty IFOX punched object-deck evidence, or an operational
error stops the run. The verifier deliberately **does not** treat any
RC=0008 as proof of a real data mismatch: check IEBCOMPR's printed
messages for unequal records and ensure no access/open failure.

**Do not proceed until reviewing the entire actual calibration
SYSPRINT and confirming SAME compared nonempty identical binary
objects, while DIFFER detected the intentionally changed bytes.**

## After calibration: allow the read-only incumbent comparison

After independently reviewing the successful calibration report,
acknowledge it explicitly for the same Git revision:

```bash
out=workarea/runtime-extensions-r0-object-identity
printf '%s\n' "$(git rev-parse HEAD)" > "$out/confirmed-calibration.txt"
bash bootstrap-toolchain/probes/r0-object-identity-probe/run.sh member
```

`R0BIMEM` builds a fresh `BCPLMEM` object to temporary `&&MEMOBJ`
with step `ASMMEM` and compares it against the **input-only** dataset
`BOOT_OBJ(BCPLMEM)` with `IEBCOMPR` step `COMPARE`. Requirements:

- `ASMMEM` must return 0000 with nonempty object records.
- `COMPARE` returning 0000 **reports equal records**, subject to
  checking the actual utility report and successful calibration.
- `COMPARE` returning 0008 needs manual inspection. A real unequal
  result means the installed and freshly built bytes **differ**;
  an open error/utility failure **is not** accepted as inequality.
- RC other than 0/8, missing steps, or an error diagnostic fails.
- The comparison never installs, overwrites or promotes any object.

If the historical utility rejects `PDS(member)` as sequential input,
**stop**. Do not edit the accepted object, add an untested transfer,
or treat a SYSOUT listing as a binary comparison. The separately
reviewed fallback is a calibrated input-only `IEBGENER` copy into a
temporary dataset and a re-comparison of two temporary datasets.

## Local-only checks

```bash
probe=bootstrap-toolchain/probes/r0-object-identity-probe
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-jobs.py" calibrate --check
python3 -B "$probe/make-jobs.py" member --check
bash -n "$probe/run.sh"
```

The generator refuses uncommitted changes to the relevant source
or probe during a real run. Authenticated JCL is generated privately
(`0600`) under ignored `workarea/runtime-extensions-r0-object-identity/`;
**never commit credential-bearing JCL, printer reports or private
configuration**. The generator writes per-run source hashes and
current Git SHA there. The verifier checks actual `IEF142I` step
results and IFOX `TOTAL RECORDS PUNCHED` counts; the operator
retains the utility report for independent comparison.

## Evidence boundary

`IEBCOMPR` is documented in *OS/VS2 MVS Utilities Release 3.8*
(GC26-3902-1) with `COMPARE TYPORG=PS`; current IBM documentation
also describes the logical-record comparison. These are **documented
expectations**, not evidence that TK5 has passed the tests yet.

Even an actual equal comparison proves only the two observed FB/80
record streams match at that moment. It does not establish the
17 October production build revision, an independent cryptographic
attestation of the installed object, or registered optional modules.
Those remain separate R.0 and R.1 matters. 
