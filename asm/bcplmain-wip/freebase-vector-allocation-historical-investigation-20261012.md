# FREEBASE and vector-allocation metadata — historical investigation (2026-10-12)

Status: **read-only contract audit; no production code edits**. Baseline: accepted G6 empty-list backing, JOB 8551, installed regression 121 PASS and installed PDS acceptance 119/119.

## Sources inspected

- `richards-bcpltape/km10/bcplmac`, `USERSAVE` and `VECAREA` macro definitions.
- `richards-bcpltape/km10/comacro`, `USERSAVE`, `FREEAREA` and `VECAREA`.
- `richards-bcpltape/bcplib/bcpl/blib`, `VALIDPOINTER`.
- `asm/bcplmem.asm`, current independent production object allocator, G87/G88 and `MEMDRAIN`.
- `asm/bcplmain-wip/20-streams-and-services.asmfrag`, previous in-main allocator (historical reconstruction context, not current production owner).

## Direct historical evidence

**BCPLMAC variant:** `USERSAVE` contains `VECLIST DS F`, described as head of list of vectors allocated by GETVEC; `VECHEAD EQU VECLIST-VLINK` offsets list traversal from a link field. `VECAREA` defines `VECTOR DSECT`, `VECBASE DS F` (BCPL address), `VECLEN DS F` (obtained bytes), `VECNEXT DS F` (next vector), `VLINK EQU VECNEXT-VECTOR`. Descriptor byte offsets are 0, 4, and 8.

**COMACRO variant:** `USERSAVE` instead defines `FREEBASE DS F`, described as base of vector allocation, plus `NEXTFREE` and `LASTFREE` byte pointers in the heap. `FREEAREA` defines `BLOCK DSECT` with `BLKHDR DS F` and `USERBLK EQU *`; its one-word block-header scheme is not the same as the three-word `VECAREA`. COMACRO also still carries a `VECAREA` definition, which does not establish that its modernized allocator actively used that descriptor.

**BLIB:** `VALIDPOINTER(N) = (SAVEAREA<=N<STACKEND) | INPROGRAM(N) | VALOF ...` reads `P := (SAVEAREA!48)>>2`; for each P, `!P <= N < P+(P!1>>2)` is the extent test and `P := (P!2)>>2` traverses the next descriptor. The three fields have the same read sequence as the `VECAREA` descriptor; link values are byte addresses and BCPL pointer values use word units.

## Current reconstructed allocator

`asm/bcplmem.asm` is a separate object and singleton, not reentrant. `GETVEC(N)` reserves `4*(N+1)+12` bytes by MVS GETMAIN, stores `(base+12)>>2` at descriptor +0, allocation byte size at +4, and the old list-head native byte address at +8; it then writes the new descriptor native byte address to its own private `VECLIST`. `FREEVEC` traverses by matching the vector's BCPL pointer and unlinks/frees the block. `MEMDRAIN` frees all remaining blocks at termination. G6!48 is currently zero and is **not** linked to BCPLMEM VECLIST.

The **descriptor shape** matches the historical BCPLMAC `VECAREA` and the three-word traversal in BLIB. However the **publication/ownership** does not match: BCPLMEM owns a private mutable list-head word, while BLIB looks up the actual pointer *value* at G6!48. Writing G6!48 once at startup cannot track later allocations and frees.

## Compatibility and risks

| Area | Evidence | Current status |
|---|---|---|
| G6 word-pointer units | BCPLMAIN stores R13 >> 2 | Verified in regression 121 for empty lists |
| BLIB descriptor offsets | `P!0`, `P!1`, `P!2` | Structurally matches BCPLMEM's three-word header |
| Next-link pointer units | byte pointer shifted right two | Matches BCPLMEM |
| Dynamic list head | BLIB reads `SAVEAREA!48` repeatedly | **Not connected** to BCPLMEM private VECLIST |
| COMACRO FREEBASE meaning | heap-region base, not proven linked-list head | **Version mismatch/uncertain provenance** |
| Invalid pointer behavior | VALIDPOINTER short-circuits other regions first; then list traversal | Only zero-pointer negative case tested |
| Released vectors | FREEVEC unlinks before FREEMAIN | No published head; no currently runnable G6 positive-path verification |

Subtlety: the BLIB condition compares `!P` (payload BCPL address) with `P+(P!1>>2)` (descriptor-based word end). This is a **broader bound** than payload start plus exactly N+1 words, and includes possible GETMAIN padding/metadata range. Document this behavior as historical source fact rather than claiming strict payload-bound validity.

## Recommended next bounded experiment

1. Preserve production baseline, no loader/heap rewrite.
2. Add a noninstalled, diagnostic-only probe that calls the *real* historical BLIB `VALIDPOINTER` before/after `GETVEC`, checks an interior pointer and verifies `FREEVEC` removes validity. To exercise the actual three-word traversal, a test-local mechanism must make G6!48 reflect the live BCPLMEM list head; options include an explicit machine-service interface to set/publish the value on every list mutation. **Do not simply write the value once at startup.**
3. Confirm semantics of the lower/upper bound tests and negative probes. For a controlled source-only experiment, inspect the descriptor directly under BCPL word-address conversion rather than inventing a production API.
4. Only after this evidence, decide whether to expose G6!48 from BCPLMEM through an explicit minimal register/pointer interface, and whether to limit it to a legacy BCPLMAC-compatibility mode. Keep GETVEC/FREEVEC object ownership in BCPLMEM.
5. In particular, do not reinterpret COMACRO's `FREEBASE` heap base as a VECLIST pointer; this is not source-proven.

## Unresolved source provenance

The inspected macro files cannot yet prove which historical runtime release generated the surviving BLIB build, or that the COMACRO `FREEBASE` heap-allocation scheme should be used with this BLIB's three-word linked-list traversal. More compiler/runtime source archaeology is needed to make that claim.

**No PDS member or assembler was modified in this investigation.**
