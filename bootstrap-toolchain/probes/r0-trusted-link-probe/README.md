# Milestone Runtime Extensions — R.0 Decision A trusted-link probe

**March:** **R.0 — Evidence and contract (open)**.
**Purpose:** Gather isolated, read-only build/link evidence for the
owner-approved **Decision A — Trusted extents**.
**Status:** Source and dry-run host checks prepared. **MVS executions
not yet observed**. **R.1 — Generic registration foundation has not
started**. Do not treat the probe as a production registrar.

## What is linked

Each profile generates four independently assembled IFOX object decks:

| IFOX step | CSECT | Link-defined symbols | Source |
| --- | --- | --- | --- |
| `ASMD` | `R0ATST` | `R0ATST` | `validator.asm` with selected expected status |
| `ASMR` | `R0AREG` | `R0RB`, `R0RE` | one 44-byte registry |
| `ASMP` | `R0APKG` | `R0PB`, `R0PE` | one 56-byte descriptor |
| `ASMF` | `R0AFUN` | `R0FUNC`, `R0FIN` | two non-invoked code addresses |

IEWL is invoked with `NCAL,LIST,XREF,MAP` and four distinct temporary
`&&` FB/80 object decks. It creates an **only-temporary** `&&R0LOAD`
load module and executes validator entry `R0ATST`. No application
or `BCPLMAIN` is linked or modified. No accepted `BOOT_OBJ` or
`BOOT_DEVOBJ` object is read or written.

A source-ownership preflight verifies each public symbol definition,
which CSECT contains it, and which source provides it. The generator
saves a SHA-256 for each rendered assembler input, plus an expected
symbol-owner ledger, to ignored `workarea/`. A duplicated, missing or
moved source symbol is rejected **before** JCL submission.
This is *source provenance*, not cryptographic proof about the loaded
MVS image. The owner must inspect the actual IEWL MAP/XREF as well.

## Negative profiles

The validator checks physical registry and descriptor extents before
reading variable fields. It compares the registry's relocated descriptor
pointers against independently linked symbol addresses **before
following them**. It recognizes only zero and independently linked
`R0FIN` as allowed finalizer addresses; the callback is never invoked.
All internal results are the **approved Decision G identifiers**, not
JES step return codes.

| Profile | JOB name | Required internal status | Actual GO/QOUT marker |
| --- | --- | ---: | --- |
| `valid` | `R0ALINK` | 0 | `R0 A VALID LINK PASS` |
| `goodhook` | `R0AHOOK` | 0 | `R0 A LINKED HOOK PASS` |
| `regzero` | `R0AREGX` | 1001 | `R0 A REG EXTENT 1001 PASS` |
| `regunal` | `R0AUNAL` | 1001 | `R0 A REG ALIGN 1001 PASS` |
| `pkgbound` | `R0APKGE` | 1004 | `R0 A PKG EXTENT 1004 PASS` |
| `reglen` | `R0ARLEN` | 1003 | `R0 A REG LENGTH 1003 PASS` |
| `pkglen` | `R0APLEN` | 1006 | `R0 A PKG LENGTH 1006 PASS` |
| `regvers` | `R0ARVER` | 1002 | `R0 A REG HEADER 1002 PASS` |
| `pkgvers` | `R0APVER` | 1005 | `R0 A PKG HEADER 1005 PASS` |
| `badhook` | `R0ABADH` | 1013 | `R0 A HOOK TARGET 1013 PASS` |

The malformed registry extent profiles modify only the test driver's
**observed pointer**, leaving the independent registry CSECT intact;
`pkgbound` modifies the registry's end-pointer field. These simulate
bad supplied bounds, not damaged or hostile MVS storage. Neither the
wrong-size nor wrong-version case reads beyond its mapped static CSECT.

Expected MVS `ASMD`, `ASMR`, `ASMP`, `ASMF`, `LKED` and `GO` steps each
return **RC=0000** only when the fixture matches its expected internal
status; unexpected acceptance/rejection causes GO RC=0008. Each
GO run must emit its exact marker **once** as a QOUT record. IFOX
source listings alone do not count as GO evidence.

## Run on Morkies

First test the isolated **valid** case. Inspect its JES report and
IEWL MAP/XREF before running the negative profiles:

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-trusted-link-probe/run.sh valid
```

The script runs all offline tests and ten credential-free JCL checks,
then submits **only** the named profile. It prints the job number,
step summary, QOUT verification, and local report path.
After successful source/link ownership inspection, each remaining
profile can be run by replacing `valid` with the profile name.

For offline tests without an MVS connection:

```bash
probe=bootstrap-toolchain/probes/r0-trusted-link-probe
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
for p in valid goodhook regzero regunal pkgbound reglen pkglen regvers pkgvers badhook; do
    python3 -B "$probe/make-jobs.py" "$p" --check
done
bash -n "$probe/run.sh"
```

Normal (non-`--check`) job generation uses local private batch credentials.
Authenticated JCL is mode 0600 in ignored
`workarea/runtime-extensions-r0-a/`; **never commit it or the full JES
printer output**. Expected source hashes and Git revision are also
recorded locally. No MVS installation procedure is part of this probe.

## IEWL ownership acceptance checklist

Before calling an executed profile a *trusted link* result, retain an
actual **IEWL MAP/XREF excerpt** identifying these four separate CSECTs:

- `R0ATST` from the `ASMD` temporary object;
- `R0AREG` with `R0RB`/`R0RE` from `ASMR`;
- `R0APKG` with `R0PB`/`R0PE` from `ASMP`;
- `R0AFUN` with `R0FUNC`/`R0FIN` from `ASMF`.

Confirm their relative addresses/sizes agree with the intended
source-generated extents (44 and 56 bytes for registry and package),
that the symbols resolved without an unintended external provider, and
that the linked code has no unresolved addresses. Compare source
hashes/Git revision with the generated manifest. An IFOX source line or
GO success marker **alone** does not prove IEWL symbol ownership.

The test's pre-submit source-owner guard deliberately rejects a wrong
CSECT, missing definition or duplicate declaration. **Neither it nor
IEWL alone proves an arbitrary pointer is safe, validates hostile
objects, or establishes an installed `BOOT_OBJ` member's build identity.**
Actual installed-object byte identity is a separate **second stage**:
first agree on a binary-safe MVS record comparison method, then rebuild
to temporary storage and compare without replacing accepted members.
This probe does not undertake that stage.
