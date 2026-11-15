# 177 — co2-native-changeco

**Native Bootstrap regression suite:** `coroutines` (CO.5)

**Purpose:** CO.2 first switch and saved continuation.

Canonical Git-controlled BCPL source: `packaging/milestones/coroutines/candidates/co2-native-changeco/source.bcpl`. This numbered test
intentionally references the accepted candidate source rather than copying
or modifying it. The accepted CO.3 library remains separately compiled.

The ordered, complete logical records in `expected.txt` are mandatory; a
truncated, duplicate, additional, malformed or reordered record fails.
Every case requires real Cambridge compilation, IFOX, IEWL, GO and JES
evidence. In the candidate-only linkage profile, `BOOT_OBJ` is read-only.

Temporary G!289–305 slots remain test-local; no public ABI is established.
The known-live Approach A / independent-stack S1 scope applies.
