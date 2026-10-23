# R.4 — JOB 3717: IEWL INCLUDE/WXTRN initial evidence

**Status: live MVS experiment PASSED, 23 October 2026.**
**Official baseline:** GitHub `main` commit `fe37f946c57086fc0152c2a5ae122949a0df7ea0`.
**System:** MVS 3.8J TK5 under Hercules, IFOX00 and IEWL.
**Source:** operator-supplied complete JES report for `R4WXLINK`, JOB 3717.
Raw printer evidence stays operator-local under ignored `workarea`.

Six IFOX assemblies, four IEWL links and four GO steps finished with
`RC=0000`, 14/14 steps. IFOX reported no flagged statements and highest
severity zero for the assembled sources. IEWL cross-reference tables show:

| Selection | IEWL/GO | Optional CSECTs | Length |
| --- | --- | --- | --- |
| 0 | L0/G0 RC=0000 | none | `X'60'` |
| A | LA/GA RC=0000 | `DMODESC`, `DMODISP` | `X'1C0'` |
| B | LB/GB RC=0000 | `R2BDSC`, `R2BDISP` | `X'1A0'` |
| A+B | LX/GX RC=0000 | all four | `X'2E8'` |

The assembler ESD dictionaries identify each descriptor and dispatcher as
separate CSECTs within **one combined package object**. Their RLD entries
relocate the dispatcher address at descriptor offset `X'34'`. IEWL reports
omitted weak references as `$UNRESOLVED(W)` and binds explicitly included
symbols to the selected CSECTs. Each GO returned zero after checking
weak-symbol presence/absence and BCEX version-1 descriptor fields.

**What JOB 3717 proves:** Known-symbol `WXTRN` selection reliably detects
explicitly included packages while omitted packages stay absent. It
requires a precompiled observer that *knows all candidate extension
symbol names*, so it does **not** establish arbitrary descriptor discovery
or remove the need for some registration-source-of-truth.

**Next candidate:** The documented `DXD`/`CXD` combination can accumulate
the storage length contributed by unique external dummy sections without
prior package symbol names. See [DXD/CXD probe](../bootstrap-toolchain/probes/iewl-optional-discovery/DXD-CXD.md).
Its result remains **unverified on MVS**. Since dummy storage is not
initialized descriptor text, success would establish package-independent
length measurement, not descriptor enumeration or automatic registration.

**No production Core Runtime, compiler, BCEX/BCRG ABI, or accepted object
library changes occurred in JOB 3717. R.4 remains open.**
