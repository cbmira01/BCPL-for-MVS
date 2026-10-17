# Historical BCPLMAIN assembler snapshots

These files are **not the active development source**. For current
development edit [`../bcplmain.asm`](../bcplmain.asm) instead.

- `bcplmain-pre-d6-production.asm`: the previously canonical, M3 production
  rebuild source retained to reproduce the accepted NATIVE_OBJ baseline.
  The snapshot remains only for historical reproduction; it is not
  mapped by the current manifest.
- `bcplmain-wip.asm`: original monolithic regression-era WIP source.
  Its staged fragments in `../bcplmain-wip/` are historical.
- `bcplmain-d3-candidate.asm` through `bcplmain-d5-candidate.asm`:
  older independently linked development candidates.
- `bcplmain-d7-candidate.asm`: independently accepted M2.1/D7 variant.
  Its stack-overflow RC=0012 is distinct from the D6 RC=0000 contract
  used by the later BCPLIO dynamic-stream M5.5 acceptance.

The source in `../bcplmain.asm` is the **exact former D6/BCPLM6
source**, the baseline for the accepted BCPLIO dynamic-stream milestone.
It has not been changed as part of this file-layout reorganization.
`NATIVE_ASM(BCPLMAIN)` maps to that canonical file; no versioned
source members remain in the manifest.

The historical files are kept for reproducibility, not automatically
populated as alternate production objects. A Git source choice is not
an MVS binary promotion.
