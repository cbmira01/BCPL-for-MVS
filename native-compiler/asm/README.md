# Native System/370 assembler runtime sources

This directory holds the **one maintained source per native runtime module**:

| Canonical Git file | CSECT / responsibility |
|---|---|
| [`bcplmain.asm`](bcplmain.asm) | BCPLMAIN bootstrap, termination and service dispatch |
| [`bcplio.asm`](bcplio.asm) | Independent BCPL character-stream / QSAM interface |
| [`bcplmem.asm`](bcplmem.asm) | Runtime memory services |
| [`bcplbyte.asm`](bcplbyte.asm) | Byte operations |
| [`bcplapt.asm`](bcplapt.asm) | Argument vectors and stack support |

**Current BCPLMAIN source:** `bcplmain.asm` contains the unchanged D6
candidate that was accepted with dynamic-stream M5.5 as DEVOBJ(BCPLM6).
Further BCPLMAIN development belongs in this file, not in another
`bcplmain-dN-candidate.asm` beside it. Keep other modules on their
canonical paths as well.

## Source naming is not object promotion

`config/dspal.yaml` deliberately maintains two MVS assembler member roles:

- `NATIVE_ASM(BCPLM6)` is populated from canonical
  `native-compiler/asm/bcplmain.asm`. The D6 candidate build
  `NATIVE_JCL` job `build-dev-bcplm6.jcl` installs only
  `NATIVE_DEVOBJ(BCPLM6)`.
- `NATIVE_ASM(BCPLMAIN)` remains populated from
  [`history/bcplmain-pre-d6-production.asm`](history/bcplmain-pre-d6-production.asm).
  The established `NATIVE_JCL(BLDBMAIN)` continues building the
  historical production `NATIVE_OBJ(BCPLMAIN)` from that source.
  **No production promotion is authorized by the naming change.**

The independently accepted M2.1 D7 variant is retained at
[`history/bcplmain-d7-candidate.asm`](history/bcplmain-d7-candidate.asm),
and the manifest still permits explicit staging of NATIVE_ASM(BCPLM7).
Its stack-overflow RC=0012 is **not** interchangeable with D6's
RC=0000 in the accepted dynamic-stream regression.

Earlier D3–D5, pre-D6, and WIP sources are retained in
[`history/`](history/). The WIP fragments remain in
[`bcplmain-wip/`](bcplmain-wip/) for historical reconstruction; they
are not the source of new BCPLMAIN development.

The obsolete standalone M1-era `*-probe.asm` experiments and matching
JCL decks were removed after the 00..145 regression and focused M4/M5
verification became the retained tests. Git history preserves the
older experiments. M4.2 and M5 verification under `native-compiler/probes/`
and `tools/checks/` remain available.

Run `python3 tools/checks/check-bcplmain-canonical.py` to check the
manifest/source relationship and IFOX card formatting without installing
or running any MVS program.

For the authoritative clean-room build and candidate reproduction see
[`packaging/clean-room-mvs-reconstruction.md`](../../packaging/clean-room-mvs-reconstruction.md).
