# Regression 122 — test-local FREEBASE vector-list traversal

**Experimental only.** Tests historical BLIB G59 `VALIDPOINTER` against
the independently compiled `BCPLMEM` G87/G88 three-word vector headers.

The BCPL program temporarily publishes a descriptor's native byte address
into `SAVEAREA!48`. This is test-local manual publication, **not** automatic
production synchronization. It then tests list traversal with two vectors,
freeing the list head, republishing the survivor, and finally clearing
the head after the last free. A pre-publication negative check explicitly
guards against `VALIDPOINTER` returning true only via its broad
stack/program extent rules.

Expected output: `V`; any discrepancy outputs `?`.
The test must run in source mode and must not modify the installed PDS.

```sh
git pull --ff-only
BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 \
  tools/run-native-regression 122 --show-output
```

Source-mode BLIB linkage uses the existing `object-blib.txt` fixture.
`BCPLMEM_OBJECT=1` is essential: it exercises the independent BCPLMEM
object, not the older BCPLMAIN inlined allocator. The wrapper selects
the object-mode stage2 path and supplies the external memory module.

This test assumes MVS GETMAIN supplies two distinct live vector addresses,
and that one is not accepted by VALIDPOINTER's broad first clause.
An environmental placement causing that overlap should be reported
as inconclusive rather than silently counted as proof.

The test cannot prove that a fully automatic published-head contract
works or that COMACRO's modernized heap FREEBASE has the same meaning.
No permanent BCPLMAIN/BCPLMEM/BLIB sources are modified.
