# Regression 121 — G6 extended save-area BLIB consumer probe

Tests canonical BCPLMAIN's G6 pointer and historical BLIB's real
`INPROGRAM` (G58) and `VALIDPOINTER` (G59) procedures. The test
asserts that historical byte-address list heads `SAVEAREA!29` (LOADLIST)
and `SAVEAREA!48` (FREEBASE) are initially zero, and that both
historical procedures reject the word address zero without traversing
either absent list. Output is exactly `G`.

This tests only the empty-list behavior. It does **not** validate
nonempty loader/vector region lists, allocator membership, or complete
historical USERSAVE fidelity. It links the historical BLIB object,
not replacement stubs.

## Current validation

Test 121 passed against DEVOBJ(BCPLM7) in Gate E and in the complete native regression panel. Use explicit candidate selection for reproduction:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7 \
tools/native/run-regression 121 --show-output
```

Historical source-only and production promotion suggestions in earlier versions of this note are superseded. Production HERC02.BCPL.OBJ remains unchanged.
