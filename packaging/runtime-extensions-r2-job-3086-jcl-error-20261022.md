# R.2 — JOB 3086 converter rejection (22 October 2026)

**March:** R.2 — Selective interoperability (ACTIVE)  
**Test revision:** `4134703b819356c0cc5556d8b71f07da631c7929`  
**Campaign directory:** `workarea/runtime-extensions-r2/acceptance/20261022T145750259107Z/` (operator-local)

## Observed results

- Four demoted Cambridge compiler-generated BCPL clients were compiled.
- The positive matrix **JOB 3085 PASS** was confirmed by the campaign
  verifier; the matrix was previously proved independently in JOB 3080.
- The negative batch was allocated **JOB 3086** but the submission
  helper returned **76**; JES reported
  `IEF452I R2NEG JOB NOT RUN - JCL ERROR`.
- The campaign correctly reported **INCOMPLETE / FAILED**. No
  negative-case GO, IFOX or IEWL outcomes are established by JOB 3086.

## Generator defect and correction

`bootstrap-toolchain/probes/r2-interoperability/make-negatives.py`
generated each of 21 IEWL steps with an invalid EXEC continuation:

```jcl
//L01      EXEC PGM=IEWL,REGION=256K,
//             PARM='NCAL,LIST,XREF,MAP',
//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR
```

The trailing comma following the completed `PARM` operand implies
further EXEC parameters, but the next JCL card begins the first DD
statement. Remove only that comma:

```jcl
//L01      EXEC PGM=IEWL,REGION=256K,
//             PARM='NCAL,LIST,XREF,MAP'
//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR
```

The host tests now explicitly check the `PARM`/`DD` boundary in
all 21 links. This invalid JCL is a concrete defect consistent with
the observed JOB rejection. The operator's truncated submit output
does not expose the detailed converter diagnostic, so **the precise
JES error position is not independently established**.

## Acceptance boundary

The correction is **not** evidence that the new deck has passed
MVS execution. R.2 remains **ACTIVE**; R.3 has not begun. Re-run the
single consolidated campaign, review actual negative diagnostics and
the positive/malformed linkage maps, and keep `BOOT_OBJ` and
`BOOT_DEVOBJ` unchanged.
