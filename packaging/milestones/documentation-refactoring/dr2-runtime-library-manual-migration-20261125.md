# DR.2 — Runtime and library manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** a8dd18e74db65971616b84cd9957629523f1c9bb  
**Status:** Initial substantive drafts; no authority transfer or DR.2 closure.

The eight explanation and nine reference chapters follow the approved outlines. Existing contract paths, history, source and oracles remain intact. This is an initial semantic mapping, not a complete replacement contract or exhaustive per-routine verification.

## Evidence alignment

Compared 23 selected tracked runtime/library blobs (eight production assembler modules, native coroutine source/header, historical BLIB/LIBHDR, and all MR10 library BCPL sources) with RC4 frozen program-source revision e910de51c19c09698be139e33084a90401511cc9: all match. Against CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a, fifteen blobs match exactly; eight assembler files differ. For those eight, comparison after excluding full-line assembler comments and blank lines and trimming trailing whitespace found identical remaining lines. This is a source comparison, not assembler output or binary identity proof. It does not establish that every tracked item was distributed or tested independently.

CO.5 and CO.6 accepted development execution and RC4 release acceptance are distinct. No new JES, IFOX, IEWL, ICINT19 or GO run; original operator-local raw receipts were not reopened.

## Migration ledger

| Original provision / authority | Destination | Reconciliation and remaining work |
| --- | --- | --- |
| Nomenclature and runtime interface conventions | Explanation 1–3, 5–8; reference 1–2, 7–8 | Preserve logical/physical distinction, separate Coroutine Support Library and distinct global/behavior/ABI contracts. No authority transfer |
| Runtime v1, sections 1–9 | Reference 1–5, 9 | Historical five-component candidate; map registration, storage, byte/memory, diagnostic/termination behavior. Current independent APTOVEC and dynamic streams supersede old implementation descriptions, not their historical evidence. Complete private ABI and exceptional path audit remains |
| D7 v2 candidate | Reference 2–4, 9 | Candidate-only scope; independent APTOVEC, allocated extent versus safe limit, D7 RC12 differs from current STKOVFL/FINIMPL and D6-compatible oracle RC0. Do not change source or expected files to reconcile text |
| Stack-check checkpoint and CO.1 option matrix | Reference 2–3, 9 | Historical STKCK body missing; current checked +60 and skip-only +20/+80 source; combined compile-only evidence not GO. Retain exact frame and candidate-specific limits |
| BCPLIO dynamic contract and JCL/QSAM responsibility contract | Explanation 4; reference 4 | Map global calls, normalization, stable handles, record shape, resource lifetime, returned failures, synthetic accounting, MVS/JES2 boundary. Dated DEVOBJ scope preserved; current production source observed. Detailed private linkage and all fault paths still need reconciliation |
| LIBHDR and historical BLIB; v1 observability | Explanation 3; reference 2, 5, 9 | Source signatures and formatting table; focused independent-object tests 069–081; preserve 075 original failure/correction; exact READN, all formatting boundaries, trailer exports and diagnostic dependencies pending |
| CO.5 production promotion/closure; CO.6 contract/closure | Explanation 5–6; reference 6–7, 9 | Map known-live root/two-worker, fixed 1024, private context, registration before reclamation, source return codes, paired behavior and historical failure. No arbitrary pointer safety or paired natural-return proof. Preserve full lifecycle/bridge evidence |
| MR10 library README, GLOBALS, coroutine/allocator source and demo | Explanation 6, 8; reference 7 | Retain separate ABI/slots, module selection, summary restrictions. Complete per-function signatures and edge cases still pending |
| Global Number Registry, extension R.0/R.5, T.1, Q.5 records | Explanation 7–8; reference 2, 8–9 | Registry owns allocation; later closure records establish implementation state; do not change registry's dated implementation notes here. G!150 DEBUGINT/FORMTREE unresolved; historical G94 duplicate retained. Detailed extension API in separate reference |
| Native library staging README and BSL design discussion | Explanation 8; reference 8 | Source candidates and inherited slot collision risk; no native library promotion; no proposed API or new user range allocated |
| RC4 guide, CO.5/CO.6 evidence | Both manuals | Preserve release/development boundaries, expected SKIP 083 and genuine MR10/IEWL failure records; no changes to frozen release |

## Explicit discrepancies and verification debt

- v1 internal G40 versus current independent BCPLAPT with APLIMIT initialized; v1/v2 fixed stream names versus current dynamic BCPLIO.
- D7 stack-overflow RC12 versus current source's RC0 normal finalization; finalizer failure can independently change FINISH status. Keep profile-specific oracles.
- Current source allocates a worker lifecycle descriptor via GETVEC(27), while the accepted private 24-word context is described in CO.5; do not turn either into a public size contract.
- Native G!150 diagnostic versus historical FORMTREE; native candidate G101–116 versus historical/compiler ownership; no renumbering authorized. Registry remains authoritative.
- Check exact current BLIB export inventory, each MR10 library signature, private assembler ABI, built-in versus dynamic stream corner cases and exceptional behavior before requesting normative transfer. Source-derived and accepted-test claims remain distinct.

DR.0 dependency-audit qualification remains applicable. No deletion, relocation, software or oracle change, allocation change, new release, authority transfer or march closure.
