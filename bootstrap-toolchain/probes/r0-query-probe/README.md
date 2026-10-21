# Milestone Runtime Extensions — R.0 shared QUERY probe

**March:** R.0 — Evidence and contract (**open**).
**Contract:** [Owner-approved shared `QUERY` ABI](../../../packaging/runtime-extensions-r0-query-abi-decision-20261021.md)
(21 October 2026). **Status: PASS under actual MVS — JOB 2206**,
five steps RC=0000, ten host tests PASS and the exact BCPL GO
marker verified. See [JOB 2206 evidence](../../../packaging/runtime-extensions-r0-query-job-2206-evidence-20261021.md).
R.1 — Generic registration foundation has not started.

The probe demonstrates the shared version-1 `QUERY` ABI over **two
independently assembled test-only native dispatcher objects** called
through one separately compiled BCPL application. The dispatchers use
**G!298 and G!299 as temporary fixture bindings only**. They do not
represent allocated globals for BCPLQSAM, BCPLTIME or any product API.
The accepted six `BOOT_OBJ` members are included **read-only**.

## Files and test behavior

- `caller.bcpl`: native BCPL client with START/STOP; checks six-word
  and eight-word QUERY descriptors, versions, opcode bitmap, flags,
  nonnull-zero capacity `-1`, negative/null errors `-3`, undersized
  all-or-nothing writes, trailing-word preservation and supported and
  unsupported non-QUERY opcodes. A failed check executes `STOP(8)`;
  success writes one unique BCPL output marker.
- `dispatcher-a.asm`: test-only six-word format-1, API 1.0; bitmap 1
  advertises opcode 1; it returns `101` for opcode 1.
- `dispatcher-b.asm`: separate test-only eight-word format-1, API 3.2;
  bitmap 5 advertises opcodes 1 and 3; it returns `201` and `203`.
  The extra words are fixture values 77 and 99, not a general new
  capability-map definition.
- `make-job.py`: validates the compiler-generated CG370 export trailer,
  retains its G!1 START entry, then adds **only** test-local relocated
  G!298 and G!299 entries. This intentionally bypasses the *future*
  generic registrar, like the proven Q.0 and R.0 native-linkage probes.
- `run.sh`: tests and generates private JCL in ignored `workarea/`,
  compiles the BCPL client with the **demoted Cambridge compiler**,
  assembles application and dispatchers in three separate IFOX steps,
  links with IEWL, submits GO and verifies the report.
- `verify-report.py`: requires one actual GO output line:
  `R0 QUERY TWO DISPATCHERS PASS`.
- `test_query.py`: credential-free offline unit tests and synthetic
  JCL generation; does not claim an actual MVS run.

## Reproduce on Morkies

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-query-probe/run.sh
```

The runner first executes host unit tests and a synthetic generator
check, then compiles the BCPL client, checks the real generated-source
JCL, and writes an authenticated deck under
`workarea/runtime-extensions-r0-query/r0-query.jcl` (private mode
0600). The MVS job name is **R0QUERY**. In **actual JOB 2206**, **ASMA**
(BCPL-generated application), **ASMB** (dispatcher A), **ASMC**
(dispatcher B), **LKED** and **GO** each returned RC=0000.
The BCPL caller was compiled earlier in **JOB 2205**.
The verified actual GO output:

```text
R0 QUERY TWO DISPATCHERS PASS
```

Linker/map examination should show `R0APP`, `R0QAA`, `R0QBB` and the
six installed Core Runtime/Base Library object members. All object
and load modules created by this harness use **temporary `&&`
datasets**. No accepted object PDS member is installed or replaced.

## Offline-only

```bash
probe=bootstrap-toolchain/probes/r0-query-probe
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

No credentials or JES reports are created by `--check`. Do not commit
generated authenticated JCL, full printer reports or local credentials.

## JOB 2204 host-generator correction

The initial Morkies attempt compiled the BCPL client successfully as
**JOB 2204** (COMP and SVCODE both RC=0000) but stopped before the
R0QUERY MVS job: a text-count check falsely rejected G!299 because
the real generated trailer's maximum-offset header and its final
export pair legitimately both contained `DC F'1196'`. The generator
now decodes and checks **actual export pairs**, instead of counting
literal appearances. A regression test covers the G!299 = 1196
maximum. The owner-supplied JOB 2204 generated-source excerpt
was checked locally and generated 715 synthetic JCL cards after the
fix, without credentials. That was the earlier failed host preparation
attempt; the subsequent **R0QUERY JOB 2206 passed**.

## Evidence boundary

This test is **not** production `BCPLREG` registration, package
selection/dependency validation, optional global collision rejection,
full register-preservation verification, or implementation of QSAM,
TIME or DEC. It tests two known synthetic packages through direct
*test-only* CG370 trailer entries, not absent-module discovery.
An eight-word descriptor preserves the approved six-word prefix but
is not itself a public appended-field allocation. JOB 2206 verifies
**only the exercised native caller/dispatcher behaviors**. Full
`BCEX` version consistency and actual registrar integration remain
unverified. The complete IEWL MAP/XREF was not supplied here.
The R.0 gate review still has other open items, and R.1 has not started.
