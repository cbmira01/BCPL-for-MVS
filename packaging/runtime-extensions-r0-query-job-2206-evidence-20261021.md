# Milestone Runtime Extensions — R.0 shared QUERY, JOB 2206

**Date:** 21 October 2026.
**March:** **R.0 — Evidence and contract (open)**.
**Disposition:** **PASS — isolated two-dispatcher native BCPL QUERY ABI
probe**, accepted for the R.0 evidence record. Not production optional
registration or completion of R.0.
**Source tested:** GitHub `main` commit
`3aae5fad3937fdf9ed2cb1d772091816e9387647`.
**Specification:** [owner-approved shared QUERY v1 ABI](runtime-extensions-r0-query-abi-decision-20261021.md).
**Probe:** [R.0 shared QUERY probe](../bootstrap-toolchain/probes/r0-query-probe/README.md).

## Operator reproduction and observations

The owner ran:

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-query-probe/run.sh
```

The pull fast-forwarded `main` from `b1a9bce` to `3aae5fa`.
**Ten** Python tests passed. The credential-free synthetic job check
reported **189 cards**. **JOB 2205** compiled `caller.bcpl` using the
interpreter-hosted **demoted Cambridge compiler**, saving native
System/370 assembler to
`workarea/runtime-extensions-r0-query/app.s370.asm`.
The generated-source check then reported **715 cards**.
The runner submitted `R0QUERY` as **JOB 2206**, observed on
**21 OCT 26 15:30:40–15:30:40**.

| Step | Program | Actual result |
| --- | --- | --- |
| ASMA | IFOX00 — native BCPL caller | RC=0000 |
| ASMB | IFOX00 — dispatcher `R0QAA` | RC=0000 |
| ASMC | IFOX00 — dispatcher `R0QBB` | RC=0000 |
| LKED | IEWL — temporary load module | RC=0000 |
| GO | Linked native BCPL executable | RC=0000 |

**JOB RESULT: SUCCESS; HIGHEST RC: 0000.**
The assembler reported **zero flagged statements** and **highest
severity 0**. The submitted JES job reported **717 cards**.

The separate report verifier required and found exactly one
**actual GO output line**, rather than merely a literal in the
assembler listing:

```text
VERIFIED QUERY GO OUTPUT: R0 QUERY TWO DISPATCHERS PASS
```

The unique output text itself was:

```text
R0 QUERY TWO DISPATCHERS PASS
```

The complete JES report and IEWL MAP/XREF were not supplied for
independent line-by-line inspection in this exchange. The reported
step RCs and the output-verifier result are the accepted owner
execution evidence. The runner retained
`workarea/runtime-extensions-r0-query/job-2206.txt` locally.

## Exactly what the test exercised

The compiled BCPL application calls **two separate test-only
assembler dispatchers** via test-local **G!298** (`R0QAA`) and
**G!299** (`R0QBB`). Those global numbers are *temporary fixture
bindings*, **not** new Global Number Registry allocations.

- A returns a **six-word** shared format-1 descriptor with API
  **1.0**, opcode bitmap `1` and no package capability flags.
- B returns an **eight-word** format-1 descriptor with API **3.2**,
  opcode bitmap `5`, flags `2`, and two appended fixture values.
- The caller checks size inquiries `(0,0,0)` yielding 6 and 8;
  `-3` for invalid null/nonzero and negative-capacity cases;
  `-1` for nonnull buffers with zero or insufficient capacity;
  entire descriptor writes, no partial write, preservation of
  trailing words, versions, bitmap/flag contents, and added words.
- Both supported synthetic opcodes return their expected values:
  A opcode 1 = 101; B opcode 1 = 201 and opcode 3 = 203.
  Unsupported opcodes, including 99, return `-2`.
- Each failed BCPL assertion executes `STOP(8)`; successful GO
  reaches the unique PASS record and normal FINISH.

The temporary application uses **test-only CG370 export-trailer
entries** that relocate the two independent dispatcher addresses.
It includes accepted `BOOT_OBJ` Core Runtime and BLIB members
**read-only**. The link writes a temporary `&&` load module,
not an accepted object PDS member.

## Limitations — not proven by JOB 2206

- **No `BCPLREG` startup registration**, missing-package handling,
  dependency checks, ownership collision rejection, transactional
  publication or generic pre-START diagnostic behavior.
- **No complete `BCEX` descriptor verification**: the two synthetic
  dispatchers report API versions, but the job does not compare those
  versions against linked production `BCEX` descriptors.
- **No production BCPLQSAM, BCPLTIME, or BCPLDEC implementation.**
  G!298/G!299 are test-local and must not be represented as
  permanent or site-wide assignments.
- No broad memory-safety guarantee for fabricated pointers, full
  register-preservation audit, or independent review of JOB 2206
  IEWL MAP/XREF and installed object-build provenance.

**Conclusion:** The **shared version-1 QUERY contract has a passing,
native BCPL, two-dispatcher R.0 isolated execution test**, extending
the earlier single-dispatcher Q.0 JOB 2157. The shared QUERY contract
and its isolated client test are complete for the R.0 gate; full
registrar integration and other outstanding R.0 evidence remain
separate. **R.0 open; R.1 not started.**
