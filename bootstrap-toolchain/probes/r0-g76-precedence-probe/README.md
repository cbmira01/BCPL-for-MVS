# Milestone Runtime Extensions — R.0 G!76 precedence probe

**March:** R.0 — Evidence and contract (**open**). **Status:**
**MVS PASS in JOB 2199**, BLIB-present precedence only. See the
[actual JOB 2199 evidence](../../../packaging/runtime-extensions-r0-g76-job-2199-evidence-20261021.md).
The BLIB-absent fallback and installed-object provenance remain open.
R.1 has not started.

## What it tests

The real installed `BOOT_OBJ(BCPLMAIN)` imports application and BLIB
exports before entering BCPL `START`. It conditionally supplies its local
`WRITEST` fallback in G!76 only if G!76 is still unset. The installed
`BOOT_OBJ(BLIB)` exports `WRITEF` in G!76, as demonstrated by JOB 2197.

This focused probe tests the *actual startup result*, not just the
presence of G!76 in source or an independent simulator:

1. The installed interpreter-hosted **demoted Cambridge compiler**
   compiles `source.bcpl` into native CG370 assembler.
2. The JCL generator gives the application CSECT a name and adds a
   **test-only** `(G!151, R0CK76)` application export. Existing CG370
   executable instructions and the original START export remain intact.
   G!151 is test-local, **not a Global Number Registry assignment**.
3. IEWL includes the **installed** `BOOT_OBJ` objects for `BCPLMAIN`,
   `BCPLIO`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, and `BLIB`, along with the
   two temporary test-only objects. No installed objects are modified.
4. The actual BCPL `START` invokes the native BCPL-ABI routine `R0CK76`.
   That routine reads the relocated installed BLIB export trailer,
   locates G!76, and compares its entry address to `G!76` in R12's
   initialized global vector. It returns 0 on exact equality or 8 on
   mismatch, missing export or malformed/oversized module length.
5. If matched, BCPL writes `R0 G76 INSTALLED BLIB PASS` and terminates
   via FINISH, expecting GO RC=0000. Otherwise it invokes STOP(8).

This is stronger than observing an export alone, but still **does not**
prove generic pre-START collision rejection, optional-package registrar
behavior, the absent-BLIB fallback, or arbitrary pointer safety.

## Run after pulling from GitHub main

With TK5 running, working source-built `BOOT_OBJ` objects, and local
`dspal` credentials configured:

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-g76-precedence-probe/run.sh
```

The runner runs local unit tests and dry checks, compiles the application
under `ICINT19`, prepares a password-bearing JCL deck **only under
ignored workarea**, submits one `R0G76` evidence job, and checks its
step RCs and actual output. The JCL uses two IFOX assemblies, one IEWL
link-edit and one GO; every step must have RC=0000 and GO must print
exactly one independent PASS record. The runner preserves the JES report,
linker map and source hashes in
`workarea/runtime-extensions-r0-g76/`.

**Offline-only check** (no MVS jobs):

```bash
probe=bootstrap-toolchain/probes/r0-g76-precedence-probe
python3 -B -m unittest discover -s "$probe" -p test_probe.py -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

Successful local checks validate the generator and source shape only;
they do **not** establish IFOX, IEWL or GO success. Do not count a
`WRITES` string in an assembler listing as an actual GO output marker.
Preserve the observed JOB numbers, GO records and IEWL MAP for the R.0
acceptance record; do not commit credential-bearing JCL or full raw JES
reports. The installed `BOOT_OBJ(BLIB)` member's independent build
provenance remains a separate gate.
