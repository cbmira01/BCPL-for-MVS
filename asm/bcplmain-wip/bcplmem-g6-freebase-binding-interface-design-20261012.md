# BCPLMEM ↔ G6!48 list-head publication — minimal interface design

Date: 2026-10-12. **Design only; no assembler or PDS changes.** Basis: historical `bcplmac` VECAREA/VECLIST, surviving BLIB G59 VALIDPOINTER, current `asm/bcplmem.asm`, and source-mode independent-object regression 122 PASS (manual G6!48 publication, STACKEND shortcut isolated). This is a targeted compatibility interface, **not** a claim that later `comacro` FREEBASE has identical semantics.

## Decision

Add one **private assembler entry** `MEMBIND` to the independently linked `BCPLMEM` object. BCPLMAIN owns `MSVFREE` (G6!48, byte displacement +192 from R13). BCPLMEM owns `VECLIST` and all three-word descriptors. MEMBIND passes a **native byte address of the fullword publication slot**, **not** the slot's current contents, and BCPLMEM mirrors its current `VECLIST` into that slot on every relevant head transition.

No BCPL global index is assigned to MEMBIND. BLIB stays unchanged. BCPLMAIN does not traverse or alter descriptor chains.

## Exact proposed ABI

- Entry symbol: `MEMBIND` (additional BCPLMEM ENTRY alongside GETVEC/FREEVEC/MEMDRAIN).
- Call linkage: `BALR 14,<register containing MEMBIND address>` from BCPLMAIN's assembler path, before entering START. Uses ordinary R14 return, **not** BCPL G87 calling convention.
- Input: `R1` contains the *native byte address* of the writable fullword `MSVFREE`; R1=0 disables publication.
- Output: no return value (do not depend on R15/condition code). Other than R1 being input, preserve R0–R3, R4–R12 and R15, and R14 return linkage. Use BCPLMEM private R10 as assembler base only if saved/restored around call.
- Binding state: BCPLMEM private word `VECPUB` holds the slot's byte address. `VECLIST` remains authoritative. Never confuse address of slot with byte address of first descriptor.
- On `MEMBIND(nonzero)`: assign VECPUB; store *current* VECLIST head native byte address to `0(VECPUB)` (normally zero at startup). Require fullword-aligned accessible slot. No user-buffer pointer validation beyond this internal trusted caller.
- On `MEMBIND(0)`: clear VECPUB. Do not dereference a stale slot and do not alter VECLIST. Caller is responsible for clearing its own live slot if needed before unbinding.
- Singleton, non-reentrant, one bound runtime instance. Multiple BCPLMAIN instances or nested invocation are explicitly unsupported pending a separate lifecycle design. A zeroed binding cannot safely be interpreted as a request to free all vectors.

## Publication and lifecycle

1. BCPLMAIN establishes the 49-word savearea and G6=R13>>2, with MSVFREE initially zero. Prior to the first BCPL GETVEC, load R1 with `MSVFREE`'s **address** and call MEMBIND. This requires extending BCPLMAIN's explicit `EXTRN` to MEMBIND and referencing its relocated external address; assembler source and modular fragment must agree.
2. GETVEC failure paths: no list mutation, no publication. On success: fully initialize new descriptor (base, byte length, next byte pointer); update private VECLIST; write new head to bound MSVFREE. Only then return the BCPL word pointer. Register-preservation behavior of G87 remains unchanged.
3. FREEVEC(NULL/unknown): no publication. Non-head removal: update predecessor `VECNEXT` before FREEMAIN; head unchanged, so no head publication needed. Head removal: write private VECLIST successor; **publish new head before FREEMAIN**. This prevents BLIB from seeing a freed head on subsequent calls (non-reentrant code; no concurrency guarantee).
4. MEMDRAIN: detach each head and publish its successor **before** FREEMAIN; when complete publish zero. Preserve its current R14 and BCPL-register behavior.
5. On normal STOP/FINISH: BCPLMAIN calls MEMDRAIN while MSVFREE is addressable and binding live; then MEMBIND(0), then releases BCPLMAIN's other owned regions and returns to MVS. Early failure before binding need not unbind; paths after binding must drain/unbind. Ensure MEMDRAIN can be safely called on the zero-list case.
6. Subsequent executions in the *same loaded instance* must bind explicitly, not rely on stale VECPUB. If same object retains static state, startup must ensure zero list from prior clean shutdown; repeated-run acceptance is a distinct gate. Never store an address into a slot once its lifetime ends.

## Candidate implementation sketch (not committed as ASM)

```
BCPLMAIN:  R1 := address(MSVFREE)
           CALL MEMBIND
           ... BCPL program runs ...
           CALL MEMDRAIN
           R1 := 0
           CALL MEMBIND
           ... release own regions ...
BCPLMEM:   VECPUB := R1
           if VECPUB != 0: *(fullword*)VECPUB := VECLIST
           ... successful GETVEC/head FREEVEC/head MEMDRAIN ...
           if VECPUB != 0: *(fullword*)VECPUB := VECLIST
```

Publication is synchronous and only reflects valid constructed list states; no forwarding pointer, getters, polling, or changes to BLIB are needed.

## Acceptance strategy / risks

- Test a **noninstalled source-mode BCPLMAIN + external BCPLMEM object**. Adapt regression 122 to *remove all direct program writes to SAVEAREA!48*; keep a local save/restore of STACKEND solely to force BLIB through list traversal. Acceptance: after allocation G6!48 is nonzero; VALIDPOINTER recognizes first and second vectors; after freeing head it follows surviving head; after final free G6!48 is zero and VALIDPOINTER rejects freed pointer. Include non-head unlink, unknown FREEVEC and failed/zero allocation cases.
- Check public globals 87/88 unchanged, R0 remains zero, permanent R1=4096 and R2/R3 unchanged through BCPL calls, and descriptor byte-pointer units consistent.
- Run independent source-mode regression, source checker and full suite in **source mode where appropriate**. Only then separately schedule a controlled replacement of BCPLMAIN **and BCPLMEM** in the object PDS; a BCPLMAIN-only promotion would leave MEMBIND unresolved. Installation is non-atomic; back up previous members and use one install job with both assemblies gated before copying either member.
- On installed acceptance, run new focused installed-mode test plus ordinary regression suite and MEMDRAIN/leak tests, excluding instrumented case 083 as usual.
- The historical `VALIDPOINTER` has a broad `SAVEAREA<=N<STACKEND` shortcut and a permissive upper extent calculation. A PASS is about **legacy traversal compatibility**, not exact user-payload validity or memory-safety proof. The ABI also does not solve potential overlap of allocator GETMAIN address ranges with that shortcut.
- Register pressure and macro expansion may necessitate minor adjustments during implementation, but do not silently change ABI or bypass validation. In particular, preserve R1 on return from MEMBIND only if the calling convention requires it: R1 is input and documented preserved here.

## Explicit exclusions

No redesign of GETMAIN/FREEMAIN, no heap FREEBASE/NEXTFREE/LASTFREE manager, no loader changes, no BLIB changes, no global-vector service slot, no locks/reentrancy, no direct BCPL-program setter for G6!48, and no production installation during design.

## Design disposition

**Ready for a separate source-only implementation march.** The interface is intentionally minimal and fully testable. Production promotion requires a separate acceptance decision.
